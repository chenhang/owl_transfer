from bs4 import BeautifulSoup

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
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://m.weibo.cn/p/index?extparam=OWL&containerid=100808c2b957d7481945468d28ac3d34f89b11',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
            'MWeibo-Pwa': '1',
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = (
            ('extparam', 'OWL'),
            ('containerid', '100808c2b957d7481945468d28ac3d34f89b11_-_feed'),
        )

        res = requests.get('https://m.weibo.cn/api/container/getIndex', headers=headers, params=params)

        # NB. Original query string below. It seems impossible to parse and
        # reproduce query strings 100% accurately so the one below is given
        # in case the reproduced version is not "correct".
        # response = requests.get('https://m.weibo.cn/api/container/getIndex?extparam=OWL&containerid=100808c2b957d7481945468d28ac3d34f89b11_-_feed', headers=headers)
        for li in res.json()['data']['cards']:
            if 'card_group' not in li || not any( [d in content_li.text for d in ['转会', '官宣', '交易', '宣布', '离队', '加入', '席位', '透露', '登场', '退役']]):
                continue
            # print(li.find('.tail-info')[-1].text)
            item = {'user_name': li.findAll('td')[2].find('a').text,
                    'link': 'http://bbs.ngacn.cc' + content_li.attrs['href'],
                    'id': 'nga-' + content_li.attrs['href'].split('tid=')[-1],
                    'text': content_li.text, 'origin_text': content_li.text,
                    'comments': [], 'images': [], 'type': 'nga', 'display': True,
                    'posted_at': int(li.findAll('td')[2].find('span').text)}
            # origin_avatar_url = li.find('.p_author_face > img', first=True).attrs.get('data-tb-lazyload', li.find(
            #     '.p_author_face > img', first=True).attrs['src'])
            # if 'http' not in origin_avatar_url:
            #     origin_avatar_url = 'http:' + origin_avatar_url
            # if self.image_mapping.get(origin_avatar_url, DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
            #     self.image_mapping[origin_avatar_url] = upload_image(self.im, origin_avatar_url, item['user_name'],
            #                                                          DEFAULT_IMAGE_URL)
            # item['user_avatar'] = self.image_mapping[origin_avatar_url]
            # for img in content_li.find('.BDE_Image'):
            #     origin_url = img.attrs['src']
            #     if self.image_mapping.get(origin_url, DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
            #         self.image_mapping[origin_url] = upload_image(self.im, origin_url, item['user_name'],
            #                                                       DEFAULT_IMAGE_URL)
            #     item['images'].append(self.image_mapping[origin_url])
            if item['id'] not in self.items or data_changed(self.items[item['id']], item):
                self.items[item['id']] = item
                self.new_items.append(item)
