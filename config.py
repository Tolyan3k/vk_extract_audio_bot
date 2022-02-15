import os


VK_USER_TOKEN = os.environ['VK_USER_TOKEN']
VK_USER_LOGIN = os.environ['VK_USER_LOGIN']
VK_USER_PASSWORD = os.environ['VK_USER_PASSWORD']
VK_USER_2FA = os.environ['VK_USER_2FA']

VK_ARCHIVE_GROUP_TOKEN = os.environ['VK_ARCHIVE_GROUP_TOKEN']
VK_ARCHIVE_GROUP_ID = os.environ['VK_ARCHIVE_GROUP_ID']

VK_MAIN_GROUP_TOKEN = os.environ['VK_MAIN_GROUP_TOKEN']
VK_MAIN_GROUP_ID = os.environ['VK_MAIN_GROUP_ID']

MONGODB_URI = os.environ['MONGODB_URI']

BOT_DIR = os.environ['PYTHONPATH']
DIRS = {
    'videos': BOT_DIR + '/temp/videos',
    'audios': BOT_DIR + '/temp/audios'
}


VIDEO_MIN_DURATION = 0
VIDEO_MAX_DURATION = 600

AUDIO_MIN_DURATION = 5


VK_MAX_ATTACHMENTS = 10
