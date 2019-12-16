#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: __init__.py
# @Date: 2019/12/16
# @Author: Mark Wang
# @Email: wangyouan@gamil.com

from .url_info import URLInfo
from .path_info import PathInfo


class Constants(URLInfo, PathInfo):
    YEAR = 'year'
    VOLUME = 'volume'
    ISSUE = 'issue'
    MONTH = 'month'
    DOI = 'doi'
    TITLE = 'title'
    ABSTRACT = 'abstract'
    AUTHOR = 'author'
    URL = 'url'
    PAGE = 'page'
