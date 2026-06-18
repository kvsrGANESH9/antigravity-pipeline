import cv2
import numpy as np
import config

def scale_and_fit(image_input, target_width=None, target_height=None):
    """
    Resizes an image to fit inside target_width x target_height while preserving aspect ratio.
    Pads the remaining area with black (letterboxing or pillarboxing).
    
    Defaults to configuration values from config.py if targets are not specified.
    
    :param image_input: Either a file path (str) or a pre-loaded numpy image array.
    :param target_width: Target canvas width (must be even).
    :param target_height: Target canvas height (must be even).
    :return: A resized and padded image of size (target_height, target_width, 3).
    """
    if target_width is None:
        target_width = config.TARGET_VIDEO_WIDTH
    if target_height is None:
        target_height = config.TARGET_VIDEO_HEIGHT

    # Enforce even dimensions for FFmpeg compatibility
    if target_width % 2 != 0:
        target_width += 1
    if target_height % 2 != 0:
        target_height += 1

    # Load image if input is a file path
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image from path: {image_input}")
    else:
        img = image_input

    h, w = img.shape[:2]
    
    # Calculate scale factor
    scale = min(target_width / w, target_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Ensure new dimensions are at least 1
    new_w = max(1, new_w)
    new_h = max(1, new_h)

    # Resize image
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create black canvas
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)

    # Calculate padding offsets to center the image
    x_offset = (target_width - new_w) // 2
    y_offset = (target_height - new_h) // 2

    # Paste resized image onto canvas
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    return canvas
