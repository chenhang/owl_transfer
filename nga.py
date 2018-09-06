from bs4 import BeautifulSoup

from util import *


class Nga():
    session = None

    def __init__(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        data = load_json('data/nga.json')
        self.items = data.get('items', {})
        self.new_items = []
        self.image_mapping = load_json('local_config/images.json')
        self.parse()
        write_json('data/nga.json', {'items': self.items, 'page': 1})
        write_json('local_config/images.json', self.image_mapping)

    def url(self, page=1):
        return "http://bbs.ngacn.cc/thread.php?fid=587&page=" + str(page)

    def parse(self):
        res = requests.get(self.url(1), headers=nga_headers,
                           cookies=nga_cookies)
        html = BeautifulSoup(res.content, "lxml")
        for li in html.findAll('tr', {'class': 'topicrow'}):
            content_li = li.findAll('td')[1].find('a')
            if 'href' not in content_li.attrs \
                    or not any(
                        [d in content_li.text for d in ['转会', '官宣', '交易', '宣布', '离队', '加入', '席位', '透露',
                                                        '登场', '退役', '人员变动', '合同', '解约', '解除合约',
                                                        '合约']]):
                continue
            # print(li.find('.tail-info')[-1].text)
            item = {'user_name': li.findAll('td')[2].find('a').text,
                    'link': 'http://bbs.ngacn.cc' + content_li.attrs['href'],
                    'id': 'nga-' + content_li.attrs['href'].split('tid=')[-1],
                    'text': content_li.text, 'origin_text': content_li.text,
                    'comments': [], 'images': [], 'type': 'nga', 'display': False,
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
