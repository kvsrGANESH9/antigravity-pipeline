import os
import config
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes_in_video(video_path, threshold=None, min_scene_len=15):
    """
    Runs content-based scene detection on the video.
    
    :param video_path: Path to the video file.
    :param threshold: Sensitivity threshold for ContentDetector (default is read from config or 27.0).
    :param min_scene_len: Minimum scene duration in frames.
    :return: A list of dicts representing each detected scene.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")
        
    if threshold is None:
        threshold = getattr(config, "SCENE_DETECTOR_THRESHOLD", 27.0)
        
    print(f"Running scene detection on '{video_path}' (threshold={threshold})...")
    
    try:
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))
        
        # Run the scene detection
        frame_skip = getattr(config, "SCENE_DETECTION_FRAME_SKIP", 0)
        scene_manager.detect_scenes(video, show_progress=False, frame_skip=frame_skip)
        raw_scene_list = scene_manager.get_scene_list()
    except Exception as e:
        print(f"Error during scene detection: {e}")
        return []
    
    scenes = []
    for i, scene in enumerate(raw_scene_list):
        start_time, end_time = scene
        scenes.append({
            'scene_num': i + 1,
            'start_sec': start_time.get_seconds(),
            'end_sec': end_time.get_seconds(),
            'start_frame': start_time.frame_num,
            'end_frame': end_time.frame_num,
            'start_timecode': start_time.get_timecode(),
            'end_timecode': end_time.get_timecode()
        })
        
    print(f"Detected {len(scenes)} scenes in video.")
    return scenes
