import os
import sqlite3

import config


def init():
    if not os.path.exists(config.DATA_PATH):
        print("Data path doesn't exists.")
        print(f"Will make dir:{config.DATA_PATH}")
        os.mkdir(config.DATA_PATH)
        os.mkdir(config.DATA_PATH + '/images')
        open(config.DATA_PATH + '/msglist.json', mode='w+',
             encoding='UTF-8').write('{}')
        open(config.DATA_PATH + '/userlist.json', mode='w+',
             encoding='UTF-8').write('{}')

    db = sqlite3.connect(f'{config.DATA_PATH}/data.db')
    db_cursor = db.cursor()
    db_cursor.execute("""
                      CREATE TABLE "last_message_list" (
                        "user_mid"	INTEGER NOT NULL UNIQUE,
                        "last_msg_timestamp"	INTEGER NOT NULL,
                        PRIMARY KEY("user_mid")
                      )""")
