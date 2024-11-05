// Initialize Firebase
fetch('/firebase-config')
    .then(response => response.json())
    .then(config => {
        firebase.initializeApp(config);
        console.log("Firebase initialized with config:", config);
    })
    .catch(error => console.error("Error loading Firebase config:", error));