import pytest

from pydantic import DirectoryPath, FilePath
import pathvalidate
import pathlib
import shutil
import os

from services.extractor import AudioExtractor, AudioFile
from services.extra import File


TEST_DIR = DirectoryPath('./tests/.temp')
shutil.rmtree(TEST_DIR, ignore_errors=True)
TEST_DIR.mkdir(exist_ok=True)

VK_URLS = [
    'https://vk.com/video202745946_456239031?list=5741411ffee8b2bea4',
]

YT_URLS = [
    # 'https://youtu.be/5jfPeClZF8M',
    # 'https://www.youtube.com/watch?v=mwKJfNYwvm800', # multiple dub tracks
    # 'https://www.youtube.com/watch?v=Do5_wU9X1pc&t=15s', # no age restrictions
    'https://www.youtube.com/watch?v=cdBK0-9gsFA',
    'https://www.youtube.com/watch?v=mwKJfNYwvm8',
    'https://www.youtube.com/watch?v=biYFsy1s2t0',
]

RT_URLS = [
    'https://rutube.ru/video/e7929fa8fe0baeff21688ef498c142a4/',
]

ALL_URLS = [
    *VK_URLS,
    *YT_URLS,
    *RT_URLS,
]


class Test_Extractor:
    def test_free_pass(cls):
        pass
    
    class Test_Url:
        def test_extract_audio(cls):
            for url in ALL_URLS:
                temp = File(dirpath=TEST_DIR, filename=f'video_{pathvalidate.sanitize_filename(url)}')
                to = File(dirpath=TEST_DIR, filename=f'audio_{pathvalidate.sanitize_filename(url)}.mp3')
                af = AudioExtractor.extract_from_url(url, temp, to)
                assert af.audiofile.as_filepath().exists()
                os.remove(af.audiofile.get_str())
