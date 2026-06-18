# Antigravity Slide-to-Video Pipeline

A sophisticated automated video processing pipeline that synchronizes PDF slides with video content, removes intros, and generates cleaned output videos with proper slide-to-video alignment.

## Features

- ✅ **Automated PDF to Slides Conversion** - Extracts slides from PDF files
- ✅ **Scene Detection** - Intelligently detects scene changes in videos
- ✅ **Visual Alignment** - Matches video scenes to corresponding slides
- ✅ **Audio-Video Synchronization** - Maintains proper audio/video synchronization
- ✅ **Intro Removal** - Removes intro sequences automatically
- ✅ **Batch Processing** - Process multiple videos in a single run
- ✅ **Comprehensive Reporting** - Detailed processing reports with timing
- ✅ **Resume Capability** - Skip already processed files
- ✅ **GUI Interface** - User-friendly folder selection interface

## System Requirements

- **OS**: Windows 7 or later
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 50GB+ for typical processing
- **Python**: 3.8+ (if running from source)

## Installation & Setup

### Option 1: Using Pre-Built EXE (Recommended)

1. Download the latest release from [GitHub Releases](https://github.com/kvsrGANESH9/antigravity-pipeline/releases)
2. Extract the ZIP file to your desired location
3. Double-click `pipeline.exe` to launch the application
4. No additional installation required!

### Option 2: Running from Source

**Prerequisites:**
- Python 3.8 or higher
- FFmpeg binaries (included in `/bin` folder)

**Setup:**
```bash
# Clone the repository
git clone https://github.com/kvsrGANESH9/antigravity-pipeline.git
cd antigravity-pipeline

# Install Python dependencies
pip install -r requirements.txt

# Run the GUI launcher
python gui_launcher.py

# Or run the CLI version
python pipeline.py --workspace /path/to/workspace
```

## Usage

### GUI Mode (Recommended)

1. **Launch** `pipeline.exe` (Windows) or `python gui_launcher.py`
2. **Select PDF Source Folder** - Contains your PDF files (one PDF per video)
3. **Select Video Source Folder** - Contains your MP4 video files
4. **Configure Output Folders** (optional):
   - Slides Output: Where extracted slide images are stored
   - Cleaned Video Output: Where final processed videos are saved
   - Reports Output: Where processing reports are saved
5. **Click "Start Processing"** and monitor the progress in the log
6. **View Reports** in the Reports folder when complete

### Command-Line Mode

```bash
# Basic usage with default directories
python pipeline.py

# Custom directories
python pipeline.py \
  --workspace C:/MyProject \
  --pdf-dir C:/PDFs \
  --video-dir C:/Videos \
  --output-dir C:/Output

# Force reprocess all files (skip resume)
python pipeline.py --force

# Don't clean temporary files after processing
python pipeline.py --no-clean-temp
```

## Input File Structure

The pipeline expects files to be organized as follows:

```
Project Folder/
├── SOURCE/                    (PDF source folder)
│   ├── video_001.pdf
│   ├── video_002.pdf
│   └── ...
├── VIDEOS/                    (MP4 video source folder)
│   ├── video_001.mp4
│   ├── video_002.mp4
│   └── ...
├── SLIDES/                    (Auto-created: extracted slide images)
├── OUTPUT/                    (Auto-created: cleaned videos)
└── REPORTS/                   (Auto-created: processing reports)
```

**Important:** 
- PDF and video filenames must match (except extension)
- Example: `lecture_01.pdf` should have corresponding `lecture_01.mp4`

## Output Files

After processing, you'll find:

1. **Cleaned Videos** in `OUTPUT/` folder
   - Naming: `{original_name}_Cleaned.mp4`
   - Format: H.264 video, AAC audio, 1920x1080

2. **Processing Report** in `REPORTS/` folder
   - `processing_report.csv` - Summary statistics for all videos
   - `processing_log.txt` - Detailed processing log

3. **Extracted Slides** in `SLIDES/` folder
   - Named slide images for each PDF
   - Used internally for video alignment

## Processing Report Format

The `processing_report.csv` includes:

| Column | Description |
|--------|-------------|
| Course Name | Input PDF/Video filename |
| Slide Count | Number of slides extracted from PDF |
| Scene Count | Number of scene changes detected in video |
| Warning Reason | Any warnings during processing |
| Extra Scenes | Number of scenes beyond available slides |
| Unmatched Slides | Number of slides not matched to scenes |
| Output Video | Path to generated cleaned video |
| Status | SUCCESS, WARNING, or FAILED |
| Processing Time | Time taken to process (in seconds) |

## Configuration

Edit `config.py` to customize behavior:

```python
# Intro cut-off time (seconds)
HARDCODED_INTRO_CUT = 5.0

# Scene detection sensitivity (lower = more sensitive)
SCENE_DETECTOR_THRESHOLD = 3.0

# Slide-to-scene matching threshold (0-100)
SIMILARITY_THRESHOLD = 55.0

# Skip already processed files
SKIP_ALREADY_PROCESSED = True

# Automatically clean temporary files
CLEAN_TEMP_AFTER_SUCCESS = True
```

## Building the EXE from Source

To build a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
.\build.bat
```

This creates a `pipeline.exe` that includes all dependencies and FFmpeg binaries.

## Troubleshooting

### Issue: "Missing PDF source slide file"
**Solution:** Ensure PDF files are in the SOURCE folder with matching video filenames

### Issue: "Low similarity detected"
**Solution:** Adjust `SIMILARITY_THRESHOLD` in `config.py` (lower value = more lenient)

### Issue: "Scene detection unstable"
**Solution:** Adjust `SCENE_DETECTOR_THRESHOLD` in `config.py` (lower = more sensitive)

### Issue: Processing is slow
**Solution:** 
- Reduce video resolution if possible
- Increase `FRAME_SAMPLE_POSITIONS` for faster (less accurate) detection
- Run on multiple machines for different videos

### Issue: "FFMPEG not found"
**Solution:** Ensure `bin/` folder contains `ffmpeg.exe` and `ffprobe.exe`

## Performance Tips

1. **Batch Processing**: Process multiple videos simultaneously on different machines
2. **Skip Resume**: Use `--force` flag only when necessary
3. **Parallel Execution**: Run multiple instances on different video sets
4. **Hardware**: Use SSD storage for faster I/O
5. **Network**: Keep PDF/Video folders on local drives, not network shares

## Advanced Usage - Multi-System Deployment

For processing large video collections across multiple machines:

1. **Prepare shared storage** with PDF and video folders
2. **Install pipeline** on each system
3. **Divide work**: Assign video ranges to each machine
4. **Run independently**: Each machine processes its assigned videos
5. **Merge results**: Copy output folders to central location

## Supported Formats

- **Input Videos**: MP4 (H.264/AAC), MOV, AVI
- **Input PDFs**: Standard PDF files
- **Output Videos**: MP4 (H.264/AAC)

## Credits

Developed by Ganesh Kumar with support from Cyvi Technologies.

## License

Proprietary - All rights reserved

## Support

For issues, questions, or feature requests:
- GitHub: [GitHub Issues](https://github.com/kvsrGANESH9/antigravity-pipeline/issues)

---

**Version**: 2.0.0 | **Last Updated**: June 2026
