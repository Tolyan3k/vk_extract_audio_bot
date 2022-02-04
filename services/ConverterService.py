from typing import Optional
from moviepy.audio.AudioClip import CompositeAudioClip, AudioClip
import moviepy.editor

from bot_types.AudioConvertSettings import AudioConvertSettings
from config import DIRS

class ConverterService(object):
    @staticmethod
    def convert_video_to_audio(video_file_name: str, audio_convert_settings: Optional[AudioConvertSettings] = None) -> str:
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

                    audio_clip.write_audiofile(DIRS['audios'] + '/' + video_file_name[:-3] + 'mp3', audio_clip_fps)
            except Exception as error:
                raise error
                
        return (video_file_name[:-3] + 'mp3')
