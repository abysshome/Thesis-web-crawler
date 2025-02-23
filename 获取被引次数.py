import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def get_citation_count(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data and 'is-referenced-by-count' in data['message']:
                citation_count = data['message']['is-referenced-by-count']
                print(f"DOI: {doi}, 引用次数: {citation_count}")
                return citation_count
            else:
                print("未找到引用次数信息")
                return 0
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求DOI {doi} 出错: {e}")
        return None

if __name__ == '__main__':
    # 读取CSV文件
    df = pd.read_csv('updated_file.csv')

    # 检查是否存在citedNum列，若不存在则创建
    if 'citedNum' not in df.columns:
        df['citedNum'] = 0

    # 获取需要处理的DOI列表（citedNum为0或者缺失）
    dois_to_process = df[df['citedNum'].fillna(0) == 0]['doi'].tolist()

    # 如果没有需要处理的DOI，则退出
    if not dois_to_process:
        print("所有DOI都已经处理完毕。")
    else:
        print(f"准备处理 {len(dois_to_process)} 个DOI...")

        # 使用线程池执行异步任务
        with ThreadPoolExecutor(max_workers=5) as executor:  # 根据需要调整max_workers的数量
            future_to_doi = {executor.submit(get_citation_count, doi): doi for doi in dois_to_process}

            citedNums = []
            last_save_time = time.time()
            save_interval = 60  # 每隔60秒保存一次

            for i, future in enumerate(as_completed(future_to_doi)):
                doi = future_to_doi[future]
                try:
                    citation_count = future.result()
                    citedNums.append(citation_count if citation_count is not None else 0)

                    # 更新DataFrame
                    df.loc[df['doi'] == doi, 'citedNum'] = citedNums[-1]

                    current_time = time.time()
                    if current_time - last_save_time >= save_interval or i == len(dois_to_process) - 1:
                        df.to_csv('updated_file1.csv', index=False)
                        print("文件已保存")
                        last_save_time = current_time

                except Exception as exc:
                    print(f"DOI {doi} generated an exception: {exc}")
                    citedNums.append(0)

        # 确保最后保存一次文件
        df.to_csv('updated_file_final.csv', index=False)
        print("所有数据处理完毕，文件最终保存")