"""
获取来自bilibili的涩图
"""

import requests
import datetime

"""
Custom part
"""
ups = [
    {
        "index": 0,
        "name": "me",
        "UID": "660076325"
    },
    {
        "index": 1,
        "name": "逗逼的咸鱼君",
        "UID": "37399681"
    },
    {
        "index": 2,
        "name": "念儿゜",
        "UID": "305276429"
    },
    {
        "index": 3,
        "name": "猫羽雫",
        "UID": "23091718"
    }

]

config = {
    "day": 1,
    "amount": 20,
    "start_day": '2022-08-04',
    "end_day": '2022-08-05'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77 '
}

"""
获取一次动态并返回json格式文件
"""


def get_dynamic_list_once(offset):
    get_url = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    params = {
        'offset': offset,  # 作为参数传入，获取下一组动态
        'host_mid': ups[0]['UID'],  # upuid
        'timezone_offset': '-480'  # 默认-480
    }
    res = requests.get(url=get_url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()['data']
    else:
        return -1


"""
获取下一组offset
"""


def get_offset(data):
    if data != -1:
        if not data['has_more']:
            return '已经没有了！'  # no more dynamics
        return data['offset']
    else:
        return -1


"""
判断是否为转载
"""


def is_origin(item):
    if 'orig' in item:
        return False
    return True

"""
获取动态发布时间，如果为转载，则为原动态发布时间
"""


def get_publish_timestamp(author):
    time_stamp = author['pub_ts']
    date_array = datetime.datetime.utcfromtimestamp(time_stamp)
    format_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
    return format_time

"""
处理一条动态
"""
def handle_one_dynamic(dict):


"""
主要执行函数
"""


def main():
    # 获取第一组动态
    data_dict = get_dynamic_list_once('')
    offset = get_offset(data_dict)

    print(data_dict)
    print(offset)


if __name__ == '__main__':
    main()
