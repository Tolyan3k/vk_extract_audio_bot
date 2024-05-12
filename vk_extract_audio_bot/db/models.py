from typing import Optional

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
)


class VideoBase(SQLModel):
    owner_id: int
    video_id: int


class VideoCreate(VideoBase):
    pass


class Video(VideoBase, table=True):
    id: int = Field(
        default=None, primary_key=True,
    )

    audio: Optional["Audio"] = Relationship(
        back_populates="video",
    )


class AudioBase(SQLModel):
    owner_id: int
    audio_id: int


class AudioCreate(AudioBase):
    pass


class Audio(AudioBase, table=True):
    id: int = Field(
        default=None, primary_key=True,
    )

    video_id: int | None = Field(
        default=None, foreign_key="video.id",
    )
    video: Optional["Video"] = Relationship(
        back_populates="audio",
    )


__all__ = ["Video", "VideoCreate", "Audio", "AudioCreate"]
