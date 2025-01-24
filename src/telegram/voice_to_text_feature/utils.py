import tempfile

from moviepy import VideoFileClip


def extract_audio(video):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as file:
        file.write(video)
        clip = VideoFileClip(file.name)

    with tempfile.NamedTemporaryFile(suffix='.ogg') as file:
        clip.audio.write_audiofile(file.name, ffmpeg_params=['-ac', '1'], logger=None)   
        voice_bytes = file.read()

    return voice_bytes


def choose_media(message):
    media_list = list(media for media in [message.voice, message.video_note] if media is not None)
    return None if not media_list else media_list[0]
