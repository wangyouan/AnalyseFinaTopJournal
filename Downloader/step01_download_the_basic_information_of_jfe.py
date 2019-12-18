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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from Constants import Constants as const


def check_if_element_exits(element, wait_time, by, address):
    start_time = time.time()
    while time.time() - start_time < wait_time:
        elements = element.find_elements(by=by, value=address)
        if len(elements) != 0:
            return True
        time.sleep(0.1)

    return False


def check_if_article_preview_exist(article_tag_element, wait_time=10):
    return check_if_element_exits(article_tag_element, wait_time, By.CLASS_NAME, 'article-preview-body')


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
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'js-article-title'))
            WebDriverWait(driver, 10).until(element_present)
            driver.find_elements_by_class_name('js-article-list-item')
            article_list = driver.find_elements_by_class_name('js-article-list-item')

            for _ in range(3):
                try:
                    for article_tag in article_list[1:]:
                        article_dict = result_dict.copy()
                        article_content = article_tag.find_element_by_class_name('js-article')
                        if not check_if_element_exits(article_content, 2, By.CLASS_NAME, 'js-article-subtype'):
                            continue
                        article_type = article_content.find_element_by_class_name('js-article-subtype')
                        if article_type.text != 'Research article':
                            continue
                        article_dict[const.TITLE] = article_content.find_element_by_class_name('js-article-title').text
                        article_dict[const.URL] = article_content.find_element_by_tag_name(
                            'dt').find_element_by_tag_name('a').get_attribute('href')
                        article_dict[const.PAGE] = article_content.find_element_by_class_name(
                            'js-article-page-range').text
                        div_list = article_content.find_elements_by_tag_name('div')
                        article_dict[const.AUTHOR] = div_list[0].text
                        article_tag.find_element_by_tag_name('button').click()

                        if check_if_article_preview_exist(article_tag, 10):
                            article_dict[const.ABSTRACT] = article_content.find_elements_by_tag_name('div')[-1].text
                            article_dict[const.DOI] = article_tag.find_elements_by_tag_name('div')[1].get_attribute(
                                'textContent')

                        result_df: DataFrame = result_df.append(article_dict, ignore_index=True)
                    time.sleep(1)
                except StaleElementReferenceException as e:
                    time.sleep(1)
                    article_list = driver.find_elements_by_class_name('js-article-list-item')

                else:
                    break

            else:
                print('Cannot load volume {} issue {}'.format(volume, issue))

    driver.quit()
    result_df.to_pickle(os.path.join(const.TEMP_PATH, '20191216_jfe_article_information.pkl'))
    result_df.to_excel(os.path.join(const.RESULT_PATH, '20191218_jfe_basic_information.xlsx'), index=False)
