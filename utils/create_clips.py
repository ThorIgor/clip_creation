import streamlit as st
import subprocess
import tempfile
import zipfile
import os
import io

@st.cache_data()
def get_video_duration(input_bytes) -> float:
    """ Get the duration of the video in seconds. """
    ffmpeg_command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        'pipe:0'
    ]

    process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate(input=input_bytes)
    
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe error: {error.decode()}")
    
    return float(output)

@st.cache_data()
def split_video(input_bytes, extension, num_clips) -> list[bytes]:
    """Split video into num_clips chunks"""
    duration = get_video_duration(input_bytes)
    clip_duration = duration / num_clips
    
    clips = []

    vf = tempfile.NamedTemporaryFile(mode='wb+', delete=False)

    vf.write(input_bytes)
    video_file = vf.name
    
    for i in range(num_clips):
        of = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
        out_file = of.name

        start_time = i * clip_duration
            
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-f', extension,
            '-i', video_file,
            '-ss', str(start_time),
            '-t', str(clip_duration),
            '-f', 'mp4',
            out_file
        ]

        process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {error.decode()}")
        
        out_bytes = of.read()

        of.close()
        os.remove(out_file)

        clips.append(out_bytes)
    
    vf.close()
    os.remove(video_file)
        
    return clips

@st.cache_data()
def add_audio_to_clip(video_bytes, audio_bytes):
    """Repalce audio stream in video_bytes on audio_bytes"""
    vf = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    af = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
    of = tempfile.NamedTemporaryFile(mode="wb+", delete=False)

    vf.write(video_bytes)
    video_file = vf.name

    af.write(audio_bytes)
    audio_file = af.name

    out_file = of.name

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-i", audio_file,
        "-c", "copy",
        "-map", "0:0",
        "-map", "1:0",
        "-shortest",
        "-f", "mp4",
        out_file
    ]

    process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, error = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {error.decode()}")
    
    out_bytes = of.read()

    vf.close()
    af.close()
    of.close()

    os.remove(video_file)
    os.remove(audio_file)
    os.remove(out_file)

    return out_bytes

@st.cache_data()
def create_zip_from_bytes(clips):
    """Conver list of clips bytes into archive bytes"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, clip in enumerate(clips):
            zip_file.writestr(f"clip_{i}.mp4", clip)
    
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.read()
    
    return zip_bytes