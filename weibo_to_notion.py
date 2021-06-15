import json
import re

import requests
import os
import time

JSON_DIR = './raw'
url = "https://api.notion.com/v1/pages"
session = requests.Session()
session.headers = {"Authorization": "secret_MKzGB222HFJLbWa8kr18huPsk8AZ3XTB0I668qO8tuW",
                   "Notion-Version": "2021-05-13"}
update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_latestjson():
    """
    获取最新json文件
    Returns:

    """
    files = os.listdir(JSON_DIR)
    file_dict = {}
    print(type(files))
    for i in files:
        if i == ".DS_Store":
            continue
        ctime = os.stat(os.path.join(JSON_DIR, i)).st_ctime
        file_dict[ctime] = i  # 添加创建时间和文件名到字典
    max_ctime = max(file_dict.keys())  # 取值最大的时间
    lastest_json = './raw/' + file_dict[max_ctime]

    return lastest_json


def convert_json():
    jsonlist = []
    with open(get_latestjson()) as js:
        jsoncontent = json.load(js)
        count = 1
        for i in jsoncontent:
            jsonlist.append(str(count) + " " + i)
            count += 1
        jsonlist = '\n'.join(jsonlist)
        return jsonlist


def push_to_notion(uploadjson):
    json = {
        'parent': {
            'database_id': 'b353529fd9734f78ae4fc8c68bd5a609'
        },
        'properties': {
            'title': {
                'id': 'title',
                'type': 'title',
                'title': [
                    {
                        'type': 'text',
                        'text': {
                            'content': "微博"+" "+uptime,
                            'link': None
                        },
                        'annotations': {
                            'bold': False,
                            'italic': False,
                            'strikethrough': False,
                            'underline': False,
                            'code': False,
                            'color': 'default'
                        },
                        'plain_text': 'shit',
                        'href': None
                    }
                ]
            },
            "type": {
                "id": "`gQ~",
                "type": "select",
                "select": {
                    "id": "5aff2f95-fd1e-489b-8840-bf10bc9519cb",
                    "name": "Post",
                    "color": "purple"
                }
            },
            "tags": {
                "id": "sD^m",
                "type": "multi_select",
                "multi_select": [
                    {
                        "id": "2382b30f-9881-4a8b-ae7f-2d34979c4fb9",
                        "name": "Weibo",
                        "color": "pink"
                    }
                ]
            },
            "status": {
                "id": "f211bdc0-ee00-4186-9a7d-f68c055ec2ee",
                "type": "select",
                "select": {
                    "id": "7abc61d4-b405-480d-b699-12588755fa65",
                    "name": "Published",
                    "color": "red"
                }
            },
            "slug": {
                "id": "d]hq",
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": update_time,
                            "link": None
                        },
                    }
                ]
            },
        },
        'children': [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "text": [{"type": "text", "text": {"content": uploadjson}}]
            }
        }, ]
    }
    resp = requests.Session().request('POST', url, params=None, data=None, json=json, headers=session.headers)
    print(resp)


if __name__ == "__main__":
    lastest_json = get_latestjson()
    uptime = []
    for x in lastest_json:
        x = re.match('^[0-9]*$', x)
        if x is not None:
            uptime.append(x.group())
    uptime = "".join(uptime)
    uploadjson = convert_json()
    push_to_notion(uploadjson)
