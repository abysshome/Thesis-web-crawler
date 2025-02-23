import random
import time

import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

from func import getLast


# <span class="link-button-text">Sign in</span>
def index_to_file():
    file = open("sciencedirect_index.txt", "w")
    for index in indexList:
        file.write(str(index) + ",")
    file.close()


def login(driver):
    # 登录函数
    driver.get('https://www.sciencedirect.com/science/article/pii/S1631072119301809')
    # driver.maximize_window()
    time.sleep(2)
    driver.find_element(By.ID, 'gh-cta-btn').click()
    # time.sleep(100)
    driver.find_element(By.ID, 'bdd-email').send_keys('')
    print("已输入邮箱")
    driver.find_element(By.ID, 'bdd-elsPrimaryBtn').click()
    print("点击")
    time.sleep(5)
    # bdd-password
    driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    driver.find_element(By.ID, 'bdd-password').send_keys("")
    print("已输入密码")
    driver.find_element(By.ID, 'bdd-elsPrimaryBtn').click()
    print("点击")
    time.sleep(2)

def extract_data(url, df, index, driver):
    driver.get(url)
    html = driver.page_source
    tree = etree.HTML(html)
    # 数据提取操作...
    # 标题
    match_title = tree.xpath('//span[@class="title-text"]//text()')
    match_title = ','.join(match_title)
    df.loc[index, 'title'] = match_title
    # doi
    match_doi = tree.xpath('//span[@class="anchor-text"]//text()')
    match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
    if match_doi[0]:
        df.loc[index, 'doi'] = match_doi[0]
    else:
        print("No doi found")
        df.loc[index, 'doi'] = 'null'
    # 摘要
    match_abstract = tree.xpath('//div[@class="abstract author"]//text()')[1:]
    match_abstract = ','.join(match_abstract)
    df.loc[index, 'abstract'] = match_abstract
    # 关键字
    match_keywords = tree.xpath(
        '//div[@class="Keywords u-font-serif text-s"]//div[@class="keywords-section" and not(contains(h2, "MSC"))]//span/text()')
    match_keywords = ','.join(match_keywords)
    df.loc[index, 'keywords'] = match_keywords
    # 期刊
    match_published_in = tree.xpath(
        '//div[@class="publication-volume u-text-center"]//text()|//a/span[@class="anchor-text"]/h2/text()')
    match_published_in = ''.join(match_published_in)
    df.loc[index, 'published'] = match_published_in
    # 作者
    match_author = tree.xpath('//div[@class="author-group"]//text()')[1:]
    match_author = ''.join(match_author)
    df.loc[index, 'authors'] = match_author


def scrape_data(month, start_index):
    # 读取
    df = pd.read_csv(f'sciencedirect\\sciencedirect{month}.csv')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)
    # 登录
    driver = webdriver.Chrome(options=options)
    login(driver)

    for index, row in df.iterrows():
        if index < start_index:
            continue
        url = row['url']
        if url.startswith('https://www.sciencedirect.com') and row['doi'] == 'nan':
            print(f"m{month}:{index}")
            try:  # 尝试爬取
                extract_data(url, df, index, driver)
                if index >= getLast(f'sciencedirect\\sciencedirect{month}.csv', "https://www.sciencedirect.com") - 2:
                    df.to_csv(f'sciencedirect\\sciencedirect{month}.csv', index=False)
                    start_index = len(df) - 1
            except Exception as e:  # 爬取失败
                print("sci_index: " + str(index))
                # 保存当前结果
                df.to_csv(f'sciencedirect\\sciencedirect{month}.csv', index=False)
                time.sleep(random.randint(1, 2))
                # 更新全局变量 start_index
                start_index = index
                indexList[month] = start_index
                index_to_file()
                # 如果 start_index 小于 20000，则继续循环
                if index <= len(df) - 1:
                    if driver:
                        driver.quit()
                    driver = webdriver.Chrome(options=options)
                    login(driver)
                else:
                    df.to_csv(f'sciencedirect\\sciencedirect{month}.csv', index=False)


# tunnel = "t910.kdltps.com:15818"
# username = ""
# password = ""
# proxies = {
#     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
#     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
# }
# chrome_options = Options()
#
# proxy = random.choice(list(proxies.values()))  # 随机选择一个代理字符串
# print(proxy)
#
# chrome_options.add_argument("--proxy-server=" + proxy)  # 添加代理

indexList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # 页面部分内容是动态加载得时候，无头模式默认size为0x0，需要设置最大化窗口并设置windowssize，不然会出现显示不全的问题
# options.add_argument('--proxy-server=http://127.0.0.1:7890')
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
    }
}
options.add_experimental_option('prefs', prefs)
if __name__ == '__main__':
    for i in range(10, 13):
        if i == 6:
            continue
        scrape_data(i, indexList[i])
    # futures = []
    # with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
    #     for i in range(4, 13):
    #         if i == 6:
    #             continue
    #         futures.append(pool.submit(scrape_data, i, indexList[i]))
    #     concurrent.futures.wait(futures)
