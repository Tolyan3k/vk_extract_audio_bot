from sqlmodel import select

from vk_extract_audio_bot.db.db import (
    get_session,
)
from vk_extract_audio_bot.db.models import (
    Audio,
    AudioCreate,
    Video,
    VideoCreate,
)


class Videos:

    @staticmethod
    def create(
        video: VideoCreate,
    ) -> Video:
        video = Video.model_validate(video)
        with get_session() as s:
            s.add(video)
            s.commit()
            s.refresh(video)
            return video

    @staticmethod
    def get(video_id: int) -> Video:
        with get_session() as s:
            return s.get_one(Video, video_id)

    @staticmethod
    def find_with(owner_id: int, video_id: int) -> Video | None:
        with get_session() as s:
            return s.exec(
                select(Video).where(
                    Video.owner_id == owner_id,
                    Video.video_id == video_id,
                ),
            ).one_or_none()

    @staticmethod
    def find_audio(
        video_id: int,
    ) -> Audio | None:
        select_audio = select(Audio).where(Audio.video_id == video_id)
        with get_session() as s:
            return s.exec(select_audio).one_or_none()

    @staticmethod
    def set_audio(video_id: int, audio_id: int) -> Video:
        with get_session() as s:
            video = s.get_one(Video, video_id)
            audio = s.get_one(Audio, audio_id)
            video.audio = audio
            s.add(video)
            s.commit()
            s.refresh(video)
            return video


class Audios:

    @staticmethod
    def create(
        audio: AudioCreate,
    ) -> Audio:
        audio = Audio.model_validate(audio)
        with get_session() as s:
            s.add(audio)
            s.commit()
            s.refresh(audio)
            return audio

    @staticmethod
    def get(audio_id: int) -> Audio:
        with get_session() as s:
            return s.get_one(Video, audio_id)

    @staticmethod
    def set_video(video_id: int, audio_id: int) -> Video:
        with get_session() as s:
            video = s.get_one(Video, video_id)
            audio = s.get_one(Audio, audio_id)
            video.audio = audio
            s.add(video)
            s.commit()
            s.refresh(video)
            return video


__all__ = ["Videos", "Audios"]
