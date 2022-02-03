from vk_api.bot_longpoll import VkBotLongPoll
from vk_api import VkApi
from vk_audio import *
import pymongo
import pyotp
import os

from bot_types.MongoVariable import MongoVariable
import config


def auth_handler():
    return pyotp.TOTP(config.VK_USER_2FA).now(), True


for dir in config.DIRS.values():
    os.makedirs(dir, exist_ok=True)

vk_user_session = VkApi(token=config.VK_USER_TOKEN)

vk_cred_session = VkApi(
    login=config.VK_USER_LOGIN, 
    password=config.VK_USER_PASSWORD, 
    auth_handler=auth_handler
)
vk_cred_session.auth()
vk_audio_session = VkAudio(vk_cred_session)

vk_archive_group_api_session = VkApi(token=config.VK_ARCHIVE_GROUP_TOKEN)
vk_main_group_api_session = VkApi(token=config.VK_MAIN_GROUP_TOKEN)

vk_bot_longpoll = VkBotLongPoll(vk_main_group_api_session, config.VK_MAIN_GROUP_ID)

last_answered_msg_id = MongoVariable(
    mongo_client=pymongo.MongoClient(config.MONGODB_URI, connect=True),
    database_name='main',
    collection_name='env',
    object_id='61f19338336dd428c6492db6',
    var_name='last_answered_message_id'
)