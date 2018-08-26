# -*- coding: utf8 -*-

import logging

import leancloud

import config
from man_tieba import ManTieba
from owl_tweets import OwlTweet
from util import *

logging.basicConfig(level=logging.ERROR)

leancloud.init(config.leancloud_app_id, config.leancloud_app_key)


def object_id_key(name, id_value):
    return name + "_" + str(id_value)


def leancloud_object(name, data, id_key='id'):
    DataObject = leancloud.Object.extend(name)
    if object_id_key(name, data[id_key]) in OBJECT_ID_MAP and name not in []:
        data_object = DataObject.create_without_data(
            OBJECT_ID_MAP[object_id_key(name, data[id_key])])
    else:
        data_object = DataObject()
    for key, value in data.items():
        data_object.set(key, value)
    return data_object


def update_data():
    redcafe = OwlTweet()
    object_data = {
        'Transfer': {'data': redcafe.new_items, 'id_key': 'id'},
    }

    for name, info in object_data.items():
        data_objects = []
        LEANCLOUD_OBJECT_DATA = load_json(os.path.join('leancloud_data', name))
        data_dict = {}
        for item in info['data']:
            if data_changed(LEANCLOUD_OBJECT_DATA.get(object_id_key(
                    name, item.get(info['id_key'])), {}), item):
                if info['id_key'] not in item:
                    continue
                data_objects.append(leancloud_object(
                    name, item, info['id_key']))
            data_dict[item.get(info['id_key'])] = item
        print(name + " Total Count:" + str(len(info['data'])))
        print(name + " Changed Count:" + str(len(data_objects)))
        i = 0
        batch_size = 20
        while True:
            if len(data_objects[i:i + batch_size]) > 0:
                leancloud.Object.save_all(data_objects[i:i + batch_size])
                i += batch_size
            else:
                break
        for data_object in data_objects:
            OBJECT_ID_MAP[object_id_key(
                name, data_object.get(info['id_key']))] = data_object.id
            LEANCLOUD_OBJECT_DATA[object_id_key(
                name, data_object.get(info['id_key']))] = data_dict[data_object.get(info['id_key'])]
        write_json('local_config/object_id_map.json', OBJECT_ID_MAP)
        write_json(os.path.join('leancloud_data', name), LEANCLOUD_OBJECT_DATA)


if __name__ == '__main__':
    LEANCLOUD_OBJECT_DATA = {}
    if not os.path.exists("leancloud_data"):
        os.makedirs("leancloud_data")
    if not os.path.exists("local_config"):
        os.makedirs("local_config")
    OBJECT_ID_MAP = load_json('local_config/object_id_map.json')
    update_data()
