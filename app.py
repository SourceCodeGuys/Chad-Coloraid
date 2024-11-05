from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, url_for, send_file
from flask_cors import CORS
import cv2
import numpy as np
from filters import apply_deuteranopia_filter, apply_protanopia_filter
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import pyrebase
from firebase_admin import credentials, firestore, initialize_app
from functools import wraps
from datetime import datetime
import pytz

# Initialize the Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Load environment variables
load_dotenv()

# Firebase configuration from environment variables
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

# Initialize Pyrebase for client-side authentication
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize Firebase Admin SDK for Firestore
cred = credentials.Certificate('firebase_admin_key.json')  # Path to your Firebase Admin SDK JSON file
initialize_app(cred)
db = firestore.client()

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session['user'] = user
        user_data = db.collection('users').document(user['localId']).get()
        if user_data.exists:
            session['username'] = user_data.to_dict().get('username', 'User')
            return redirect(url_for('profile'))
    except Exception:
        return render_template('index.html', message="Invalid credentials. Please try again.")

@app.route('/register', methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user['localId']
        db.collection('users').document(user_id).set({
            'firstname': firstname,
            'lastname': lastname,
            'username': username,
            'email': email
        })
        return redirect(url_for('index'))
    except Exception:
        return render_template('index.html', message="Registration failed. Try again.")

@app.route('/profile')
@login_required
def profile():
    user_id = session['user']['localId']
    test_results = db.collection('test_results').where('user_id', '==', user_id).stream()
    has_results = any(True for _ in test_results)
    return render_template('profile.html', username=session.get('username'), has_results=has_results)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session['user']['localId']
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        try:
            db.collection('users').document(user_id).update({
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'email': email
            })
            return redirect(url_for('settings'))
        except Exception:
            return redirect(url_for('settings'))
    user_data = db.collection('users').document(user_id).get().to_dict()
    return render_template('settings.html', user_data=user_data)
# New route for the About page
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test')
@login_required
def test():
    return render_template('test.html')

@app.route('/result')
@login_required
def result():
    return render_template('result.html')

@app.route('/testresults')
@login_required
def test_results():
    user_id = session['user']['localId']
    results_ref = db.collection('test_results').where('user_id', '==', user_id).get()
    results = []

    # Define the timezone for GMT+8
    gmt_plus_8 = pytz.timezone('Asia/Singapore')
    
    for doc in results_ref:
        result = doc.to_dict()
        # Format the timestamp to GMT+8 if it exists
        if 'timestamp' in result and result['timestamp']:
            # Convert the timestamp to UTC and then to GMT+8
            utc_time = result['timestamp'].replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(gmt_plus_8)
            result['timestamp'] = local_time.strftime("%Y-%m-%d %I:%M:%S %p (GMT+8)")
        results.append(result)

    return render_template('test_results.html', results=results)



@app.route('/save-results', methods=['POST'])
@login_required
def save_results():
    user_id = session['user']['localId']
    data = request.get_json()
    try:
        db.collection('test_results').add({
            'user_id': user_id,
            'total_score': data.get('total_score'),
            'classification': data.get('classification'),
            'classification_scores': data.get('classification_scores'),
            'timestamp': datetime.utcnow()  # Save the current UTC timestamp
        })
        return jsonify({"success": True, "message": "Results saved successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get-results', methods=['GET'])
@login_required
def get_results():
    user_id = session['user']['localId']
    try:
        results = db.collection('test_results').where('user_id', '==', user_id).get()
        result_list = [doc.to_dict() for doc in results]
        return jsonify({"success": True, "results": result_list}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get-latest-results', methods=['GET'])
def get_latest_results():
    user_id = session.get('user', {}).get('localId')
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 403

    try:
        # Fetch the latest test result for the user
        results_ref = db.collection('test_results').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
        if not results_ref:
            return jsonify({"success": False, "message": "No results found"}), 404
        
        latest_result = results_ref[0].to_dict()
        # Convert timestamp to desired format if needed
        if 'timestamp' in latest_result:
            gmt_plus_8 = pytz.timezone('Asia/Singapore')
            latest_result['timestamp'] = latest_result['timestamp'].astimezone(gmt_plus_8).strftime("%Y-%m-%d %I:%M:%S %p (GMT+8)")
        
        return jsonify({"success": True, "result": latest_result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route('/camera')
@login_required
def camera():
    user_id = session['user']['localId']
    results = db.collection('test_results').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
    if results:
        result = results[0].to_dict()
        classification = result['classification'].lower()
        total_score = result['total_score']

        # Initialize default values
        session['severity'] = 0.0
        session['filter_type'] = 'none'

        # Determine severity based on classification and total_score
        if classification == 'deutan':
            if 71 <= total_score <= 120:
                session['severity'] = 0.3
            elif 121 <= total_score <= 200:
                session['severity'] = 0.6
            elif total_score > 200:
                session['severity'] = 1.0
            session['filter_type'] = 'deuteranopia'

        elif classification == 'protan':
            if 71 <= total_score <= 120:
                session['severity'] = 0.3
            elif 121 <= total_score <= 200:
                session['severity'] = 0.6
            elif total_score > 200:
                session['severity'] = 1.0
            session['filter_type'] = 'protanopia'

        return render_template('Camera.html', filter_type=session['filter_type'], severity=session['severity'])
    else:
        return "No test results available.", 404


@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'frame' not in request.files:
        return jsonify({'error': 'No frame uploaded'}), 400

    frame_file = request.files['frame']
    np_frame = np.frombuffer(frame_file.read(), np.uint8)
    frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

    # Retrieve settings from session
    filter_type = session.get('filter_type')
    severity = session.get('severity', 0.5)

    # Apply the appropriate filter
    if filter_type == 'deuteranopia':
        frame = apply_deuteranopia_filter(frame, severity)
    elif filter_type == 'protanopia':
        frame = apply_protanopia_filter(frame, severity)

    # Encode the frame to JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    return send_file(BytesIO(buffer), mimetype='image/jpeg')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
