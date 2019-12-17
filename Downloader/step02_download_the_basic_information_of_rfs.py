#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: step02_download_the_basic_information_of_rfs
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

user_agent_list = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
    'Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
    'Safari/537.36',
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; '
    '.NET CLR 3.5.30729)'
]


def check_if_valid_sections(title):
    prefixs = ['REGULAR ARTICLES', 'ARTICLE', 'SPECIAL SECTION']
    for prefix in prefixs:
        if title.startswith(prefix):
            return True

    return False


def scrape_article_information(article_division):
    citation_division = article_division.find('div', class_='ww-citation-primary')
    page_list = re.findall(r'Pages\s(\d+–\d+)', citation_division.text)
    if page_list:
        page = page_list[0]
    else:
        page = np.nan
    return {const.TITLE: article_division.find('h5').text.strip(),
            const.AUTHOR: article_division.find('div', class_='al-authors-list').text.strip(),
            const.URL: citation_division.find('a').text, const.DOI: citation_division.find('a').text, const.PAGE: page}


if __name__ == '__main__':
    article_info = DataFrame(
        columns=[const.YEAR, const.VOLUME, const.ISSUE, const.TITLE, const.URL, const.AUTHOR, const.PAGE, const.DOI])
    for volume in range(29, 34):
        for issue in range(1, 13):
            if volume == 33 and issue > 1:
                continue

            if not article_info.loc[
                (article_info[const.VOLUME] == volume) & (article_info[const.ISSUE] == issue)].empty:
                continue

            url = 'https://academic.oup.com/rfs/issue/{}/{}'.format(volume, issue)
            req = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)})
            soup = BeautifulSoup(req.content, 'lxml')
            req.close()

            article_list = soup.find(id='ArticleList')
            sections = article_list.find_all('section')
            result_dict = {const.YEAR: 1987 + volume, const.VOLUME: volume, const.ISSUE: issue}
            initial_size = article_info.shape[0]
            for section in sections:
                section_title = section.find('h4', class_='title').text

                if check_if_valid_sections(section_title.upper()):
                    article_divs = section.find_all('div', class_='al-article-item-wrap')

                    for article_div in article_divs:
                        article_dict = result_dict.copy()
                        article_dict.update(scrape_article_information(article_div))

                        article_info: DataFrame = article_info.append(article_dict, ignore_index=True)

            current_size = article_info.shape[0]
            if current_size == initial_size:
                print('Volume {} issue {} has not article section'.format(volume, issue))

            time.sleep(random.random() * 5)

    for issue in [6, 8, 9]:
        url = 'https://academic.oup.com/rfs/issue/29/{}'.format(issue)
        req = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)})
        soup = BeautifulSoup(req.content, 'lxml')
        req.close()

        result_dict = {const.YEAR: 1987 + 29, const.VOLUME: 29, const.ISSUE: issue}

        article_list = soup.find(id='ArticleList')
        article_divs = article_list.find_all('div', class_='al-article-item-wrap')
        for article_div in article_divs:
            author_div = article_div.find('div', class_='al-authors-list')
            if author_div is None:
                continue

            article_dict = result_dict.copy()
            article_dict.update(scrape_article_information(article_div))
            article_info: DataFrame = article_info.append(article_dict, ignore_index=True)
        time.sleep(random.random() * 5)

    article_info.loc[:, const.ABSTRACT] = np.nan
    # for i in article_info.loc[article_info[const.ABSTRACT].isnull()].index:
    #     article_url = article_info.loc[i, const.URL]
    #     req = requests.get(article_url, headers={'User-Agent': random.choice(user_agent_list)})
    #     article_soup = BeautifulSoup(req.content, 'lxml')
    #     req.close()
    #     article_info.loc[i, const.ABSTRACT] = article_soup.find('section', class_='abstract').text.strip()
    #     time.sleep(random.random() * 5)

    driver = webdriver.Chrome()
    for i in article_info.loc[article_info[const.ABSTRACT].isnull()].index:
        article_url = article_info.loc[i, const.URL]
        driver.get(article_url)
        article_soup = BeautifulSoup(driver.page_source, 'lxml')
        req.close()
        article_info.loc[i, const.ABSTRACT] = article_soup.find('section', class_='abstract').text.strip()
        time.sleep(random.random() * 5)
    driver.quit()

    article_info.to_pickle(os.path.join(const.TEMP_PATH, '20191217_rfs_basic_information.pkl'))
