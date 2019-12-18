#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: step03_download_the_basic_information_of_jf
# @Date: 2019/12/17
# @Author: Mark Wang
# @Email: wangyouan@gamil.com

"""
python -m Downloader.step01_download_the_basic_information_of_jfe
"""

import os
import re
import time
import random
import requests

from selenium import webdriver
import numpy as np
from pandas import DataFrame
from bs4 import BeautifulSoup

from Constants import Constants as const
from .step02_download_the_basic_information_of_rfs import user_agent_list

if __name__ == '__main__':
    article_info = DataFrame(
        columns=[const.YEAR, const.VOLUME, const.ISSUE, const.TITLE, const.URL, const.AUTHOR, const.PAGE, const.DOI])

    for year in range(2017, 2020):
        for issue in range(1, 7):
            volume = year - 1945
            result_dict = {const.YEAR: year, const.VOLUME: volume, const.ISSUE: issue}

            url = 'https://onlinelibrary.wiley.com/toc/15406261/{}/{}/{}'.format(year, volume, issue)
            req = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)})
            soup = BeautifulSoup(req.content, 'lxml')
            req.close()

            article_div_list = soup.find_all('div', class_='issue-item')

            for article_div in article_div_list:
                author_spans = article_div.find_all('span', class_='author-style')
                if not author_spans:
                    continue

                article_dict = result_dict.copy()
                article_dict.update({const.AUTHOR: ';'.join(map(lambda x: x.text.strip(), author_spans)),
                                     const.TITLE: article_div.find('h2').text,
                                     const.DOI: '/'.join(article_div.find('a').get('href').split('/')[2:]),
                                     const.PAGE: article_div.find('li', class_='page-range').find_all('span')[-1].text})

                article_dict[const.URL] = "http://doi.org/{}".format(article_dict[const.DOI])

                article_info: DataFrame = article_info.append(article_dict, ignore_index=True)

            time.sleep(random.random() * 5 + 1)

    valid_article: DataFrame = article_info.loc[article_info[const.TITLE] != 'AMERICAN FINANCE ASSOCIATION']
    valid_article: DataFrame = valid_article.loc[~valid_article[const.TITLE].str.startswith('Report')]
    valid_article: DataFrame = valid_article.loc[
        ~valid_article[const.TITLE].str.startswith('American Finance Association')]
    valid_article: DataFrame = valid_article.loc[
        ~valid_article[const.TITLE].str.startswith('Corrigendum for')]
    valid_article.loc[:, const.TITLE] = valid_article[const.TITLE].str.strip()

    valid_article.loc[:, const.ABSTRACT] = np.nan

    driver = webdriver.Chrome()

    for i in valid_article.index:
        driver.get(valid_article.loc[i, const.URL])
        soup = BeautifulSoup(driver.page_source, 'lxml')
        valid_article.loc[i, const.ABSTRACT] = soup.find('section', class_="article-section__abstract").find(
            'div').text.strip()
        time.sleep(random.random() * 5 + 1)

    driver.quit()
    valid_article.to_pickle(os.path.join(const.TEMP_PATH, '20191218_jf_abstract.pkl'))
    valid_article.to_excel(os.path.join(const.RESULT_PATH, '20191218_jf_abstract.xlsx'), index=False)
