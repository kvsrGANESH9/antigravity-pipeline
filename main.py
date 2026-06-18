#!/usr/bin/env python3
"""
Antigravity Slide-to-Video Pipeline - Main Entry Point
Launches the GUI application
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    try:
        from gui_launcher import main as launch_gui
        launch_gui()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("\nAttempting to run CLI version instead...")
        import pipeline
        pipeline.main()

if __name__ == "__main__":
    main()
