from typing import Optional
from vk_api import VkApi

import __init__

class VkMesasgeService:
    @staticmethod
    def get_message_by_id(vk_session: VkApi, msg_id) -> Optional[dict]:
        msg_data = vk_session.get_api().messages.getById(message_ids=msg_id)
        if msg_data['count'] == 1:
            return msg_data['items'][0]

    @staticmethod
    def get_videos_from_message(vk_msg: dict) -> list:
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
