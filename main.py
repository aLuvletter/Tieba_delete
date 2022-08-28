# -*- coding:utf-8 -*-
# Time: 2022/8/20 16:43
# Author: 佚名
import re
import requests
import datetime

def san_page():
    page_id = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Cookie': '百度Cookies'
    }
    for i in range(0, 51, 50):  # 扫描页数50倍数+1,扫3页即101
        url = 'xx吧主页地址' + str(i)
        response = requests.get(url, headers=headers)
        html = response.text.encode('gbk', 'ignore').decode('gbk')
        tiezi_list = re.findall('<li class=" j_thread_list clearfix thread_item_box".*?/p/(.*?)".*?最后回复时间">\r\n            (.*?)        </span>', html, re.S)
        check_reply_time(tiezi_list, page_id)
    del_reply(page_id)
def check_reply_time(tiezi_list, page_id):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    month = int(now_time.split('-')[1].replace('0', ''))
    day = int(now_time.split('-')[2].replace('0', ''))
    for item in tiezi_list:
        if ':' in item[1]:
            page_id.append(item[0])
        elif int(item[1].split('-')[0]) == month and int(item[1].split('-')[1]) == day - 1:
            page_id.append(item[0])

def del_reply(page_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Cookie': '百度Cookies'
    }
    del_number = 0
    del_error_number = 0
    ban_number = 0
    ban_error_number = 0
    for id in page_id:
        url = 'https://tieba.baidu.com/p/' + str(id)
        response = requests.get(url, headers=headers)
        html = response.text.encode('gbk', 'ignore').decode('gbk')
        fid = re.findall('fid: \'(.*?)\',', html, re.S)[0]
        reply = re.findall('p_author_face.*?/home/main\?id=(.*?)&fr=pb&ie=utf-8">.*?d_badge_lv">(.*?)</div></a>.*?id="post_content_(.*?)" class="d_post.*?style="display:;">            (.*?)</div><br>', html, re.S)
        for item in reply:
            if int(item[1]) == 1:
                for item in keyword:
                    if item in item[3]:
                        url = 'https://tieba.baidu.com/f/commit/post/delete'
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                            'Referer': 'https://tieba.baidu.com/p/%s' % id,
                            'Cookie': '百度Cookies'
                        }
                        payload = {
                            'commit_fr': 'pb',
                            'ie': 'utf-8',
                            'tbs': '个人tbs',  # 个人tbs
                            'kw': '贴吧中文名',  # 吧名
                            'fid': fid,  # 贴吧id
                            'tid': id,  # 帖子id
                            'is_vipdel': 0,
                            'reason': 4,  # 删除原因
                            'pid': item[2],  # 回复帖子id
                            'is_finf': 'false'
                        }
                        response = requests.post(url, headers=headers, data=payload).json()  # 删帖
                        if response['err_code'] == 0:
                            del_number = del_number + 1
                        else:
                            del_error_number = del_error_number + 1
                        url = 'https://tieba.baidu.com/pmc/blockid'
                        payload = {
                            'day': 1,  # 封禁天数默认 1 天
                            'fid': fid,  # 吧 id
                            'tbs': '帖子 tbs',
                            'ie': 'gbk',  # 网页编码
                            'portrait[]': item[0],  # 用户 id
                            'reason': '发表政治贴、色情贴，此处不宜，给予封禁处罚。'
                        }
                        response = requests.post(url, headers=headers, data=payload).json()
                        if response['errmsg'] == '成功':
                            ban_number = ban_number + 1
                        else:
                            ban_error_number = ban_error_number + 1
                        break
    print('本次共计删帖成功%s个,删除失败%s个.\n本次共计封禁用户%s个,封禁失败%s个.' % (del_number, del_error_number, ban_number, ban_error_number))

if __name__ == '__main__':
    keyword = ['月', '@']
    san_page()
