import pyotp
import vkaudiotoken
from dotenv import find_dotenv, set_key
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
)
from vk_api import VkApi
from vkwave.api import API
from vkwave.api.token.token import (
    BotSyncSingleToken,
    UserSyncSingleToken,
)

from .settings import CONFIG
from .utils.vk.android import (
    VkAndroidApi,
)
from .utils.vk.audios import VkAudios


@retry(
    wait=wait_fixed(1), stop=stop_after_attempt(3),
)
def get_vk_audio_token() -> str:
    return vkaudiotoken.get_vk_official_token(
        CONFIG.VK_USER_LOGIN,
        CONFIG.VK_USER_PASSWORD,
        pyotp.TOTP(CONFIG.VK_USER_2FA).now(),
    )["token"]


if CONFIG.vk_audio_client_token is None:
    env_file = find_dotenv()
    CONFIG.vk_audio_client_token = get_vk_audio_token()
    set_key(
        env_file,
        "VK_AUDIO_CLIENT_TOKEN",
        CONFIG.vk_audio_client_token,
    )

vk_android_api = VkAndroidApi(
    token=CONFIG.vk_audio_client_token, secret=CONFIG.VK_AUDIO_CLIENT_SECRET,
)

vk_user_api = VkApi(token=CONFIG.VK_USER_TOKEN)
vk_main_group_api = VkApi(token=CONFIG.VK_MAIN_GROUP_TOKEN)
vk_archive_group_api = VkApi(token=CONFIG.VK_ARCHIVE_GROUP_TOKEN)
vk_audio_api: VkAudios = VkAudios(vk_android_api, vk_user_api)

USER_API = API([UserSyncSingleToken(CONFIG.VK_USER_TOKEN)])
MAIN_GROUP_API = API([BotSyncSingleToken(CONFIG.VK_MAIN_GROUP_TOKEN)])
ARCHIVE_GROUP_API = API([BotSyncSingleToken(CONFIG.VK_ARCHIVE_GROUP_TOKEN)])
VK_AUDIO_API = vk_audio_api
