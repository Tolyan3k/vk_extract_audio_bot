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

        # На данный момент возможность не поддерживается библиотекой
        # audio = vk_audio_session.get_by_id(audio_upl_info['ads']['content_id'])[0]
        # if not isinstance(audio, bool) and audio.can_edit:
        #     audio.edit(
        #         artist= audio.artist,
        #         title= audio.title,
        #         text= audio_info.lyrics,
        #     )
        # else:
        #     print("Не удалось добавить текст в аудиозапись")

        return audio_upl_info['ads']['content_id']

    @staticmethod
    def delete_audio(content_id: str) -> None:
        audio = vk_audio_session.get_by_id([content_id])[0]
        if not (isinstance(audio, bool) and audio == False) \
            and audio.can_delete:
            audio.delete()

    @staticmethod
    def add_audio(content_id: str, to: str) -> Optional[str]:
        audio = vk_audio_session.get_by_id([content_id])[0]
        if not (isinstance(audio, bool) and audio == False):
            audio.add(to)
            new_content_id = f"{audio['owner_id']}_{audio['id']}"

            return new_content_id
