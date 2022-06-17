from moviepy.audio.AudioClip import CompositeAudioClip, AudioClip
from typing import Optional
import moviepy.editor
import ffmpeg

from bot_types.AudioConvertSettings import AudioConvertSettings
from config import DIRS

class ConverterService(object):
    @staticmethod
    def convert_video_to_audio(video_file_name: str, audio_convert_settings: AudioConvertSettings) -> str:
        video_file_info = ffmpeg.probe(DIRS['videos'] + '/' + video_file_name)

        bit_rate = None
        if video_file_info.get('streams') \
            and len(video_file_info.get('streams')) > 1 \
            and video_file_info.get('streams')[1].get('bit_rate'):

            bit_rate = video_file_info.get('streams')[1].get('bit_rate')


        if audio_convert_settings:
            try:
                with moviepy.editor.VideoFileClip(DIRS['videos'] + '/' + video_file_name) as video_clip:
                    audio_clip = video_clip.audio
                    audio_clip_fps = audio_clip.fps

                    if audio_clip.duration < audio_convert_settings.min_duration:
                        silence = AudioClip(
                            make_frame=lambda t: [0] * audio_clip.nchannels,
                            duration=audio_convert_settings.min_duration - audio_clip.duration, 
                            fps=audio_clip.fps
                        )
                        audio_clip = CompositeAudioClip([audio_clip, silence])

                    audio_clip.write_audiofile(DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3', audio_clip_fps, bitrate=bit_rate)
            except Exception as error:
                raise error
                
        return (video_file_name[:-3] + 'mp3')
