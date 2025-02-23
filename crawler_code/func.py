import os

import pandas as pd


def getLast(path, url): # 获取上次爬取的最后一条数据的索引
    res = 0
    df = pd.read_csv(path)
    for index, row in df.iterrows():
        if row['url'].startswith(url):
            res = index
    return res


if __name__ == '__main__':
    print(getLast(f'../informs/informs3.csv', "https://pubsonline.informs.org") - 1)
