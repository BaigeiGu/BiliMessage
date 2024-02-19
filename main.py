import json
import logging
import os
import time
from urllib.parse import urlparse

import requests
import schedule

import BiliApi
import WindowsToast
from config import *
from init import init

if not os.path.exists(DATA_PATH):
    init()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
)

Bili = BiliApi.BiliApi(COOKIE=COOKIES)

UserListFile = open(f'{DATA_PATH}/userlist.json', mode='r', encoding='UTF-8')

UserList = json.loads(UserListFile.read())
UserListFile.close()


def download_user_avatar(talker_id, picurl):
    with open(f'{DATA_PATH}/images/{talker_id}.png', mode='wb') as f:
        r = requests.get(picurl)
        f.write(r.content)


def updateMsgList(talker_id, last_msg_timestamp):
    UserList[talker_id]['last_msg_timestamp'] = last_msg_timestamp

    UserListFile = open(f'{DATA_PATH}/userlist.json',
                        mode='w',
                        encoding='UTF-8')
    UserListFile.write(json.dumps(UserList, ensure_ascii=False))
    UserListFile.close()


def updateUserList(talker_id,
                   last_msg_timestamp: int | None = None,
                   sysinfo: tuple | None = None):
    # sysinfo:tuple (name:str,picurl:str)

    if sysinfo == None:
        userInfo = Bili.getUserInfo(user_mid=talker_id)
        picurl = userInfo['card']['face']
        name = userInfo['card']['name']
    else:
        name, picurl = sysinfo

    pic_filepath = urlparse(picurl).path
    pic_name = os.path.basename(pic_filepath)

    if talker_id in UserList.keys():
        # 若已经录入过此用户
        if pic_name != UserList[talker_id]['avartar_file_name']:
            # 若头像有更新 则重新下载
            download_user_avatar(talker_id=talker_id, picurl=picurl)

        if last_msg_timestamp == None:
            # 若未传入新的消息时间 取上一条消息时间
            last_msg_timestamp = UserList[talker_id]['last_msg_timestamp']
    else:
        download_user_avatar(talker_id=talker_id, picurl=picurl)


    userData = {
        'name': name,
        'last_msg_timestamp': last_msg_timestamp,
        'avartar_file_name': pic_name,
        'last_avatar_timestamp': int(time.time()*1000000)
    }

    UserList[talker_id] = userData

    UserListFile = open(f'{DATA_PATH}/userlist.json',
                        mode='w',
                        encoding='UTF-8')
    UserListFile.write(json.dumps(UserList, ensure_ascii=False))
    UserListFile.close()


def newMessage(item):
    last_msg_timestamp = item['session_ts']
    talker_id = str(item['talker_id'])

    last_msg = item['last_msg']
    if last_msg['content'] == None:
        last_msg_content = None
    else:
        last_msg_content = json.loads(last_msg['content'])

    if not 'account_info' in item.keys():
        if not talker_id in UserList.keys():
            # 首次收到消息 添加用户
            updateUserList(talker_id=talker_id,
                           last_msg_timestamp=last_msg_timestamp)
        if (UserList[talker_id]['last_avatar_timestamp'] -
                int(time.time()*1000000)) >= AVATAR_TIMEOUT*1000000:
            # 头像超时后更新头像
            updateUserList(talker_id=talker_id)
    else:
        # 系统消息
        updateUserList(talker_id=talker_id,
                       last_msg_timestamp=last_msg_timestamp,
                       sysinfo=(item['account_info']['name'],
                                item['account_info']['pic_url']))

    updateMsgList(talker_id, last_msg_timestamp)

    if 'content' in last_msg_content.keys() and str(
            last_msg['sender_uid']) == talker_id:
        sender_name = UserList[talker_id]['name']
        msg_content = last_msg_content['content']
        logging.info(f'收到来自{sender_name}的消息：{msg_content}')
        WindowsToast.send_toast_with_icon(
            title='哔哩哔哩消息',
            text=[sender_name, msg_content],
            imgPath=f'{DATA_PATH}/images/{talker_id}.png',
            jumpto='https://message.bilibili.com/#/whisper/')


def getLatestMessage():
    logging.info('已获取最新消息列表')

    newMessage_flag = False
    msgList = Bili.getMessageList()['session_list']
    for item in msgList:
        last_msg_timestamp = item['session_ts']
        talker_id = str(item['talker_id'])

        if not talker_id in UserList.keys():
            newMessage_flag = True
            newMessage(item)

        elif int(last_msg_timestamp
                 ) > UserList[talker_id]['last_msg_timestamp']:
            newMessage_flag = True
            newMessage(item)

    if newMessage_flag == False:
        logging.info('无新消息')


schedule.every(30).seconds.do(getLatestMessage)
logging.info('Started')
getLatestMessage()

while True:
    schedule.run_pending()
    time.sleep(1)
