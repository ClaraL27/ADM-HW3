from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import os

# 1.1
def get_link(url_link, file_txt):
    anime = []
    for page in tqdm(range(0, 400)):
        url = url_link + str(page * 50)
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', class_='hoverinfo_trigger fl-l ml12 mr8'):
            if type(link.get('id')) == str:
                anime.append(link.get('href'))

    with open(file_txt, 'w', encoding = 'utf-8') as f:
        for link_l in anime:
            f.write(link_l + str('\n'))


# 1.2
def crawl_html(start_index, stop_index=0):
    with open('anime_links.txt', 'r', encoding='utf-8') as f:
        urls = f.read().splitlines()[start_index:]
        if stop_index == 0:
            stop_index = len(urls)
        for i, url in zip(tqdm(range(start_index, stop_index)), urls):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.35 Safari/537.36 QIHU 360SE'
            }

            anime_page = requests.get(url, headers = headers)

            # if something bad happen
            if(anime_page.status_code != 200):
                raise Exception(f"Something really bad happened. Current index was {i}")

            pages = i//50 + 1
            path = f"pages/page_{pages}"
            try:
                os.mkdir(path)
            except OSError:
                pass
            else:
                print ("Successfully created the directory %s " %path)

            with open(f'{path}/article_{i+1}.html', 'w', encoding='utf-8') as f:
                f.write(anime_page.text)