import requests
import WBISign
import logging

class ApiError(RuntimeError):
    def __init__(self, arg=None):
        try:
            self.args = arg
        except:
            pass


class BiliApi:
    USERAGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'

    def __init__(self, COOKIE, USERAGENT=USERAGENT) -> None:
        self.USERAGENT = USERAGENT
        self.COOKIE = COOKIE

    def send_request(self,
                     url: str,
                     method: str = 'GET',
                     params: dict = None) -> dict:
        header = {'user-agent': self.USERAGENT, 'Cookie': self.COOKIE}
        match method:
            case 'GET':
                r = requests.get(
                    url,
                    params=params,
                    headers=header,
                )

        res = r.json()

        if res['code'] == 0:
            return res['data']
        else:
            logging.error(res['code'])
            logging.error(res['message'])
            raise ApiError(res['code'], res['message'])

    def getUserInfo(self, user_mid: int, photo: bool = False) -> dict:
        # https://api.bilibili.com/x/web-interface/card
        # user_mid 用户mid
        # photo 是否需要用户页头图
        params = WBISign.WBI({
            'mid': user_mid,
            'photo': photo,
        })
        res = self.send_request(
            url=f'https://api.bilibili.com/x/web-interface/card',
            params=params)
        return res

    def getMessageList(self, session_type: int = 1) -> dict:
        # https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions
        res = self.send_request(
            url=
            f'https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions',
            params={
                'session_type': session_type,
                'mobi_app': 'web'
            })
        return res

    def getMessageSession(self, user_mid: int, user_type: int = 1) -> dict:
        # https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs
        res = self.send_request(
            url=
            f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs',
            params={
                'talker_id': user_mid,
                'session_type': user_type
            })
        return res
