from enum import IntEnum, auto
from pathlib import Path
import shutil
import os

from pydantic import BaseModel, DirectoryPath, AnyUrl, FilePath
from .downloader import DownloadedFile, Downloader
from moviepy.editor import VideoFileClip
import ffmpeg

from .extra import File


class AudioFile(BaseModel):
    original: DownloadedFile
    audiofile: File


class ExtractorOptions(BaseModel):
    bitrate: int
    hz: int
    max_size: int
    # ext: AudioFileExtension = AudioFileExtension.MP3


class AudioExtractor:
    @staticmethod
    def extract_from_url(url: AnyUrl, temp: File, to: File) -> AudioFile:
        if temp == to:
            ValueError('Temp file path and target file path must differ')
        any_f = Downloader.download_any(url, temp, DownloadedFile.Type.AUDIO)
        aud_f = AudioExtractor.extract_from_file(any_f, to)
        os.remove(temp.get_str())
        return aud_f
    
    @staticmethod
    def extract_from_file(f: DownloadedFile, to: File) -> AudioFile:
        if f.filepath == to:
            raise ValueError('Downloaded file path and target file path must have differents paths')
        if f.filetype == DownloadedFile.Type.AUDIO:
            if f.filepath != to:
                shutil.copyfile(f.filepath.get_str(), to.get_str())
        else: # VIDEO
            AudioExtractor._extract_audio(f.filepath, to)
        return AudioFile(original=f, audiofile=to)
        
    
    @staticmethod
    def _has_audio(file: File) -> bool:
        probe = ffmpeg.probe(file.get_str())
        if 'streams' in probe:
            for stream in probe['streams']:
                if stream['codec_type'] == 'audio':
                    return True
        return False
    
    @staticmethod
    def _extract_audio(vid_f: File, to: File, opts = None) -> None:
        v_clip = VideoFileClip(vid_f.get_str())
        a_clip = v_clip.audio
        a_clip.write_audiofile(to.get_str())
        v_clip.close()
        a_clip.close()
        return to
