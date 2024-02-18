import json
import os
import time

import requests
import schedule
import logging

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

MsgListFile = open(f'{DATA_PATH}/msglist.json', mode='r', encoding='UTF-8')
UserListFile = open(f'{DATA_PATH}/userlist.json', mode='r', encoding='UTF-8')

MsgList = json.loads(MsgListFile.read())
MsgListFile.close()
UserList = json.loads(UserListFile.read())
UserListFile.close()


def updateMsgList():
    MsgListFile = open(f'{DATA_PATH}/msglist.json',
                       mode='w+',
                       encoding='UTF-8')
    MsgListFile.write(json.dumps(MsgList))
    MsgListFile.close()


def updateUserList(talker_id, last_msg_timestamp):
    userInfo = Bili.getUserInfo(user_mid=talker_id)
    userData = {
        'name': userInfo['card']['name'],
        'last_msg_timestamp': last_msg_timestamp
    }
    UserList[talker_id] = userData

    UserListFile = open(f'{DATA_PATH}/userlist.json',
                        mode='w',
                        encoding='UTF-8')
    UserListFile.write(json.dumps(UserList, ensure_ascii=False))
    UserListFile.close()

    with open(f'{DATA_PATH}/images/{talker_id}.png', mode='bw') as f:
        r = requests.get(userInfo['card']['face'])
        f.write(r.content)


def updateUserList_SysMsg(talker_id, name, picurl, last_msg_timestamp):
    userData = {'name': name, 'last_msg_timestamp': last_msg_timestamp}
    UserList[talker_id] = userData

    UserListFile = open(f'{DATA_PATH}/userlist.json',
                        mode='w+',
                        encoding='UTF-8')
    UserListFile.write(json.dumps(UserList))
    UserListFile.close()

    with open(f'{DATA_PATH}/images/{talker_id}.png', mode='bw') as f:
        r = requests.get(picurl)
        f.write(r.content)


def newMessage(item):
    last_msg_timestamp = item['session_ts']
    talker_id = str(item['talker_id'])

    MsgList[talker_id] = int(last_msg_timestamp)
    updateMsgList()

    last_msg = item['last_msg']
    if last_msg['content'] == None:
        last_msg_content = None
    else:
        last_msg_content = json.loads(last_msg['content'])

    if not talker_id in UserList.keys():
        if not 'account_info' in item.keys():
            updateUserList(talker_id=talker_id,
                           last_msg_timestamp=last_msg_timestamp)
        else:
            updateUserList_SysMsg(talker_id=talker_id,
                                  name=item['account_info']['name'],
                                  picurl=item['account_info']['pic_url'],
                                  last_msg_timestamp=last_msg_timestamp)

    if 'content' in last_msg_content.keys() and str(last_msg['sender_uid']) == talker_id:
        sender_name = UserList[talker_id]['name']
        msg_content = last_msg_content['content']
        logging.info(f'收到来自{sender_name}的消息：{msg_content}')
        WindowsToast.send_toast_with_icon(
            title='哔哩哔哩消息',
            text=[sender_name, msg_content],
            imgPath=f'{DATA_PATH}/images/{talker_id}.png',
            jumpto='https://message.bilibili.com/#/whisper/')


def getLatestMessage():
    logging.debug('已获取最新信息列表')
    msgList = Bili.getMessageList()['session_list']
    for item in msgList:
        last_msg_timestamp = item['session_ts']
        talker_id = str(item['talker_id'])

        if talker_id in MsgList.keys():
            if int(last_msg_timestamp) > MsgList[talker_id]:
                newMessage(item)
        else:
            MsgList[talker_id] = {}
            MsgList[talker_id]['last_msg_timestamp'] = int(last_msg_timestamp)
            newMessage(item)


# getLatestMessage()d

schedule.every(30).seconds.do(getLatestMessage)
logging.info('Started')
while True:
    schedule.run_pending()
    time.sleep(1)
