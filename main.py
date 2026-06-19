#!/usr/bin/env python3
"""
Antigravity Slide-to-Video Pipeline - Main Entry Point
Launches the GUI application
"""

import sys
import os
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def runtime_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def report_startup_error(error):
    error_path = os.path.join(runtime_dir(), "startup_error.txt")
    with open(error_path, "w", encoding="utf-8") as f:
        f.write(f"Error launching GUI: {error}\n\n")
        f.write(traceback.format_exc())

    if getattr(sys, "frozen", False):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None,
                f"Could not launch the GUI.\n\nDetails were written to:\n{error_path}",
                "Antigravity Pipeline",
                0x10,
            )
        except Exception:
            pass

    return error_path

def main():
    """Main entry point"""
    try:
        from gui_launcher import main as launch_gui
        launch_gui()
    except Exception as e:
        error_path = report_startup_error(e)
        print(f"Error launching GUI: {e}")
        print(f"Details written to: {error_path}")
        if getattr(sys, "frozen", False):
            return 1
        print("\nAttempting to run CLI version instead...")
        import pipeline
        pipeline.main()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
