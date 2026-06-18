# Setting Up GitHub Repository

## Quick Start Guide

Follow these steps to deploy your Antigravity Pipeline to GitHub.

### Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "+" → "New repository"
3. Enter details:
   - **Repository name**: `antigravity-pipeline`
   - **Description**: "Automated slide-to-video synchronization pipeline"
   - **Visibility**: Public
   - **Initialize repository**: Do NOT check any options
4. Click "Create repository"

### Step 2: Initialize Git Locally

Open PowerShell in your project directory and run:

```powershell
cd c:\Users\SLI15592\.gemini\antigravity\scratch

# Initialize git
git init
git add .
git commit -m "Initial commit: Production-ready slide-to-video pipeline"
git branch -M main
git remote add origin https://github.com/kvsrGANESH9/antigravity-pipeline.git
git push -u origin main
```

### Step 3: Verify on GitHub

1. Go to your repository: `https://github.com/kvsrGANESH9/antigravity-pipeline`
2. You should see all files listed:
   - `.gitignore`
   - `build.bat`
   - `config.py`
   - `DEPLOYMENT.md`
   - `gui_launcher.py`
   - `main.py`
   - `pairing_manager.py`
   - `pdf_converter.py`
   - `pipeline.py`
   - `README.md`
   - `requirements.txt`
   - `scale_fit.py`
   - `scene_detection.py`
   - `video_composer.py`
   - `bin/` folder with FFmpeg binaries

## Building and Releasing the EXE

### Step 1: Build the Executable

```powershell
# Navigate to project directory
cd c:\Users\SLI15592\.gemini\antigravity\scratch

# Run build script
.\build.bat
```

This creates `dist\pipeline.exe`

### Step 2: Create Release Package

```powershell
# Create temporary directory
mkdir release_package
cd release_package

# Copy files
copy ..\dist\pipeline.exe .
copy ..\config.py .
copy ..\README.md .
copy ..\requirements.txt .
xcopy ..\bin bin\ /E /I

# Go back to project
cd ..
```

### Step 3: Create ZIP for Release

Using Windows built-in or 7-Zip:
- Right-click `release_package` folder
- Send to → Compressed (zipped) folder
- Creates `release_package.zip`
- Rename to `antigravity-pipeline-v2.0.0.zip`

### Step 4: Create GitHub Release

1. Go to your repository
2. Click "Releases" (on the right sidebar)
3. Click "Create a new release"
4. Fill in:
   - **Tag version**: `v2.0.0`
   - **Release title**: `Antigravity Pipeline v2.0.0`
   - **Description**:
     ```
     # Antigravity Pipeline v2.0.0 - Production Release
     
     ## Features
     - GUI-based interface for easy use
     - Automatic PDF-to-video synchronization
     - Scene detection and intro removal
     - Comprehensive processing reports
     - Multi-system deployment support
     
     ## Installation
     1. Download `antigravity-pipeline-v2.0.0.zip`
     2. Extract all files to your desired location
     3. Double-click `pipeline.exe` to start
     
     ## System Requirements
     - Windows 7 or later
     - 4GB RAM minimum (8GB recommended)
     - 50GB disk space for typical processing
     
     ## Quick Start
     1. Create two folders: `SOURCE` (PDFs) and `VIDEOS` (MP4s)
     2. Place your PDF and video files there
     3. Run pipeline.exe
     4. Select the folders when prompted
     5. Click "Start Processing"
     6. Check REPORTS folder for results
     
     ## Documentation
     See README.md for detailed usage instructions.
     ```

5. Click "Attach binaries" and select `antigravity-pipeline-v2.0.0.zip`
6. Click "Publish release"

### Step 5: Verify Release

1. Go to your repository
2. Click "Releases"
3. You should see `v2.0.0` listed
4. Download the ZIP to test it

## Future Updates

When you want to release version 2.0.1:

```powershell
# Make code changes, test, then:
git add .
git commit -m "Version 2.0.1: Bug fixes"
git tag -a v2.0.1 -m "Release version 2.0.1"
git push origin main
git push origin v2.0.1

# Then repeat "Building and Releasing the EXE" steps
```

## Sharing with Others

Your repository URL is:
```
https://github.com/kvsrGANESH9/antigravity-pipeline
```

Users can:
1. Download releases from: `https://github.com/kvsrGANESH9/antigravity-pipeline/releases`
2. Or clone the source: `git clone https://github.com/kvsrGANESH9/antigravity-pipeline.git`

## GitHub Pages (Optional Documentation Site)

You can create a website for your project:

1. Go to repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose "main" branch and "/root" folder
4. Your site will be available at: `https://kvsrganesh9.github.io/antigravity-pipeline/`

## Troubleshooting

### "fatal: not a git repository"
```powershell
# Make sure you're in the correct directory
cd c:\Users\SLI15592\.gemini\antigravity\scratch
```

### "error: The requested URL returned error: 401"
- Check your GitHub credentials
- Ensure you have access to the repository

### build.bat fails
- Ensure Python 3.8+ is installed
- Run: `pip install pyinstaller`
- Check that all files are present

---

**Next Steps:**
1. Follow this guide to create your GitHub repository
2. Build the executable using build.bat
3. Create a release with the EXE
4. Share the repository link!

**Questions?** Check DEPLOYMENT.md for more details.
