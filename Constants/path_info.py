#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: path_info
# @Date: 2019/12/16
# @Author: Mark Wang
# @Email: wangyouan@gamil.com

import os


class PathInfo(object):
    ROOT_PATH = '/home/zigan/Documents/wangyouan/study/AnalyzeTopJournal'
    DATA_PATH = os.path.join(ROOT_PATH, 'data')
    TEMP_PATH = os.path.join(ROOT_PATH, 'temp')
    RESULT_PATH = os.path.join(ROOT_PATH, 'output')
