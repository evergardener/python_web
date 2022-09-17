"""
获取来自bilibili的涩图
"""
import os.path
import re
import sqlite3
import string
import random

import requests
import datetime

import xlwt as xlwt

"""
Custom part
"""
ups = [
    {
        "index": 0,  # 单纯索引值
        "name": "me",  # 用户名
        "type": 0,  # 动态类型，需要不同正则解析
        "UID": "660076325"  # uid
    },
    {
        "index": 1,
        "name": "逗逼的咸鱼君",
        "type": 1,
        "UID": "37399681"
    },
    {
        "index": 2,
        "name": "念儿゜",
        "type": 2,
        "UID": "305276429"
    },
    {
        "index": 3,
        "name": "猫羽雫",
        "type": 3,
        "UID": "23091718"
    }

]

config = {
    "day": 1,
    "amount": 20,
    "start_day": '2022-08-04',
    "end_day": '2022-08-05',
    "savePath": 'D:\\Evergarden\\Desktop\\pics\\'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77 '
}
current_amount = 0
flag = True
# 正则
pattern_artist = r'画师[:|：](.+)'
pattern_pixiv_id = r'(\d{5,})'
"""
获取一次动态并返回json格式文件
"""


def get_dynamic_list_once(offset):
    get_url = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    params = {
        'offset': offset,  # 作为参数传入，获取下一组动态
        'host_mid': ups[1]['UID'],  # upuid
        'timezone_offset': '-480'  # 默认-480
    }
    res = requests.get(url=get_url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()['data']
    else:
        return -1


"""
判断是否还有下一组，如果有则获取下一组offset
"""


def get_offset(data):
    has_more = data['has_more']
    if has_more:
        return has_more, data['offset']
    return has_more, 0


"""
判断是否为转载
"""


def is_origin(item):
    if 'orig' in item:
        return item['orig']['modules']
    return item['modules']


"""
获取动态发布时间，如果为转载，则为原动态发布时间
"""


def get_publish_timestamp(author):
    time_stamp = author['pub_ts']
    date_array = datetime.datetime.utcfromtimestamp(time_stamp)
    format_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
    return format_time, time_stamp


"""
处理一条动态
"""


def handle_one_dynamic(dynamicForOne):
    data = {
        "name": "",
        "id": [],
        "time": '',
        "works": []
    }
    modules = is_origin(dynamicForOne)
    author = modules['module_author']
    dynamic = modules['module_dynamic']
    publish_time, time_stamp = get_publish_timestamp(author)

    # data['time'] = publish_time
    data['time'] = time_stamp
    if get_ts() is not None and time_stamp <= get_ts():
        flag = False
    # 文案
    desc = dynamic['desc']
    artist = ''
    pixiv_id = ''
    try:
        artist = re.search(pattern_artist, desc['text'])
        pixiv_id = re.findall(pattern_pixiv_id, desc['text'])  # 不用search()，考虑到只有id的情况
    except TypeError:
        print('Desc为空，鉴定为动态没有发布图片！')

    if artist is not None and artist != '':
        # print(artist.group(1))
        data['name'] = artist.group(1)

    # if len(pixiv_id) == 1:
    # print(pixiv_id)
    data['id'] = pixiv_id

    if 'draw' in dynamic['major']:
        src_items = dynamic['major']['draw']['items']
        for item in src_items:
            src = item['src']
            data['works'].append(src)
    return data


"""
处理一组动态
"""


def handle_group_dynamics(data):
    dynamic_group = []
    for item in data['items']:
        dynamic_group.append(handle_one_dynamic(item))

    return dynamic_group


"""
创建数据库
"""


def create_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    sql = '''
        CREATE TABLE demo(
        ID INT PRIMARY KEY NOT NULL,
        NAME varchar(30),
        PIXIV_ID varchar(20),
        src varchar(100)
        )
    '''
    cursor.execute(sql)
    conn.commit()
    conn.close()


"""
将数据存入数据库
"""


def save_to_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    # 写sql
    sql = ''
    cursor.execute(sql)
    conn.commit()
    conn.close()


"""
限制条件，是否继续获取
"""


def to_continue():
    if current_amount >= config['amount']:
        return False


"""
下载图片
"""


def download(data, save_path):
    for o in data:
        download_one_dynamic(o)

"""下载一条动态图片
"""
def download_one_dynamic(data):
    index = 0
    random_name = get_file_name(10)
    print("当前正在下载" + str(data['time']) + "发布的图片!")
    for item in data['works']:
        suffix = os.path.splitext(item)[-1]
        if len(data['id']) == 1:
            file_name = data['id'][0] + '-' + str(index) + suffix
        else:
            file_name = random_name + '-' + str(index) + suffix
        index += 1
        # print(config['savePath'] + file_name)
        with open(config['savePath'] + file_name, 'wb') as f:
            f.write(requests.get(item).content)
        f.close()




"""
获取随机文件名

"""

def get_file_name(randomlength):
    str_list = random.sample(string.digits + string.ascii_letters, randomlength)
    random_str = ''.join(str_list)
    return random_str
"""
保存到excel
"""


def save_to_excel(data, sava_path):
    # 保存画师
    # 保存图片链接
    workbook = xlwt.Workbook(encoding='utf-8')
    names_sheet = workbook.add_sheet('画师', cell_overwrite_ok=False)
    links_sheet = workbook.add_sheet('链接', cell_overwrite_ok=False)


    names_sheet.write(0, 0, 'name')
    names_sheet.write(0, 1, 'id')
    names_sheet.write(0, 2, 'time')
    i = 1
    for o in data:
        names_sheet.write(i, 0, o['name'])
        names_sheet.write(i, 1, o['id'])
        names_sheet.write(i, 2, o['time'])
        i += 1
    workbook.save(sava_path + 'test.xls')



"""
将最后一次获取的offset保存到txt，以便下一次继续从此开始
"""
def save_offset(offset):
    with open('offset.txt', 'w') as f:
        f.write(str(offset))
    f.close()

"""
将退出时的最新动态timestamp写入txt
"""
def save_timestamp(ts):
    ts = str(ts)
    with open('../../../ts.txt', 'w+') as f:
        f.write(ts)

    f.close()

# 获取ts
def get_ts():
    try:
        with open('../../../ts.txt', 'r') as f:
            ts = f.readline()
            f.close()
            return int(ts
                       )
    except FileNotFoundError:
        print('哟，还没写！')
        save_timestamp(0)

"""
主要执行函数
"""


def main():
    # 获取offset
    offset = ''
    try:
        with open('offset.txt', 'r') as f:
            offset = f.readline()

        f.close()
    except FileNotFoundError:
        print("文件不存在，还是第一次呢！")
    # 获取第一组动态
    data_dict = get_dynamic_list_once(offset)
    has_more, offset = get_offset(data_dict)
    # print(has_more)
    # print(offset)
    i = 0
    latest_ts = 0
    while flag:
        data = handle_group_dynamics(data_dict)
        if latest_ts == 0:
            latest_ts = data[0]['time']
        save_offset(offset)
        download(data, config['savePath'])
        data_dict = get_dynamic_list_once(offset)
        has_more, offset = get_offset(data_dict)
        save_to_excel(data, config['savePath'])
        # print(data)

        # 下载图片


        i += 1
    # print(data_dict['items'][0])
    # print(handle_one_dynamic(data_dict['items'][0]))

    print('下载完成，正在处理余后作业...')
    save_timestamp(latest_ts)
    # print(offset)




def test():
    save_to_excel(config['savePath'])


if __name__ == '__main__':
    main()
