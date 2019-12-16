#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: step01_download_the_basic_information_of_jfe
# @Date: 2019/12/16
# @Author: Mark Wang
# @Email: wangyouan@gamil.com

"""
python -m Downloader.step01_download_the_basic_information_of_jfe
"""

import os
import time

from pandas import DataFrame
from selenium import webdriver

from Constants import Constants as const


def check_if_article_preview_exist(article_tag_element, wait_time=10):
    start_time = time.time()
    while time.time() - start_time < wait_time:
        elements = article_tag_element.find_elements_by_class_name('article-preview-body')
        if len(elements) != 0:
            return True
        time.sleep(0.1)

    return False


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    result_df = DataFrame(
        columns=[const.YEAR, const.ISSUE, const.VOLUME, const.TITLE, const.DOI, const.PAGE, const.ABSTRACT,
                 const.AUTHOR, const.URL])
    for volume in range(123, 136):
        for issue in range(1, 5):
            if volume == 135 and issue != 1:
                continue

            issue_url = 'https://www.sciencedirect.com/journal/journal-of-financial-economics/vol/{}/issue/{}'.format(
                volume, issue)
            driver.get(issue_url)
            result_dict = {const.VOLUME: volume, const.ISSUE: issue, const.YEAR: 1986 + (volume - 2) // 4}
            article_list = driver.find_elements_by_class_name('js-article-list-item')

            for article_tag in article_list[1:]:
                article_dict = result_dict.copy()
                article_content = article_tag.find_element_by_class_name('js-article')
                article_dict[const.TITLE] = article_content.find_element_by_class_name('js-article-title').text
                article_dict[const.URL] = article_content.find_element_by_tag_name('dt').find_element_by_tag_name(
                    'a').get_attribute('href')
                article_page = article_content.find_elements_by_class_name('js-article-page-range').text()
                div_list = article_content.find_elements_by_class_name('div')
                article_dict[const.AUTHOR] = div_list[0].text
                article_tag.find_element_by_tag_name('button').click()

                if check_if_article_preview_exist(article_tag, 10):
                    article_dict[const.ABSTRACT] = article_content.find_elements_by_class_name('div')[-1].text
                    article_dict[const.DOI] = article_tag.find_elements_by_tag_name('div')[1].get_attribute(
                        'textContent')

                result_df: DataFrame = result_df.append(article_dict, ignore_index=True)
            time.sleep(1)

    driver.quit()
    result_df.to_pickle(os.path.join(const.TEMP_PATH, '20191216_jfe_article_information.pkl'))
