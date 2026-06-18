# Deployment Guide

## GitHub Repository Setup

### Initial Setup

1. **Create new repository** on GitHub:
   - Repository name: `antigravity-pipeline`
   - Description: "Automated slide-to-video synchronization pipeline"
   - Visibility: Public
   - Initialize with: None (push existing)

2. **Initialize local repository**:
```bash
cd c:\Users\SLI15592\.gemini\antigravity\scratch
git init
git add .
git commit -m "Initial commit: Production-ready slide-to-video pipeline"
git branch -M main
git remote add origin https://github.com/kvsrGANESH9/antigravity-pipeline.git
git push -u origin main
```

### Repository Structure

```
antigravity-pipeline/
├── README.md                 # User guide
├── DEPLOYMENT.md            # This file
├── requirements.txt         # Python dependencies
├── config.py                # Configuration file
├── main.py                  # Entry point
├── build.bat               # Build script for .exe
├── gui_launcher.py         # GUI application
├── pipeline.py             # Core pipeline logic
├── pairing_manager.py      # Scene-to-slide matching
├── pdf_converter.py        # PDF to slides conversion
├── scene_detection.py      # Video scene detection
├── scale_fit.py           # Image scaling utility
├── video_composer.py       # FFmpeg wrapper
├── bin/                   # FFmpeg binaries (DO NOT COMMIT)
│   ├── ffmpeg.exe
│   └── ffprobe.exe
└── .gitignore            # Git ignore rules
```

## Building Releases

### Prerequisites

```bash
# Install build dependencies
pip install pyinstaller
```

### Build Process

1. **Test locally first**:
```bash
python gui_launcher.py
python pipeline.py --help
```

2. **Run build script**:
```bash
cd c:\Users\SLI15592\.gemini\antigravity\scratch
.\build.bat
```

3. **Verify output**:
```bash
# Check that dist\pipeline.exe exists
dir dist\
```

### Create Release Package

1. **Create release directory**:
```bash
mkdir antigravity-pipeline-v2.0.0
cd antigravity-pipeline-v2.0.0
```

2. **Copy files**:
```bash
copy dist\pipeline.exe .
copy config.py .
copy README.md .
copy requirements.txt .
mkdir bin
copy ..\bin\ffmpeg.exe bin\
copy ..\bin\ffprobe.exe bin\
```

3. **Create ZIP file**:
```bash
# Using 7-Zip or built-in tools
# Zip contains: pipeline.exe, config.py, README.md, requirements.txt, bin/
```

## Publishing to GitHub

### Create Release

1. **Tag the commit**:
```bash
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

2. **Create GitHub Release**:
   - Go to: https://github.com/kvsrGANESH9/antigravity-pipeline/releases
   - Click "Create a new release"
   - Tag: `v2.0.0`
   - Title: `Antigravity Pipeline v2.0.0`
   - Description:
     ```
     ## Changes
     - Initial production release
     - GUI-based interface for easy use
     - Comprehensive reporting with processing times
     - Multi-system deployment support
     
     ## Installation
     1. Download `antigravity-pipeline-v2.0.0.zip`
     2. Extract all files
     3. Double-click `pipeline.exe`
     
     ## Requirements
     - Windows 7 or later
     - 4GB RAM minimum
     ```
   - Attach files: `antigravity-pipeline-v2.0.0.zip`
   - Publish release

## GitHub Actions (Optional CI/CD)

Create `.github/workflows/build.yml`:

```yaml
name: Build EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Build with PyInstaller
        run: .\build.bat
      - name: Upload to Release
        uses: actions/upload-release-asset@v1
```

## Versioning

- **Major.Minor.Patch** format (e.g., v2.0.0)
- Update in multiple places:
  - Tag: `v2.0.0`
  - Release title
  - README if needed

## Update Checklist

Before each release:

- [ ] Test GUI input/output
- [ ] Test CLI mode
- [ ] Verify all 9 Python files present
- [ ] Check FFmpeg binaries in bin/
- [ ] Update config.py defaults
- [ ] Run build.bat successfully
- [ ] Test standalone .exe
- [ ] Update requirements.txt if dependencies changed
- [ ] Update README with new features
- [ ] Create git tag
- [ ] Create GitHub release with .zip

## Distribution Methods

### Method 1: Direct Download from GitHub
- Users download from Releases page
- Most straightforward method

### Method 2: Package Manager
- Could publish to PyPI (complex, not recommended for .exe)

### Method 3: Installer
- Could create Windows .msi installer (future enhancement)

## Support & Maintenance

- Monitor GitHub Issues
- Provide updates in releases
- Keep FFmpeg binaries current
- Document any config changes

---

**Current Version**: v2.0.0 (June 2026)
