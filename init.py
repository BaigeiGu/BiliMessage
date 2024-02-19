import os
import config

def init():
    if not os.path.exists(config.DATA_PATH):
        print("Data path doesn't exists.")
        print(f"Will make dir:{config.DATA_PATH}")
        os.mkdir(config.DATA_PATH)
        os.mkdir(config.DATA_PATH + '/images')
        open(config.DATA_PATH + '/userlist.json', mode='w+',
             encoding='UTF-8').write('{}')
