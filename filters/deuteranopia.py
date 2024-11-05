import cv2
import numpy as np

def adjust_lab_values(l, a, b, severity):
    a = np.where(a > 128, np.minimum(a + severity * (a - 128), 255), 
                 np.maximum(a - severity * (128 - a), 0)).astype(np.uint8)
    b = np.where(a > 128, b + severity * (a - 128) // 2, 
                 b - severity * (128 - a) // 2).astype(np.uint8)
    return l, a, b

def correct_color_lab(source, severity):
    lab = cv2.cvtColor(source, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l, a, b = adjust_lab_values(l, a, b, severity)
    corrected_lab = cv2.merge([l, a, b])
    corrected_rgb = cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2RGB)
    return corrected_rgb

def rgb_to_lms(rgb):
    transformation_matrix = np.array([[0.31399022, 0.63951294, 0.04649755],
                                      [0.15537241, 0.75789446, 0.08670142],
                                      [0.01775239, 0.10944209, 0.87256922]])
    return np.dot(rgb, transformation_matrix.T)

def lms_to_rgb(lms):
    inverse_matrix = np.array([[5.47221206, -4.6419601, 0.16963708],
                               [-1.1252419, 2.29317094, -0.1678952],
                               [0.02980165, -0.19318073, 1.16364789]])
    return np.dot(lms, inverse_matrix.T)

def adjust_lms_values(lms, severity):
    l, m, s = cv2.split(lms)
    m = m * (1 - severity) + l * severity
    adjusted_lms = cv2.merge([l, m, s])
    return adjusted_lms

def correct_color_lms(source, severity):
    lms = rgb_to_lms(source.astype(np.float32) / 255.0)
    adjusted_lms = adjust_lms_values(lms, severity)
    corrected_rgb = lms_to_rgb(adjusted_lms)
    corrected_rgb = np.clip(corrected_rgb * 255.0, 0, 255).astype(np.uint8)
    return corrected_rgb

def apply_deuteranopia_filter(frame, severity):
    # Convert to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Apply LAB correction
    corrected_lab = correct_color_lab(frame_rgb, severity)

    # Apply LMS correction on the LAB-corrected frame
    corrected_lms = correct_color_lms(corrected_lab, severity)

    # Blend LAB and LMS corrected frames (100% and 50%)
    combined_corrected = cv2.addWeighted(corrected_lab, 1, corrected_lms, 0.5, 0)

    # Convert back to BGR for OpenCV display
    corrected_frame_bgr = cv2.cvtColor(combined_corrected, cv2.COLOR_RGB2BGR)
    return corrected_frame_bgr
