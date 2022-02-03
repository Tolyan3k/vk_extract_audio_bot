from youtube_dl import YoutubeDL
from typing import Optional
import re

from bot_types.VideoDownloadSettings import VideoDownloadSetting
from bot_types.VideoPlatform import VideoPlatform
from bot_types.VideoInfo import VideoInfo
from __init__ import vk_user_session
import config

class VideoService(object):
    @staticmethod
    def get_video_info(link: str) -> VideoInfo:
        platform = None
        #Если yotube_dl не выкинет исключение, то можно узнать платформу по экстрактору
        try:
            with YoutubeDL({}) as ydl:
                info_dict = ydl.extract_info(link, download=False)

                #Пока будет распозновать только видосы из ВК
                if info_dict['extractor'] == "vk":
                    platform = VideoPlatform.VK
                else:
                    platform = VideoPlatform.OTHER
        except:
            pass

        #Иначе проверяем остальные платформы
        if platform == None:
            raise "Не удалось определить платформу"

        return VideoInfo(
            title=info_dict['title'],
            author=info_dict['uploader'],
            platform=platform,
            duration=info_dict['duration']
        )

    @staticmethod
    def download_video(link: str, download_setting: VideoDownloadSetting) -> Optional[str]:
        video_info = VideoService.get_video_info(link)

        if video_info.platform == VideoPlatform.VK \
            and download_setting.min_duration <= video_info.duration <= download_setting.max_duration:
            ydl_opts = {
                'format' : 'best',
                #'outtmpl': config.DIRS['videos'] + '/{%(title)s}_{%(uploader)s}.mp4',
                'outtmpl': config.DIRS['videos'] + '/temp.mp4',
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        else:
            return None

        #return f"{{{video_info.title}}}_{{{video_info.author}}}.mp4"
        return 'temp.mp4'
