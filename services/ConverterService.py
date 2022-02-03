from typing import Optional
import moviepy.editor

from bot_types.AudioConvertSettings import AudioConvertSettings
from config import DIRS

class ConverterService(object):
    @staticmethod
    def convert_video_to_audio(video_file_name: str, audio_convert_settings: Optional[AudioConvertSettings] = None) -> str:
        if audio_convert_settings:
            with moviepy.editor.VideoFileClip(DIRS['videos'] + '/' + video_file_name) as video_clip:
                if video_clip.audio.duration < audio_convert_settings.min_duration:
                    audio_clip = video_clip.audio.set_end(audio_convert_settings.min_duration)
                    audio_clip.write_audiofile(DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3')
                video_clip.audio.write_audiofile(DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3')
        # video = moviepy.editor.VideoFileClip(DIRS['videos'] + '/' + video_file_name)
        # video.audio.write_audiofile(DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3')
        # video.close()        

        return (video_file_name[:-3] + 'mp3')
