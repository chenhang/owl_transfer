import pyimgur
from dateutil.parser import parse

from util import *


class OwlTweet:
    file_path = 'transfer.json'

    def __init__(self):
        self.origin_items = load_json(self.file_path)
        if not os.path.exists("data"):
            os.makedirs("data")
        self.items = load_json('data/tweets.json')
        self.new_items = []
        self.image_mapping = load_json('local_config/images.json')
        self.parse()
        write_json('data/tweets.json', self.items)
        write_json('local_config/images.json', self.image_mapping)

    def parse(self):
        for tweet in self.origin_items['tweets'].values():
            item = {'user_name': tweet['user']['name'],
                    'id': tweet['id_str'], 'posted_at': parse(tweet['created_at']).timestamp(),
                    'origin_text': tweet['text'], 'type': 'tweet'}
            item['text'] = self.items.get(item['id'], {}).get('text', None)
            if item['text'] is None:
                item['text'] = translate(tweet['text']) + "\n\n" + tweet['text']
            if tweet['in_reply_to'] is not None:
                item['in_reply_to'] = {'id': tweet['in_reply_to']['id_str'],
                                       'origin_text': tweet['in_reply_to']['text'],
                                       'user_name': tweet['in_reply_to']['user']['name'], }
                item['in_reply_to']['text'] = self.items.get(item['id'], {}).get('in_reply_to', {}) \
                    .get('text', None)
                if item['in_reply_to']['text'] is None:
                    item['in_reply_to']['text'] = translate(tweet['in_reply_to']['text']) + "\n\n" + \
                                                  tweet['in_reply_to'][
                                                      'text']
                if self.image_mapping.get(tweet['in_reply_to']['user']['profile_image_url'],
                                          DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
                    self.image_mapping[tweet['in_reply_to']['user']['profile_image_url']] = upload_image(self.im, tweet[
                        'in_reply_to']['user'][
                        'profile_image_url'], item['in_reply_to']['user_name'], DEFAULT_IMAGE_URL)
                item['in_reply_to']['user_avatar'] = self.image_mapping[
                    tweet['in_reply_to']['user']['profile_image_url']]
            if self.image_mapping.get(tweet['user']['profile_image_url'],
                                      DEFAULT_IMAGE_URL) == DEFAULT_IMAGE_URL:
                self.image_mapping[tweet['user']['profile_image_url']] = upload_image(self.im, tweet['user'][
                    'profile_image_url'], item['user_name'], DEFAULT_IMAGE_URL)
            item['user_avatar'] = self.image_mapping[tweet['user']['profile_image_url']]
            if item['id'] not in self.items or data_changed(self.items[item['id']], item):
                self.new_items.append(item)
                self.items[item['id']] = item
