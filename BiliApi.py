import requests
import WBISign


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
        # cookie = {'SESSDATA': self.SESSDATA}
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
            raise ApiError

    def getUserInfo(self, user_mid: int, photo: bool = False) -> dict:
        # https://api.bilibili.com/x/web-interface/card?mid={mid}&photo={photo}
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
        # https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&mobi_app=web
        res = self.send_request(
            url=
            f'https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions',
            params={
                'session_type': session_type,
                'mobi_app': 'web'
            })
        return res

    def getMessageSession(self, user_mid: int, user_type: int = 1) -> dict:
        # https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id=527094915&session_type=1
        res = self.send_request(
            url=
            f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs',
            params={
                'talker_id': user_mid,
                'session_type': user_type
            })
        return res
