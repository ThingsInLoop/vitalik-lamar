import tempfile

from moviepy import VideoFileClip


def extract_audio(video, postfix):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as file:
        file.write(video)
        clip = VideoFileClip(file.name)

    with tempfile.NamedTemporaryFile(suffix='.ogg') as file:
        clip.audio.write_audiofile(file.name, ffmpeg_params=['-ac', '1'], logger=None)   
        voice_bytes = file.read()

    return voice_bytes
