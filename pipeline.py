import argparse
import os
import time
import csv
import glob
import traceback
import config

from pdf_converter import convert_pdf_to_slides
from scene_detection import detect_scenes_in_video
from pairing_manager import prepare_ffconcat_data
from video_composer import extract_trimmed_audio, extract_trimmed_video, generate_ffconcat_script, compose_final_video, get_media_duration, validate_durations

def setup_directories(
    workspace_dir=None,
    source_dir=None,
    videos_dir=None,
    slides_dir=None,
    output_dir=None,
    reports_dir=None,
    temp_dir=None
):
    if workspace_dir is None:
        workspace_dir = config.BASE_DIR

    if source_dir is None:
        source_dir = os.path.join(workspace_dir, "SOURCE")
    if videos_dir is None:
        videos_dir = os.path.join(workspace_dir, "VIDEOS")
    if slides_dir is None:
        slides_dir = os.path.join(workspace_dir, "SLIDES")
    if output_dir is None:
        output_dir = os.path.join(workspace_dir, "OUTPUT")
    if reports_dir is None:
        reports_dir = os.path.join(workspace_dir, "REPORTS")
    if temp_dir is None:
        temp_dir = os.path.join(workspace_dir, "TEMP")

    dirs = {
        'source': source_dir,
        'videos': videos_dir,
        'slides': slides_dir,
        'output': output_dir,
        'reports': reports_dir,
        'temp_audio': os.path.join(temp_dir, "audio"),
        'temp_frames': os.path.join(temp_dir, "frames"),
        'temp_ffconcat': os.path.join(temp_dir, "ffconcat")
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs

def log_to_file(log_path, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def _truthy_env(name):
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}

def read_completed_courses(report_path):
    latest_by_course = {}
    if not os.path.exists(report_path):
        return set()
    try:
        with open(report_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                course_name = row.get("Course Name")
                if course_name:
                    latest_by_course[course_name] = row
    except Exception as e:
        print(f"Warning: Could not read completed courses from report: {e}")
        return set()

    completed = set()
    for course_name, row in latest_by_course.items():
        output_video = row.get("Output Video", "")
        if row.get("Status") in ["SUCCESS", "WARNING"] and output_video and os.path.exists(output_video):
            completed.add(course_name)
    return completed

def append_to_report(report_path, course_name, slide_count, scene_count, 
                     warning_reason, extra_scenes, unmatched_slides, output_video, status, processing_time=0.0):
    file_exists = os.path.exists(report_path)
    headers = [
        "Course Name", "Slide Count", "Scene Count", 
        "Warning Reason", "Extra Scenes", "Unmatched Slides", "Output Video", "Status", "Processing Time (sec)"
    ]
    try:
        with open(report_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow([
                course_name, slide_count, scene_count, warning_reason, 
                extra_scenes, unmatched_slides, output_video, status, f"{processing_time:.2f}"
            ])
    except PermissionError:
        print(f"Warning: Could not write to {report_path} (File might be open in another program).")

def clean_temp_files(course_name, dirs):
    for dir_key in ['temp_audio', 'temp_frames', 'temp_ffconcat']:
        for f in glob.glob(os.path.join(dirs[dir_key], f"{course_name}*")):
            try:
                os.remove(f)
            except Exception:
                pass

def process_course(course_name, video_path, dirs, log_path, report_csv):
    start_time = time.time()
    log_to_file(log_path, f"--- Starting processing for course: {course_name} ---")
    
    pdf_path = os.path.join(dirs['source'], f"{course_name}.pdf")
    output_video_path = os.path.join(dirs['output'], f"{course_name}_Cleaned.mp4")
    
    if not os.path.exists(pdf_path):
        elapsed = time.time() - start_time
        log_to_file(log_path, f"FAILED: Missing PDF source slide file: {pdf_path}")
        append_to_report(report_csv, course_name, 0, 0, "MISSING_PDF", 0, 0, "None", "FAILED", elapsed)
        return "FAILED"
        
    try:
        slide_dir = os.path.join(dirs['slides'], course_name)
        pdf_pages, is_skipped = convert_pdf_to_slides(pdf_path, slide_dir)
        log_to_file(log_path, f"Slides ready ({pdf_pages} pages). Skipped generation: {is_skipped}")
    except Exception as e:
        elapsed = time.time() - start_time
        log_to_file(log_path, f"FAILED: Failed to render slides from PDF: {e}")
        append_to_report(report_csv, course_name, 0, 0, "CORRUPT_FILE", 0, 0, "None", "FAILED", elapsed)
        return "FAILED"

    try:
        intro_end_time = getattr(config, "HARDCODED_INTRO_CUT", 4.0)
        
        temp_audio_path = os.path.join(dirs['temp_audio'], f"{course_name}_trimmed.m4a")
        temp_trimmed_video_path = os.path.join(dirs['temp_frames'], f"{course_name}_trimmed.mp4")
        
        extract_trimmed_audio(video_path, intro_end_time, temp_audio_path)
        extract_trimmed_video(video_path, intro_end_time, temp_trimmed_video_path)
        audio_dur = get_media_duration(temp_audio_path)
        
        scenes = detect_scenes_in_video(temp_trimmed_video_path)
        detected_scenes = len(scenes)
        
        slide_seq_data, status, warning_reason, extra_scenes, unmatched_slides = prepare_ffconcat_data(
            scenes, slide_dir, audio_dur, video_path=temp_trimmed_video_path
        )
        
        if status == "FAILED":
            elapsed = time.time() - start_time
            log_to_file(log_path, f"FAILED: {warning_reason}")
            append_to_report(report_csv, course_name, pdf_pages, detected_scenes, warning_reason, 0, 0, "None", "FAILED", elapsed)
            return "FAILED"
            
        ffconcat_path = os.path.join(dirs['temp_ffconcat'], f"{course_name}_slides.txt")
        generate_ffconcat_script(slide_seq_data, ffconcat_path, audio_duration=audio_dur)
        
        compose_final_video(ffconcat_path, temp_audio_path, output_video_path, audio_duration=audio_dur)

        duration_ok, duration_error = validate_durations(output_video_path, temp_audio_path)
        if not duration_ok:
            elapsed = time.time() - start_time
            log_to_file(log_path, f"FAILED: {duration_error}")
            append_to_report(report_csv, course_name, pdf_pages, detected_scenes, 
                             "DURATION_MISMATCH", extra_scenes, unmatched_slides, output_video_path, "FAILED", elapsed)
            return "FAILED"
        
        elapsed = time.time() - start_time
        log_to_file(log_path, f"{status}: Cleaned video exported to {output_video_path} (Time: {elapsed:.2f}s)")
        append_to_report(report_csv, course_name, pdf_pages, detected_scenes, 
                         warning_reason, extra_scenes, unmatched_slides, output_video_path, status, elapsed)
                         
    except Exception as e:
        elapsed = time.time() - start_time
        log_to_file(log_path, f"FAILED: {e}\n{traceback.format_exc()}")
        append_to_report(report_csv, course_name, pdf_pages, 0, "FFMPEG_FAILURE", 0, 0, "None", "FAILED", elapsed)
        return "FAILED"
        
    finally:
        if config.CLEAN_TEMP_AFTER_SUCCESS:
            clean_temp_files(course_name, dirs)

    return status

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Antigravity slide-to-video pipeline. Provide PDF and raw video directories to build cleaned output videos."
    )
    parser.add_argument("--workspace", help="Workspace root containing SOURCE, VIDEOS, SLIDES, OUTPUT, REPORTS and TEMP directories.")
    parser.add_argument("--pdf-dir", help="Directory containing source PDF files.")
    parser.add_argument("--video-dir", help="Directory containing raw MP4 video files.")
    parser.add_argument("--slides-dir", help="Directory to store generated slide images.")
    parser.add_argument("--output-dir", help="Directory to store final output videos.")
    parser.add_argument("--reports-dir", help="Directory to store logs and reports.")
    parser.add_argument("--temp-dir", help="Directory to store temporary processing files.")
    parser.add_argument("--force", action="store_true", help="Force reprocess even if course has already been successfully completed.")
    parser.add_argument("--no-clean-temp", action="store_true", help="Do not delete temporary files after successful processing.")
    return parser.parse_args()


def main(args=None):
    if args is None:
        args = parse_arguments()

    workspace = args.workspace or os.getenv("PIPELINE_WORKSPACE", config.BASE_DIR)
    force_reprocess = args.force or getattr(config, "FORCE_REPROCESS", False) or _truthy_env("PIPELINE_FORCE_REPROCESS")
    if args.no_clean_temp:
        config.CLEAN_TEMP_AFTER_SUCCESS = False

    temp_dir_arg = getattr(args, 'temp_dir', None)
    dirs = setup_directories(
        workspace_dir=workspace,
        source_dir=args.pdf_dir,
        videos_dir=args.video_dir,
        slides_dir=args.slides_dir,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        temp_dir=temp_dir_arg
    )
    log_path = os.path.join(dirs['reports'], "processing_log.txt")
    report_csv = os.path.join(dirs['reports'], "processing_report.csv")
    
    start_batch_time = time.time()
    log_to_file(log_path, "==================================================")
    log_to_file(log_path, "Starting Simplified Robust Batch Run")
    log_to_file(log_path, "==================================================")
    
    completed_courses = set()
    if config.SKIP_ALREADY_PROCESSED and not force_reprocess:
        completed_courses = read_completed_courses(report_csv)
        log_to_file(log_path, f"Resume check: Found {len(completed_courses)} previously completed courses.")
    elif force_reprocess:
        log_to_file(log_path, "Force reprocess enabled: existing completed report entries will be ignored.")
    
    video_files = glob.glob(os.path.join(dirs['videos'], "*.mp4"))
    
    stats = {'total': len(video_files), 'success': 0, 'warning': 0, 'skipped': 0, 'failed': 0}
    
    for vf in video_files:
        filename = os.path.basename(vf)
        course_name, _ = os.path.splitext(filename)
        
        if config.SKIP_ALREADY_PROCESSED and not force_reprocess and course_name in completed_courses:
            log_to_file(log_path, f"Skipping course '{course_name}' (already processed successfully).")
            stats['skipped'] += 1
            continue
            
        status = process_course(course_name, vf, dirs, log_path, report_csv)
        if status == "SUCCESS": stats['success'] += 1
        elif status == "WARNING": stats['warning'] += 1
        else: stats['failed'] += 1
        
    total_proc_time = time.time() - start_batch_time
    summary = f"""
==================================================
BATCH PROCESSING SUMMARY
========================
Total Files: {stats['total']}
Processed Successfully: {stats['success']}
Processed with Warnings: {stats['warning']}
Skipped Files: {stats['skipped']}
Failed Files: {stats['failed']}
Total Processing Time: {total_proc_time:.2f} seconds
==================================================
"""
    log_to_file(log_path, summary)
    print(summary)

if __name__ == "__main__":
    main()
