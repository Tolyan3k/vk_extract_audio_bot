import pytest

from pydantic import NewPath, DirectoryPath
from services.extra import File
from loguru import logger
import shutil
import os

TEST_DIR = DirectoryPath('./tests/.temp')
shutil.rmtree(TEST_DIR, ignore_errors=True)
TEST_DIR.mkdir(exist_ok=True)

def create_and_delete_file(filepath: str):
    np = NewPath(filepath)
    np.touch()
    os.remove(np)
    
class Test_File:
    def test_nop(cls):
        pass
    
    def test_filename_with_spaces(cls):
        f = File(dirpath='', filename='some file.txt')
        create_and_delete_file(f.get_str())
            
    def test_valid_file(cls):
        f = File(dirpath='', filename='good_file_name.txt')
        create_and_delete_file(f.get_str())
        
    def test_empty_filename(cls):
        with pytest.raises(Exception) as err:
            f = File(dirpath='.', filename='')
    
    def test_not_exisiting_dirpath(cls):
        with pytest.raises(Exception) as err:
            f = File(dirpath='not-existsing-dirpath', filename='filename')
            
    def test_filepath_points_to_dir(cls):
        with pytest.raises(Exception) as err:
            f = File(dirpath='tests', filename='.temp')
            
    def test_filename_deprecated_chars(cls):
        with pytest.raises(Exception) as err:
            f = File(dirpath='', filename='!@#$%^&*()?_.txt')

    def test_filename_has_dir(cls):
        with pytest.raises(Exception) as err:
            f = File(dirpath='', filename='tests/file.txt')
            
    def test_change_valid_filename_to_another(cls):
        f = File(dirpath='', filename='valid filename')
        # with pytest.raises(Exception) as err:
        f.filename = 'another valid filename'
    
    def test_change_valid_dirpath_to_another(cls):
        f = File(dirpath='', filename='filename')
        f.dirpath = './tests'
        
    def test_change_valid_dirpath_to_invalid(cls):
        f = File(dirpath='', filename='filename')
        with pytest.raises(Exception) as err:
            f.dirpath = '!@#$%^&*()?_.txt'
        
    def test_change_valid_filename_to_invalid(cls):
        f = File(dirpath='', filename='valid filename')
        with pytest.raises(Exception) as err:
            f.filename = '!@#$%^&*()?_.txt'
            
    def test_str_eq_get_str(cls):
        f = File(dirpath='', filename='filename')
        assert f'{f}' == f.get_str()
        
    def test_filepath_on_not_existing_file(cls):
        f = File(dirpath='', filename='filename')
        f.as_filepath()
            
    def test_filepath_on_existing_file(cls):
        f = File(dirpath='', filename='filename')
        np = NewPath(f'{f}')
        np.touch()
        f.as_filepath()
        os.remove(f'{np}')
        