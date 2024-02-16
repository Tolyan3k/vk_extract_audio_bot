import pytest
import pathvalidate
from pydantic import NewPath, FilePath, DirectoryPath

import shutil
import pathlib
import os

from services.extra import File
from services.downloader import Downloader, DownloadedFile


TEST_DIR = './tests/.temp'
test_dir = DirectoryPath(TEST_DIR)
shutil.rmtree(test_dir, ignore_errors=True)
test_dir.mkdir()

PUBLIC_URLS = [
    # 'https://youtu.be/5jfPeClZF8M',
    # 'https://www.youtube.com/watch?v=mwKJfNYwvm800', # multiple dub tracks
    # 'https://www.youtube.com/watch?v=Do5_wU9X1pc&t=15s',
    'https://www.youtube.com/watch?v=cdBK0-9gsFA',
    'https://www.youtube.com/watch?v=mwKJfNYwvm8',
    'https://www.youtube.com/watch?v=biYFsy1s2t0',
]

def is_exists_and_file(filepath: File):
    np = NewPath(f'{filepath}')
    return np.exists() and np.is_file()

class Test_YT:
    def test_nop(cls):
        pass
    
    class Test_VideoInfo:
        def test_get_info_works(cls):
            for url in PUBLIC_URLS:
                info = Downloader.get_video_info(url)
    
    class Test_Links:
        class Test_DownloadOnlyVideo:
            def test_downloads(cls):
                for url in PUBLIC_URLS:
                    to = File(dirpath=TEST_DIR, filename=pathvalidate.sanitize_filename(url))
                    dlf = Downloader.download_video(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())
            
            def test_is_real_video(cls):
                pass
                        
        class Test_DownloadOnlyAudio:
            def test_downloads(cls):
                for url in PUBLIC_URLS:
                    to = File(dirpath=TEST_DIR, filename=pathvalidate.sanitize_filename(url))
                    dlf = Downloader.download_audio(url, to)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())
            
            def test_is_real_audio(cls):
                pass
            
        class Test_DownloadAny:
            def test_first_audio(cls):
                """must be only audio
                """
                for url in PUBLIC_URLS:
                    to = File(dirpath=TEST_DIR, filename=pathvalidate.sanitize_filename(url))
                    dlf = Downloader.download_any(url, to, DownloadedFile.Type.AUDIO)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())
            
            def test_first_video(cls):
                """must be only video
                """
                for url in PUBLIC_URLS:
                    to = File(dirpath=TEST_DIR, filename=pathvalidate.sanitize_filename(url))
                    dlf = Downloader.download_any(url, to, DownloadedFile.Type.VIDEO)
                    assert is_exists_and_file(dlf.filepath)
                    os.remove(dlf.filepath.get_str())
