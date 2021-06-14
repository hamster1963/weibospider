from datetime import datetime
import json
import os
import re
from lxml import etree
import requests
import log_tools

BASE_URL = 'https://s.weibo.com'
# raw json文件位置
JSON_DIR = './raw'
ARCHIVE_DIR = './archives'
LOG_DIR = './logs'

logger = log_tools.init_logger(__name__)


def getHTML(url, needPretty=False):
    """ 获取网页 HTML 返回字符串

    Args:
        url: str, 网页网址
        needPretty: bool, 是否需要美化(开发或测试时可用)
    Returns:
        HTML 字符串
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/84.0.4147.125 Safari/537.36 '
    }
    response = requests.get(url, headers=headers)
    return response.text


def save(filename, content):
    """ 写文件

    Args:
        filename: str, 文件路径
        content: str/dict, 需要写入的内容
    Returns:
        None
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # 写 JSON
        if filename.endswith('.json') and isinstance(content, dict):
            json.dump(content, f, ensure_ascii=False, indent=2)
        # 其他
        else:
            f.write(content)


def load(filename):
    """ 读文件

    Args:
        filename: str, 文件路径
    Returns:
        文件所有内容 字符串
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


# 使用 xpath 解析 HTML
def parseHTMLByXPath(content):
    """ 使用 xpath 解析 HTML, 提取榜单信息

    Args:
        content: str, 待解析的 HTML 字符串
    Returns:
        榜单信息的字典 字典
    """
    html = etree.HTML(content)

    titles = html.xpath('//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/text()')[0:10]
    hrefs = html.xpath('//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/@href')[0:10]
    hots = html.xpath(
        '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/../span/text()')[0:10]
    titles = [title.strip() for title in titles]
    hrefs = [BASE_URL + href.strip() for href in hrefs]
    hots = [int(hot.strip()) for hot in hots]

    correntRank = {}
    for i, title in enumerate(titles):
        correntRank[title] = {'href': hrefs[i], 'hot': hots[i]}

    return correntRank


# 更新本日榜单
def updateJSON(correntRank):
    """ 更新当天的 JSON 文件

    Args:
        correntRank: dict, 最新的榜单信息
    Returns:
        与当天历史榜单对比去重, 排序后的榜单信息字典
    """
    filename = datetime.today().strftime('%Y%m%d') + '.json'
    filename = os.path.join(JSON_DIR, filename)

    # 文件不存在则创建
    if not os.path.exists(filename):
        save(filename, {})

    historyRank = json.loads(load(filename))
    for k, v in correntRank.items():
        # 若当前榜单和历史榜单有重复的，取热度数值(名称后面的数值)更大的一个
        if k in historyRank:
            historyRank[k]['hot'] = max(historyRank[k]['hot'], correntRank[k]['hot'])
        # 若没有，则添加
        else:
            historyRank[k] = v

    # 将榜单按 hot 值排序
    rank = {k: v for k, v in sorted(historyRank.items(), key=lambda item: item[1]['hot'], reverse=True)}

    # 更新当天榜单 json 文件
    save(filename, rank)
    return rank


def updateArchive(rank):
    """ 更新当天的 Markdown 归档文件

    Args:
        rank: dict, 榜单信息
    Returns:
        更新后当天 Markdown 文件内容
    """
    line = '1. [{title}]({href}) {hot}'
    lines = [line.format(title=k, hot=v['hot'], href=v['href']) for k, v in rank.items()]
    content = '\n'.join(lines)

    filename = datetime.today().strftime('%Y%m%d') + '.md'
    filename = os.path.join(ARCHIVE_DIR, filename)

    # 更新当天榜单 markdown 文件
    save(filename, content)
    return content


def updateReadme(rank):
    """ 更新 README.md

    Args:
        rank: str, markdown 格式的榜单信息
    Returns:
        None
    """
    try:
        filename = './README.md'

        rank = '最后更新时间 {}\n\n'.format(datetime.now().strftime('%Y-%m-%d %X')) + rank

        rank = '<!-- Rank Begin -->\n\n' + rank + '\n<!-- Rank End -->'

        content = re.sub(r'<!-- Rank Begin -->[\s\S]*<!-- Rank End -->', rank, load(filename))
        save(filename, content)

    except IOError:
        print(
            "Error: 没有找到文件或读取文件失败")
    else:
        print('最后更新时间 {}\n\n'.format(datetime.now().strftime('%Y-%m-%d %X')))


def main():
    url = '/top/summary'
    try:
        content = getHTML(BASE_URL + url)
        correntRank = parseHTMLByXPath(content)
        rankJSON = updateJSON(correntRank)
        rankMD = updateArchive(rankJSON)
        updateReadme(rankMD)
    except Exception as e:
        logger.exception(e)
        raise e

if __name__ == '__main__':
    main()
