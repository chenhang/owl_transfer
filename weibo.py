from bs4 import BeautifulSoup
from dateutil.parser import parse

from util import *


class Weibo():
    session = None

    def __init__(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        data = load_json('data/weibo.json')
        self.items = data.get('items', {})
        self.new_items = []
        self.image_mapping = load_json('local_config/images.json')
        self.parse()
        write_json('data/weibo.json', {'items': self.items, 'page': 1})
        write_json('local_config/images.json', self.image_mapping)

    def url(self, page=1):
        return "http://bbs.ngacn.cc/thread.php?fid=587&page=" + str(page)

    def parse(self):
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://m.weibo.cn/',
            'MWeibo-Pwa': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        res = requests.get('https://m.weibo.cn/feed/friends',
                           headers=headers, cookies=weibo_cookies)

        posts = res.json()['data']['statuses']
        for li in posts:
            if not any([d in li['text'] for d in
                        ['转会', '官宣', '交易', '宣布', '离队', '加入', '席位', '透露',
                         '登场', '退役', '人员变动', '合同', '解约', '解除合约', '合约', '爆料']]):
                continue
            item = {'user_name': li['user']['screen_name'],
                    'link': "https://m.weibo.cn/status/" + li['id'],
                    'id': li['id'],
                    'text': BeautifulSoup(li['text'], 'lxml').text,
                    'comments': [], 'images': [p['url'] for p in li['pics']] if 'pics' in li else [],
                    'type': 'weibo', 'display': True,
                    'posted_at': parse(li['created_at']).timestamp()}
            origin_avatar_url = li['user']['profile_image_url']
            if 'http' not in origin_avatar_url:
                origin_avatar_url = 'http:' + origin_avatar_url
            if self.image_mapping.get(origin_avatar_url, DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
                self.image_mapping[origin_avatar_url] = upload_image('', origin_avatar_url, item['user_name'],
                                                                     DEFAULT_IMAGE_URL)
            item['user_avatar'] = self.image_mapping[origin_avatar_url]
            # for img in content_li.find('.BDE_Image'):
            #     origin_url = img.attrs['src']
            #     if self.image_mapping.get(origin_url, DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
            #         self.image_mapping[origin_url] = upload_image(self.im, origin_url, item['user_name'],
            #                                                       DEFAULT_IMAGE_URL)
            #     item['images'].append(self.image_mapping[origin_url])
            if item['id'] not in self.items or data_changed(self.items[item['id']], item):
                self.items[item['id']] = item
                self.new_items.append(item)
