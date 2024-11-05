import cv2
import numpy as np

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

def adjust_hls_values(hls):
    h, s, l = cv2.split(hls)
    is_dominant_color = (s > 100)  # Placeholder logic; replace with actual logic
    h = np.where(is_dominant_color, h * 0.7, h)
    s = np.where(is_dominant_color, s * 0.9, s)
    l = np.where(is_dominant_color, l * 1.25, l)

    h = np.clip(h, 0, 179).astype(np.uint8)
    s = np.clip(s, 0, 255).astype(np.uint8)
    l = np.clip(l, 0, 255).astype(np.uint8)
    adjusted_hls = cv2.merge([h, s, l])
    return adjusted_hls

def adjust_lms_values(lms, severity):
    l, m, s = cv2.split(lms)
    m = m * (1 - severity) + l * severity
    adjusted_lms = cv2.merge([l, m, s])
    return adjusted_lms

def apply_protanopia_filter(frame, severity):
    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Apply HLS adjustments
    frame_hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    adjusted_hls = adjust_hls_values(frame_hls)
    adjusted_bgr_hls = cv2.cvtColor(adjusted_hls, cv2.COLOR_HLS2BGR)

    # Convert the original frame to LMS
    lms = rgb_to_lms(frame_rgb.astype(np.float32) / 255.0)

    # Apply LMS adjustments for Protanopia simulation
    adjusted_lms = adjust_lms_values(lms, severity)

    # Convert LMS back to RGB
    adjusted_rgb = lms_to_rgb(adjusted_lms)
    adjusted_rgb = np.clip(adjusted_rgb * 255.0, 0, 255).astype(np.uint8)

    # Convert LMS-adjusted frame to BGR for blending
    adjusted_bgr_lms = cv2.cvtColor(adjusted_rgb, cv2.COLOR_RGB2BGR)

    # Blend HLS and LMS adjustments (HLS 100%, LMS 20%)
    combined_adjusted = cv2.addWeighted(adjusted_bgr_hls, 1, adjusted_bgr_lms, 0.2, 0)

    return combined_adjusted
