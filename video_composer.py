import os
import subprocess
import config

def run_background_process(cmd, **kwargs):
    """
    Runs FFmpeg/FFprobe without opening a visible console window on Windows.
    """
    if os.name == "nt":
        kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs.setdefault("startupinfo", startupinfo)
    return subprocess.run(cmd, **kwargs)

def get_media_duration(file_path):
    """
    Retrieves the duration of a media file in seconds using ffprobe.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Media file not found: {file_path}")
        
    cmd = [
        config.FFPROBE_PATH,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    
    result = run_background_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    duration_str = result.stdout.strip()
    return float(duration_str)

def get_stream_duration(file_path, stream_type):
    """
    Retrieves the duration of the first stream matching stream_type using ffprobe.
    stream_type should be "v" for video or "a" for audio.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Media file not found: {file_path}")

    cmd = [
        config.FFPROBE_PATH,
        "-v", "error",
        "-select_streams", f"{stream_type}:0",
        "-show_entries", "stream=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]

    result = run_background_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    duration_str = result.stdout.strip()
    if not duration_str or duration_str == "N/A":
        return get_media_duration(file_path)
    return float(duration_str)

def extract_trimmed_audio(video_path, intro_end_time, output_audio_path):
    """
    Extracts audio from video_path starting from intro_end_time using FFmpeg.
    """
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    
    cmd = [
        config.FFMPEG_PATH,
        "-y",
        "-ss", str(intro_end_time),
        "-i", video_path,
        "-vn",
        "-c:a", "aac",
        "-b:a", "192k",
        output_audio_path
    ]
    
    print(f"Extracting trimmed audio starting at {intro_end_time}s to {output_audio_path}...")
    run_background_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def extract_trimmed_video(video_path, intro_end_time, output_video_path):
    """
    Extracts a trimmed video without audio starting from intro_end_time using FFmpeg.
    """
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    
    cmd = [
        config.FFMPEG_PATH,
        "-y",
        "-ss", str(intro_end_time),
        "-i", video_path,
        "-c:v", "copy",
        "-an",
        output_video_path
    ]
    
    print(f"Extracting trimmed video starting at {intro_end_time}s to {output_video_path}...")
    run_background_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def generate_ffconcat_script(slide_sequence_data, output_script_path, audio_duration=None):
    """
    Generates the ffconcat script for FFmpeg's concat demuxer.
    Consumes the prepared slide sequence data.
    If audio_duration is provided, extends the last slide to perfectly match it.
    """
    dir_name = os.path.dirname(output_script_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    lines = ["ffconcat version 1.0"]
    limit = len(slide_sequence_data)
    
    for i, data in enumerate(slide_sequence_data):
        slide_path = data['path']
        duration = data['duration']
        
        if i == limit - 1 and audio_duration is not None:
            # For the last slide, calculate the elapsed time before it
            elapsed = sum(d['duration'] for d in slide_sequence_data[:i])
            # The remaining duration should be exactly enough to reach audio_duration
            if audio_duration > elapsed:
                duration = audio_duration - elapsed
                print(f"Adjusted last slide duration to {duration:.3f}s to match audio.")
        
        # FFmpeg concat demuxer requires forward slashes and escaped single quotes
        normalized_path = slide_path.replace("\\", "/")
        lines.append(f"file '{normalized_path}'")
        lines.append(f"duration {duration}")
        
    # Append the last slide again without a duration to satisfy FFmpeg's concat demuxer behavior
    if limit > 0:
        normalized_path = slide_sequence_data[-1]['path'].replace("\\", "/")
        lines.append(f"file '{normalized_path}'")
        
    with open(output_script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    return output_script_path

def compose_final_video(ffconcat_script_path, temp_audio_path, output_video_path, audio_duration=None):
    """
    Muxes the slides and audio into a final MP4 using local FFmpeg.
    """
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    
    cmd = [
        config.FFMPEG_PATH,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", ffconcat_script_path,
        "-i", temp_audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-threads", "0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart"
    ]
    
    if audio_duration is not None:
        duration_text = f"{float(audio_duration):.3f}"
        cmd.extend([
            "-vf", f"fps=25,format=yuv420p,trim=duration={duration_text},setpts=PTS-STARTPTS",
            "-af", f"atrim=duration={duration_text},asetpts=PTS-STARTPTS",
            "-shortest",
            "-t", duration_text
        ])
    else:
        cmd.extend(["-vf", "fps=25,format=yuv420p"])
        cmd.append("-shortest")
        
    cmd.append(output_video_path)
    
    print(f"Composing final video to {output_video_path}...")
    result = run_background_process(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr}")
        raise RuntimeError(f"FFmpeg composition failed with exit code {result.returncode}")

def validate_durations(output_video_path, trimmed_audio_path, tolerance=None):
    """
    Validates that the final video duration matches the trimmed audio duration within tolerance.
    """
    if tolerance is None:
        tolerance = config.DURATION_TOLERANCE_SECONDS
        
    video_dur = get_stream_duration(output_video_path, "v")
    output_audio_dur = get_stream_duration(output_video_path, "a")
    source_audio_dur = get_stream_duration(trimmed_audio_path, "a")
    
    stream_diff = abs(video_dur - output_audio_dur)
    source_diff = abs(output_audio_dur - source_audio_dur)
    print(
        "Duration Validation: "
        f"Video={video_dur:.3f}s, OutputAudio={output_audio_dur:.3f}s, "
        f"SourceAudio={source_audio_dur:.3f}s, "
        f"StreamDiff={stream_diff:.3f}s, SourceDiff={source_diff:.3f}s "
        f"(Tolerance={tolerance}s)"
    )
    
    if stream_diff > tolerance:
        return False, f"Output stream duration mismatch: Video={video_dur:.3f}s, Audio={output_audio_dur:.3f}s (Diff={stream_diff:.3f}s > {tolerance}s)"

    if source_diff > tolerance:
        return False, f"Output audio duration mismatch: OutputAudio={output_audio_dur:.3f}s, SourceAudio={source_audio_dur:.3f}s (Diff={source_diff:.3f}s > {tolerance}s)"
        
    return True, None
