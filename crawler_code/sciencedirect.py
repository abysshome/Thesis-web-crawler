import time
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local

start_index = 0
thread_local = local()  # 创建线程本地存储对象


def login(driver):
    # 登录函数
    if not getattr(thread_local, 'logged_in', False):
        # 如果线程本地存储中的 logged_in 属性为 False（未登录状态），则执行登录操作
        driver.get('https://www.sciencedirect.com/science/article/pii/S1631072119301809')
        driver.maximize_window()
        time.sleep(2)
        driver.find_element(By.ID, 'gh-cta-btn').click()
        driver.find_element(By.ID, 'bdd-email').send_keys('')
        driver.find_element(By.ID, 'bdd-elsPrimaryBtn').click()
        time.sleep(2)
        driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        driver.find_element(By.CLASS_NAME, 'els-container-right').click()
        time.sleep(2)
        driver.find_element(By.ID, 'username').send_keys('')
        driver.find_element(By.ID, 'password').send_keys('')
        driver.find_element(By.ID, 'login_submit').click()
        time.sleep(2)
        # 将 logged_in 属性标记为 True，表示已登录
        thread_local.logged_in = True


def extract_data(url, df, index):
    try:
        driver = getattr(thread_local, 'driver', None)
        if not driver:
            # 如果线程本地存储中没有 driver 属性，说明是第一次访问，创建新的 WebDriver 实例
            driver = webdriver.Chrome()
            login(driver)  # 调用登录函数，确保登录状态
            # 将新创建的 WebDriver 实例存储在线程本地存储中
            thread_local.driver = driver

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
        df.loc[index, 'doi'] = match_doi[0]
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
    except Exception as e:
        print(f"发生异常：{e}")


def scrape_data(month):
    global start_index
    df = pd.read_csv(f'data\\month{month}.csv')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for index, row in df.iterrows():
            if index < start_index:
                continue
            url = row['url']
            if url.startswith('https://www.sciencedirect.com'):
                futures.append(executor.submit(extract_data, url, df, index))

        # 等待所有任务完成
        for future in as_completed(futures):
            future.result()

    # 任务完成后关闭 WebDriver
    driver = getattr(thread_local, 'driver', None)
    if driver:
        driver.quit()

    df.to_csv(f'sciencedirect-muti{month}.csv', index=False)


if __name__ == '__main__':
    for i in range(1, 13):
        if i == 6:
            continue
        # 启动程序
        start_index = 0
        scrape_data(i)
