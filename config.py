import os
import sys

"""
Application configuration for the Antigravity slide-to-video pipeline.

When the project is packaged with PyInstaller, the FFmpeg binaries are bundled
and extracted at runtime under sys._MEIPASS.
"""

# Centralized Configuration Settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
if getattr(sys, "frozen", False):
    BIN_DIR = os.path.join(sys._MEIPASS, "bin")

STRICT_MODE = True
PIPELINE_VERSION = "visual-align-v2"
HARDCODED_INTRO_CUT = 5.0
FALLBACK_SLIDE_DURATION = 10.0

TARGET_VIDEO_WIDTH = 1920
TARGET_VIDEO_HEIGHT = 1080

FRAME_SAMPLES_PER_SCENE = 3
FRAME_SAMPLE_POSITIONS = [0.25, 0.50, 0.75]
SIMILARITY_THRESHOLD = 55.0
DURATION_TOLERANCE_SECONDS = 1.0
VISUAL_ALIGNMENT_ENABLED = True
VISUAL_ALIGNMENT_MAX_FORWARD_SCAN = 3
VISUAL_ALIGNMENT_ALLOW_BACKTRACK = False

REUSE_EXISTING_SLIDES = True
SKIP_ALREADY_PROCESSED = True
FORCE_REPROCESS = False
CLEAN_TEMP_AFTER_SUCCESS = True

# FFMPEG and FFPROBE Paths
FFMPEG_PATH = os.path.join(BIN_DIR, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BIN_DIR, "ffprobe.exe")

# Optimizations
SCENE_DETECTOR_THRESHOLD = 3.0
SCENE_DETECTION_FRAME_SKIP = 4
