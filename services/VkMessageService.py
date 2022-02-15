from typing import Optional

from vk_api import VkApi

from bot_types.VideoPlatform import \
    VIDEO_PATTERNS_COMPILED_FULL, VIDEO_PATTERNS_COMPILED, VIDEO_PATTERNS_COMPILED_WITH_PLATFORMS
from bot_types.VkVideoPlatform import VkVideoPlatform, video_platform_to_vk_video_platform
import __init__


class VkMesasgeService:
    @staticmethod
    def get_message_by_id(vk_session: VkApi, msg_id) -> Optional[dict]:
        msg_data = vk_session.get_api().messages.getById(message_ids=msg_id)
        if msg_data['count'] == 1:
            return msg_data['items'][0]

    @staticmethod
    def get_video_attachments_from_message(vk_msg: dict) -> list:
        videos = []

        def iter_find_video(vk_msg: dict):
            for key in vk_msg.keys():
                if key == 'video':
                    videos.append(vk_msg[key])
                elif isinstance(vk_msg[key], dict):
                    iter_find_video(vk_msg[key])
                elif isinstance(vk_msg[key], list):
                    for list_elem in vk_msg[key]:
                        iter_find_video(list_elem)
        iter_find_video(vk_msg)
        
        return videos

    @staticmethod
    def get_video_links_from_text(vk_msg: dict) -> list[dict]:
        video_links = []

        for video_link_match in VIDEO_PATTERNS_COMPILED_FULL.finditer(vk_msg['text']):
            for video_pattern_compiled in VIDEO_PATTERNS_COMPILED_WITH_PLATFORMS:
                if (temp := video_pattern_compiled[0].match(video_link_match.string)):
                    video_link = {}
                    for group in temp:
                        video_link.setdefault(group, temp.group(group))
                    video_link.setdefault('platform', video_platform_to_vk_video_platform(video_pattern_compiled[1]))
                    video_links.append(video_link)
                    break

        return video_links
