import os

from moviepy import VideoFileClip


def extract_audio(video, postfix):
    video_file_name = f'/var/tmp/.voice-to-text-video-{postfix}.mp4'
    audio_file_name = f'/var/tmp/.voice-to-text-audio-{postfix}.ogg'
    with open(video_file_name, 'wb') as file:
      file.write(video)

    clip = VideoFileClip(video_file_name)
    clip.audio.write_audiofile(audio_file_name,
                               ffmpeg_params=['-ac', '1'],
                               logger=None)

    with open(audio_file_name, 'rb') as file:
      voice_bytes = file.read()

    os.remove(video_file_name)
    os.remove(audio_file_name)

    return voice_bytes
