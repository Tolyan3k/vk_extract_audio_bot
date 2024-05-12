# ruff: noqa: ERA001

from vk_extract_audio_bot.utils.downloader import VideoInfo


VIDEO_URLS_SUPPORTS_ONLY_AUDIO = [
    # youtube
    "https://www.youtube.com/watch?v=cdBK0-9gsFA",    # fun
    "https://www.youtube.com/watch?v=mwKJfNYwvm8",    # MR BEEEEEAAAAAST!
    "https://www.youtube.com/watch?v=PXcvxCBNfmo",    # Unapropriate content
    "https://www.youtube.com/watch?v=7Graxjlewio",    # suicide content
    "https://www.youtube.com/watch?v=yaGYT_mhNWg",    # music video
    # same music video but from public playlist: not work because of 3rd party
    # "https://youtu.be/yaGYT_mhNWg?list=PLEOxAKm2kVX0Uc9gUVlJpFYymdJB0xw74",
    # from private plalist
    "https://youtu.be/on22V_2Zno0?list=PLEOxAKm2kVX1c7bzmDF51QpZ9i6b4VE4M",
]
"""Видео, у которых аудио можно скачать отдельно от видео."""

VIDEO_URLS_SUPPORTS_ONLY_AUDIO_WITH_VINFO = [
    (
        "https://www.youtube.com/watch?v=yaGYT_mhNWg",
        VideoInfo(
            url="https://www.youtube.com/watch?v=yaGYT_mhNWg",
            video_id="yaGYT_mhNWg",
            extractor="youtube",
            formats=[],
            author="NEEDY GIRL OVERDOSE - Topic",
            title="INTERNET ANGEL (feat. Aiobahn)",
            duration=60.0,
        ),
    ),
    (
        "https://www.youtube.com/watch?v=cdBK0-9gsFA",
        VideoInfo(
            url="https://www.youtube.com/watch?v=cdBK0-9gsFA",
            video_id="cdBK0-9gsFA",
            extractor="youtube",
            formats=[],
            author="зевака",
            title="Роман Трахтенберг. Про Пuсюна, Дусю и Розелло",
            duration=602.0,
        ),
    ),
    (
        "https://www.youtube.com/watch?v=PXcvxCBNfmo",
        VideoInfo(
            url="https://www.youtube.com/watch?v=PXcvxCBNfmo",
            video_id="PXcvxCBNfmo",
            extractor="youtube",
            formats=[],
            author="FlynnFlyTaggart",
            title="Ужасы Фетиш-Каналов Ютуба. VOL. 2",
            duration=1536.0,
        ),
    ),
    (
        "https://www.youtube.com/watch?v=7Graxjlewio",
        VideoInfo(
            url="https://www.youtube.com/watch?v=7Graxjlewio",
            video_id="7Graxjlewio",
            extractor="youtube",
            formats=[],
            author="да я баклажан и чё",
            title="доктор я хочу покончить с собой",
            duration=16.0,
        ),
    ),
    (
        "https://www.youtube.com/watch?v=mwKJfNYwvm8",
        VideoInfo(
            url="https://www.youtube.com/watch?v=mwKJfNYwvm8",
            video_id="mwKJfNYwvm8",
            extractor="youtube",
            formats=[],
            author="MrBeast",
            title="I Built 100 Wells In Africa",
            duration=629.0,
        ),
    ),
    (
        "https://youtu.be/on22V_2Zno0?list=PLEOxAKm2kVX1c7bzmDF51QpZ9i6b4VE4M",
        VideoInfo(
            url="https://youtu.be/on22V_2Zno0?list=PLEOxAKm2kVX1c7bzmDF51QpZ9i6b4VE4M",
            video_id="on22V_2Zno0",
            extractor="youtube",
            formats=[],
            author="각설탕위참깨nawrk3",
            title="미유",
            duration=4.0,
        ),
    ),
]
"""Видео, у которых аудио можно скачать отдельно от видео."""

VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO = [
    # vk
    "https://vk.com/video202745946_456239031?list=5741411ffee8b2bea4",    # from public playlist
    "https://vk.com/video-202888637_456246039",    # random video from [RaveDJ]
    "https://vk.com/video-67535637_456239212",    # .vkuser.net
    # rutube
    "https://rutube.ru/video/e7929fa8fe0baeff21688ef498c142a4/",    # random video
]
"""Видео, у которых аудио есть только в составе контейнера с видео."""

VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO_WITH_VINFO = [
    (
        "https://rutube.ru/video/e7929fa8fe0baeff21688ef498c142a4/",
        VideoInfo(
            url="https://rutube.ru/video/e7929fa8fe0baeff21688ef498c142a4/",
            video_id="e7929fa8fe0baeff21688ef498c142a4",
            extractor="rutube",
            formats=[],
            author="nari_man007",
            title="САМЫЙ КРУТОЙ ОТЕЛЬ В ЧЕБОКСАРАХ",
            duration=313.0,
        ),
    ),
    (
        "https://vk.com/video202745946_456239031?list=5741411ffee8b2bea4",
        VideoInfo(
            url="https://vk.com/video202745946_456239031?list=5741411ffee8b2bea4",
            video_id="202745946_456239031",
            extractor="vk",
            formats=[],
            author="Arsen Dolapov",
            title="WELCOME TO THE RICE FIELDS MOTHERFUCKER",
            duration=2.0,
        ),
    ),
    (
        "https://vk.com/video-67535637_456239212",
        VideoInfo(
            url="https://vk.com/video-67535637_456239212",
            video_id="-67535637_456239212",
            extractor="vk",
            formats=[],
            author="Симпсоны, Южный парк, Футурама, Рик и Морти",
            title="СИМПСОНЫ - Лучшие Моменты (Назад В Будущее)",
            duration=563.0,
        ),
    ),
    (
        "https://vk.com/video-202888637_456246039",
        VideoInfo(
            url="https://vk.com/video-202888637_456246039",
            video_id="-202888637_456246039",
            extractor="vk",
            formats=[],
            author="Vladislav Glukhikh",
            title="а может я ядерный? а может я дикий? ??",
            duration=253.0,
        ),
    ),
]
"""Видео, у которых аудио есть только в составе контейнера с видео."""

VIDEO_URLS_WITHOUT_AUDIO = [
    # vk
    "https://vk.com/video-69296730_456255345",
]
"""Видео, у которых в составе контейнера нет аудио дорожки."""

VIDEO_URLS_UNITED = [
    *VIDEO_URLS_SUPPORTS_ONLY_AUDIO, *VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO,
]
"""Все видео кроме `VIDEO_URLS_WITHOUT_AUDIO`"""

VIDEOS_WITH_VINFO_UNITED = [
    *VIDEO_URLS_SUPPORTS_ONLY_AUDIO_WITH_VINFO,
    *VIDEO_URLS_NOT_SUPPORTS_ONLY_AUDIO_WITH_VINFO,
]
