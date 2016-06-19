import requests
import json
import re
from collections import OrderedDict
from bs4 import BeautifulSoup


def decolog(name):
    """
    :param name: str
    :return: str json
    """
    html = requests.get("http://www.dclog.jp/%s" % name)
    soup = BeautifulSoup(html.text, "html.parser")
    data = []
    for article in soup.select('article'):
        # 非公開のエントリがあった場合の対策
        if article.select('.decoBody'):
            content = ''
            images = []
            for div in article.select('.decoBody div'):
                if div.img:
                    # 1つのdivの中に複数のimgがある場合の対策
                    for img in div.find_all('img'):
                        # gifは除外する
                        if not re.compile(r'\.gif$').search(img.get('src')):
                            if not images:
                                # imagesが空の場合はそのまま追加する
                                images.append(img.get('src'))
                            else:
                                # それ以外は重複チェックをしてから追加する
                                has_no_duplicate = True
                                for image in images:
                                    if image == img.get('src'):
                                        has_no_duplicate = False
                                if has_no_duplicate:
                                    images.append(img.get('src'))
                elif div.text == '':
                    content += '\n'
                else:
                    content += div.text + '\n'
            data.append(OrderedDict([
                ('entry_id', re.sub(r'^/en/[0-9]+/', '', article.header.a.get('href'))),
                ('title', article.header.text.replace('\n', '')),
                ('content', content),
                ('images', images),
                ('created_at', article.time.get('datetime'))
            ]))
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return json_str

# open('data.json', 'w').write(decolog('erijchan'))
