import requests,hashlib,urllib,random,string,re

import threading
import time
import os


RPS = 5
RPS_DELAY = 1 / RPS


class LastRpsRequests:
    def __init__(self, rps) -> None:
        self.rps = rps
        self.request_times = [0] * (rps)
        self.last_rps_request_id = 0
        self.full = False

        # self.last_request_time = 0
        pass

    def can_request(self) -> bool:
        return self.get_delay() == 0.0

    def get_delay(self) -> float:
        if self.full:
            current_time = time.time()
            last_rps_request_time = self.request_times[(self.last_rps_request_id + 1) % self.rps]

            time_diff = current_time - last_rps_request_time
            # print(time_diff)

            return max(0.0, (1 / self.rps) - time_diff)

        return 0.0
        # current_time = time.time()
        # time_diff = current_time - self.last_request_time
        # print(time_diff)

        # return max(0.0, (1 / self.rps + 0.1) - time_diff)

    def timestamp(self) -> None:
        self.request_times[self.last_rps_request_id] = time.time()

        if not self.full and self.last_rps_request_id + 1 == len(self.request_times):
            self.full = True

        self.last_rps_request_id += 1
        self.last_rps_request_id %= len(self.request_times)

        # self.last_request_time = time.time()


class VkAndroidApi(object):
    session = requests.Session()
    session.headers={"User-Agent": "VKAndroidApp/4.13.1-1206 (Android 4.4.3; SDK 19; armeabi; ; ru)","Accept": "image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*"}


    def _get_auth_params(self,login,password):
        return {
            'grant_type':'password',
            'scope':'nohttps,audio',
            'client_id':2274003,
            'client_secret':'hHbZxrka2uZ6jB1inYsH',
            'validate_token':'true',
            'username':login,
            'password':password
        }


    def __init__(self, login=None, password=None, token=None, secret=None, v=5.95):
        self.v=v;
        self.lock = threading.Lock()
        self.last_rps_requests = LastRpsRequests(RPS)

        #Генерируем рандомный device_id
        self.device_id = "".join( random.choice(string.ascii_lowercase+string.digits) for i in range(16))
        if token is not None and secret is not None:
            self.token=token
            self.secret=secret
        else:
            answer =  self.session.get("https://oauth.vk.com/token",params=self._get_auth_params(login, password)).json()
            if("error" in answer): raise PermissionError("invalid login|password!")
            self.secret = answer["secret"]
            self.token = answer["access_token"]

            #Методы, "Открывающие" доступ к аудио. Без них, аудио получить не получится
            self.method('execute.getUserInfo',func_v=9), 
            self.method('auth.refreshToken',lang='ru')


    def method(self,method,**params):
        url =( "/method/{method}?v={v}&access_token={token}&device_id={device_id}".format(method=method, v=self.v, token=self.token, device_id=self.device_id)
            +"".join("&%s=%s"%(i,params[i]) for i in params if params[i] is not None)
        )

        #генерация ссылки по которой будет генерироваться md5-подпись
        #обратите внимание - в даннаой ссылке нет urlencode параметров
        return self._send(url, params, method)


    def _send(self, url, params=None, method=None, headers=None):
        hash = hashlib.md5((url+self.secret).encode()).hexdigest()

        if method is not None and params is not None:
            url = ("/method/{method}?v={v}&access_token={token}&device_id={device_id}".format(method=method, token=self.token, device_id=self.device_id, v=self.v)
                + "".join(
                "&"+i+"="+urllib.parse.quote_plus(str(params[i])) for i in params if(params[i] is not None)
                ))
        
        response = None
        with self.lock:
            time.sleep(self.last_rps_requests.get_delay())
            
            if headers is None:
                response = self.session.get('https://api.vk.com' + url + "&sig=" + hash).json()
            else:
                response = self.session.get('https://api.vk.com' + url + "&sig=" + hash, headers=headers).json()

            self.last_rps_requests.timestamp()
        
        if response.get('error'):
            raise Exception(response.get('error'))
            
        return response
        

    _pattern = re.compile(r'/[a-zA-Z\d]{6,}(/.*?[a-zA-Z\d]+?)/index.m3u8()')


    def to_mp3(self, url):
        return self._pattern.sub(r'\1\2.mp3',url)
