import yt_dlp
import youtube_dl

from bot_types.VideoDownloadSettings import VideoDownloadSettings
from bot_types.VideoPlatform import VideoPlatform
from bot_types.VideoInfo import VideoInfo
import config

class VideoService(object):
    @staticmethod
    def get_video_info(link: str) -> VideoInfo:
        platform = None

        with yt_dlp.YoutubeDL({}) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            if info_dict is None:
                raise Exception("Не удалось извлечь информацию из видео")

            if info_dict['extractor'] == "vk":
                platform = VideoPlatform.VK
            elif info_dict['extractor'] == 'youtube':
                platform = VideoPlatform.YOUTUBE
            elif info_dict.get('extractor') is not None:
                platform = VideoPlatform.OTHER
        
        return VideoInfo(
            title=info_dict['title'],
            author=info_dict['uploader'],
            platform=platform,
            duration=info_dict['duration']
        )

    @staticmethod
    def get_video_info_from_vk_video(vk_video_obj: dict) -> VideoInfo:
        platform = VideoPlatform.VK
        title = vk_video_obj['title']
        if vk_video_obj.get('user_id'):
            author = vk_video_obj['user_id']
        else:
            author = vk_video_obj['owner_id']
        duration = vk_video_obj['duration']
        is_public = (vk_video_obj.get('is_private') == None)

        return VideoInfo(
            title= title,
            author= author,
            platform= platform,
            duration= duration,
            is_public= is_public,
        )

    @staticmethod
    def download_video(link: str, download_settings: VideoDownloadSettings, video_info: VideoInfo = None) -> str:
        if video_info is None:
            video_info = VideoService.get_video_info(link)

        if video_info.platform == VideoPlatform.VK \
            and download_settings.min_duration <= video_info.duration <= download_settings.max_duration:
            ydl_opts = {
                'format' : 'best',
                'outtmpl': config.BOT_WORK_DIRS['videos'] + f'/{download_settings.file_name}.mp4',
            }
        elif video_info.platform == VideoPlatform.YOUTUBE \
            and download_settings.min_duration <= video_info.duration <= download_settings.max_duration:
            ydl_opts = {
                'format' : 'best',
                'outtmpl': config.BOT_WORK_DIRS['videos'] + f'/{download_settings.file_name}.mp4',
            }
        else:
            return None

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as error:
            raise error

        return f'{download_settings.file_name}.mp4'
