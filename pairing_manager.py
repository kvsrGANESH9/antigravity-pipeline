import os
import glob
import cv2
import config

def _load_slide_previews(slide_files, size=(256, 256)):
    previews = []
    for idx, slide_path in enumerate(slide_files):
        img = cv2.imread(slide_path)
        if img is None:
            continue
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        previews.append((idx, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
    return previews

def _best_slide_for_scene(cap, scene, slide_previews, allowed_indices=None, size=(256, 256)):
    midpoint = scene['start_sec'] + ((scene['end_sec'] - scene['start_sec']) / 2.0)
    cap.set(cv2.CAP_PROP_POS_MSEC, midpoint * 1000)
    ok, frame = cap.read()
    if not ok:
        return None, 0.0

    frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    best_idx = None
    best_score = -1.0
    allowed = set(allowed_indices) if allowed_indices is not None else None
    for slide_idx, slide_gray in slide_previews:
        if allowed is not None and slide_idx not in allowed:
            continue
        score = cv2.matchTemplate(frame_gray, slide_gray, cv2.TM_CCOEFF_NORMED)[0][0] * 100.0
        if score > best_score:
            best_score = score
            best_idx = slide_idx

    return best_idx, best_score

def _prepare_visual_ffconcat_data(scenes, slide_files, video_path):
    if not video_path or not os.path.exists(video_path):
        return None

    slide_previews = _load_slide_previews(slide_files)
    if not slide_previews:
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    durations_by_slide = [0.0] * len(slide_files)
    matched_scene_count = 0
    threshold = getattr(config, "SIMILARITY_THRESHOLD", 55.0)
    current_slide_idx = 0
    max_forward_scan = max(1, getattr(config, "VISUAL_ALIGNMENT_MAX_FORWARD_SCAN", 3))
    allow_backtrack = getattr(config, "VISUAL_ALIGNMENT_ALLOW_BACKTRACK", False)

    try:
        for scene in scenes:
            if allow_backtrack:
                allowed_indices = None
            else:
                scan_end = min(len(slide_files), current_slide_idx + max_forward_scan + 1)
                allowed_indices = range(current_slide_idx, scan_end)

            slide_idx, score = _best_slide_for_scene(cap, scene, slide_previews, allowed_indices=allowed_indices)
            if slide_idx is None or score < threshold:
                continue
            durations_by_slide[slide_idx] += scene['end_sec'] - scene['start_sec']
            matched_scene_count += 1
            if slide_idx > current_slide_idx:
                current_slide_idx = slide_idx
    finally:
        cap.release()

    if matched_scene_count == 0:
        return None

    slide_sequence_data = []
    unmatched_slides = 0
    fallback_duration = getattr(config, "FALLBACK_SLIDE_DURATION", 10.0)

    for idx, slide_path in enumerate(slide_files):
        duration = durations_by_slide[idx]
        if duration <= 0:
            unmatched_slides += 1
            duration = fallback_duration
        slide_sequence_data.append({
            'path': slide_path,
            'duration': duration
        })

    extra_scenes = max(0, matched_scene_count - len(slide_files))
    if unmatched_slides == 0:
        status = "SUCCESS"
        warning_reason = "NONE"
    elif getattr(config, "STRICT_MODE", False):
        status = "FAILED"
        warning_reason = "VISUAL_ALIGNMENT_UNMATCHED_SLIDES"
    else:
        status = "WARNING"
        warning_reason = "VISUAL_ALIGNMENT_UNMATCHED_SLIDES"
    return slide_sequence_data, status, warning_reason, extra_scenes, unmatched_slides

def prepare_ffconcat_data(scenes, slide_dir, trimmed_audio_duration, video_path=None):
    """
    Pairs detected educational scenes with slide JPEGs using fallback logic.
    Calculates the duration for each slide.
    
    :param scenes: Complete list of detected scenes in the trimmed video.
    :param slide_dir: Directory containing slide JPEGs.
    :param trimmed_audio_duration: Duration of the trimmed audio.
    :return: (slide_sequence_data, status, warning_reason, extra_scenes, unmatched_slides)
    """
    slide_files = sorted(glob.glob(os.path.join(slide_dir, "slide_*.jpg")))
    slide_count = len(slide_files)
    scene_count = len(scenes)
    
    status = "SUCCESS"
    warning_reason = "NONE"
    extra_scenes = 0
    unmatched_slides = 0
    
    slide_sequence_data = []
    
    if slide_count == 0:
        return [], "FAILED", "MISSING_SLIDES", 0, 0

    if scenes and getattr(config, "VISUAL_ALIGNMENT_ENABLED", True):
        visual_result = _prepare_visual_ffconcat_data(scenes, slide_files, video_path)
        if visual_result is not None:
            return visual_result
        
    # FALLBACK MODE: Scene Detection Failed
    if scene_count == 0:
        status = "WARNING"
        warning_reason = "SCENE_DETECTION_FAILED"
        
        if trimmed_audio_duration and trimmed_audio_duration > 0:
            duration_per_slide = trimmed_audio_duration / slide_count
        else:
            duration_per_slide = config.FALLBACK_SLIDE_DURATION
            
        for slide_path in slide_files:
            slide_sequence_data.append({
                'path': slide_path,
                'duration': duration_per_slide
            })
            
        return slide_sequence_data, status, warning_reason, extra_scenes, unmatched_slides

    # Normal mapping
    limit = min(scene_count, slide_count)
    
    for i in range(limit):
        scene = scenes[i]
        slide_path = slide_files[i]
        duration = scene['end_sec'] - scene['start_sec']
        
        slide_sequence_data.append({
            'path': slide_path,
            'duration': duration
        })

    # Case 1: Scene Count > Slide Count
    if scene_count > slide_count:
        extra_scenes = scene_count - slide_count
        if getattr(config, "STRICT_MODE", False):
            status = "FAILED"
            warning_reason = "SCENE_COUNT_MISMATCH"
        else:
            status = "WARNING"
            warning_reason = "SCENE_COUNT_HIGHER"
        
        # Calculate sum of remaining scene durations
        extra_duration = 0.0
        for i in range(slide_count, scene_count):
            extra_duration += (scenes[i]['end_sec'] - scenes[i]['start_sec'])
            
        # Add the extra duration to the last mapped slide
        if slide_sequence_data:
            slide_sequence_data[-1]['duration'] += extra_duration

    # Case 2: Slide Count > Scene Count
    elif slide_count > scene_count:
        unmatched_slides = slide_count - scene_count
        if getattr(config, "STRICT_MODE", False):
            status = "FAILED"
            warning_reason = "SCENE_COUNT_MISMATCH"
        else:
            status = "WARNING"
            warning_reason = "SLIDE_COUNT_HIGHER"
        
        # Duration of the final detected scene
        final_scene_duration = scenes[-1]['end_sec'] - scenes[-1]['start_sec'] if scene_count > 0 else config.FALLBACK_SLIDE_DURATION
        
        # Append remaining slides with the final scene duration
        for i in range(scene_count, slide_count):
            slide_sequence_data.append({
                'path': slide_files[i],
                'duration': final_scene_duration
            })

    return slide_sequence_data, status, warning_reason, extra_scenes, unmatched_slides

def pair_and_verify(scenes, slide_dir, video_path, temp_frames_dir, course_name, strict_mode=None):
    if strict_mode is None:
        strict_mode = getattr(config, "STRICT_MODE", False)
        
    slide_files = sorted(glob.glob(os.path.join(slide_dir, "slide_*.jpg")))
    slide_count = len(slide_files)
    scene_count = len(scenes)
    
    if slide_count == 0:
        return False, "MISSING_SLIDES", [], "No slides found in directory."
        
    if strict_mode and scene_count != slide_count:
        return False, "SCENE_COUNT_MISMATCH", [], f"Scene count mismatch: Detected educational scenes = {scene_count}, slide JPEGs = {slide_count} (STRICT_MODE=True)."
        
    scores = [100.0] * min(scene_count, slide_count)
    return True, "SUCCESS", scores, ""
