from vk_api.upload import VkUpload
from typing import Optional

from bot_types.AudioInfo import AudioInfo
from __init__ import *

class VkAudioService(object):
    @staticmethod
    def upload_audio(audio_path: str, audio_info: AudioInfo) -> str:
        audio_upl_info = VkUpload(vk_user_session).audio(
            audio=audio_path,
            artist=audio_info.artist,
            title=audio_info.title
        )

        return audio_upl_info['ads']['content_id']

    @staticmethod
    def delete_audio(content_id: str) -> None:
        vk_audio_api.method('audio.delete',
            owner_id=content_id.split('_')[0],
            audio_id=content_id.split('_')[1]
        )
        # audio = vk_audio_session.get_by_id([content_id])[0]
        # if not (isinstance(audio, bool) and audio == False) \
        #     and audio.can_delete:
        #     audio.delete()

    @staticmethod
    def add_audio(content_id: str, to: str = '') -> Optional[str]:
        new_content_id = None
        
        if (to != ''):
            result = vk_audio_api.method('audio.add',
                owner_id=content_id.split('_')[0],
                audio_id=content_id.split('_')[1],
                group_id=to,
            )
        else:
            result = vk_audio_api.method('audio.add',
                owner_id=content_id.split('_')[0],
                audio_id=content_id.split('_')[1],
            )

        if len(result) == 1:
            new_content_id = result['response']

        # audio = vk_audio_session.get_by_id([content_id])[0]
        # if not (isinstance(audio, bool) and audio == False):
        #     audio.add(to)
        #     new_content_id = f"{audio['owner_id']}_{audio['id']}"

        return new_content_id


    # @staticmethod
    # def set_public_search_visibility(audio_content_id: str, visibility: bool):
    #     result = vk_audio_api.method('audio.edit',
    #         owner_id=audio_content_id.split('_')[0],
    #         audio_id=audio_content_id.split('_')[1],
    #         no_search= 0 if visibility else 1,
    #         text= audio_text,
    #     )['response']

    #     return result

    @staticmethod
    def edit_audio(audio_content_id: str, new_text: str, search_visibility: bool):
        result = vk_audio_api.method('audio.edit',
            owner_id=audio_content_id.split('_')[0],
            audio_id=audio_content_id.split('_')[1],
            no_search= 0 if search_visibility else 1,
            text= new_text,
        )['response']

        return result
