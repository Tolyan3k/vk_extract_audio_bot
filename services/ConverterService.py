from moviepy.audio.AudioClip import CompositeAudioClip, AudioClip
from typing import Optional
import moviepy.editor
import ffmpeg
import math

from bot_types.AudioConvertSettings import AudioConvertSettings

from config import VK_MAX_AUDIOFILE_SIZE_MB
from config import BOT_WORK_DIRS


class ConverterService(object):
    @staticmethod
    def has_audio(video_file_name: str):
        video_file_info = ffmpeg.probe(BOT_WORK_DIRS['videos'] + '/' + video_file_name)

        if video_file_info.get('streams') and len(video_file_info['streams']) > 1:
            return True

        return False
        
    
    @staticmethod
    def convert_video_to_audio(video_file_name: str, audio_convert_settings: AudioConvertSettings) -> str:
        video_file_info = ffmpeg.probe(BOT_WORK_DIRS['videos'] + '/' + video_file_name)

        bit_rate = None
        if video_file_info.get('streams') \
            and len(video_file_info.get('streams')) > 1 \
            and video_file_info.get('streams')[1].get('bit_rate'):

            bit_rate = video_file_info.get('streams')[1].get('bit_rate')

            if video_file_info.get('streams')[1].get('duration'):
                duration = video_file_info.get('streams')[1].get('duration')
                vk_max_audiofile_size_bits = VK_MAX_AUDIOFILE_SIZE_MB * (1000 ** 2) * 8
                vk_max_audufile_bitrate = int(math.floor(vk_max_audiofile_size_bits / float(duration)))

                bit_rate = str(min(int(bit_rate), vk_max_audufile_bitrate))

        if audio_convert_settings:
            try:
                with moviepy.editor.VideoFileClip(BOT_WORK_DIRS['videos'] + '/' + video_file_name) as video_clip:
                    audio_clip = video_clip.audio
                    audio_clip_fps = audio_clip.fps
                    audio_clip_duration = audio_clip.duration
                    audio_clip_nchannels = audio_clip.nchannels
                        
                    if audio_clip.duration < audio_convert_settings.min_duration:
                        silence = AudioClip(
                            make_frame= lambda t: [0] * audio_clip_nchannels,
                            duration= audio_convert_settings.min_duration - audio_clip_duration, 
                            fps= audio_clip_fps
                        )
                        audio_clip = CompositeAudioClip([audio_clip, silence])

                    audio_clip.write_audiofile(BOT_WORK_DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3', audio_clip_fps, bitrate=bit_rate)
            except Exception as error:
                raise error
                
        return (video_file_name[:-3] + 'mp3')
