import pandas as pd

for i in range(1, 13):
    if i == 6:
        continue
    df_ieee = pd.read_csv(f'ieee\\ieee{i}.csv')
    df_tandfonline = pd.read_csv(f'tandfonline\\tandfonline{i}.csv')
    df_informs = pd.read_csv(f'informs\\informs{i}.csv')
    df_sciencedirect = pd.read_csv(f'sciencedirect\\sciencedirect{i}.csv')
    df_ceramics = pd.read_csv(f'ceramics-over\\ceramics{i}.csv')

    df_ieee['date of publication'] = df_ieee['date of publication'].astype(str)
    df_ieee['doi'] = df_ieee['doi'].astype(str)
    df_ieee['abstract'] = df_ieee['abstract'].astype(str)
    df_ieee['published'] = df_ieee['published'].astype(str)
    df_ieee['authors'] = df_ieee['authors'].astype(str)
    df_ieee['title'] = df_ieee['title'].astype(str)
    df_ieee['keywords'] = df_ieee['keywords'].astype(str)

    df_tandfonline['date of publication'] = df_tandfonline['date of publication'].astype(str)
    df_tandfonline['doi'] = df_tandfonline['doi'].astype(str)
    df_tandfonline['abstract'] = df_tandfonline['abstract'].astype(str)
    df_tandfonline['published'] = df_tandfonline['published'].astype(str)
    df_tandfonline['authors'] = df_tandfonline['authors'].astype(str)
    df_tandfonline['title'] = df_tandfonline['title'].astype(str)
    df_tandfonline['keywords'] = df_tandfonline['keywords'].astype(str)

    df_informs['date of publication'] = df_informs['date of publication'].astype(str)
    df_informs['doi'] = df_informs['doi'].astype(str)
    df_informs['abstract'] = df_informs['abstract'].astype(str)
    df_informs['published'] = df_informs['published'].astype(str)
    df_informs['authors'] = df_informs['authors'].astype(str)
    df_informs['title'] = df_informs['title'].astype(str)
    df_informs['keywords'] = df_informs['keywords'].astype(str)

    df_sciencedirect['date of publication'] = df_sciencedirect['date of publication'].astype(str)
    df_sciencedirect['doi'] = df_sciencedirect['doi'].astype(str)
    df_sciencedirect['abstract'] = df_sciencedirect['abstract'].astype(str)
    df_sciencedirect['published'] = df_sciencedirect['published'].astype(str)
    df_sciencedirect['authors'] = df_sciencedirect['authors'].astype(str)
    df_sciencedirect['title'] = df_sciencedirect['title'].astype(str)
    df_sciencedirect['keywords'] = df_sciencedirect['keywords'].astype(str)

    df_ceramics['date of publication'] = df_ceramics['date of publication'].astype(str)
    df_ceramics['doi'] = df_ceramics['doi'].astype(str)
    df_ceramics['abstract'] = df_ceramics['abstract'].astype(str)
    df_ceramics['published'] = df_ceramics['published'].astype(str)
    df_ceramics['authors'] = df_ceramics['authors'].astype(str)
    df_ceramics['title'] = df_ceramics['title'].astype(str)
    df_ceramics['keywords'] = df_ceramics['keywords'].astype(str)
    # 遍历 df1，如果URL匹配，则将其对应的行替换为 df1 中的行
    for index, row in df_sciencedirect.iterrows():
        url = row['c']
        if url.startswith('https://ceramics.onlinelibrary.wiley.com'):
            df_sciencedirect.iloc[index] = df_ceramics.iloc[index]
        elif url.startswith('https://ieeexplore.ieee.org'):
            df_sciencedirect.iloc[index] = df_ieee.iloc[index]
        elif url.startswith('https://pubsonline.informs.org'):
            df_sciencedirect.iloc[index] = df_informs.iloc[index]
        elif url.startswith('https://www.tandfonline.com'):
            df_sciencedirect.iloc[index] = df_tandfonline.iloc[index]
    # 保存到CSV文件，注意设置index=False
    df_sciencedirect.to_csv(f'results\\month{i}.csv', index=False)
