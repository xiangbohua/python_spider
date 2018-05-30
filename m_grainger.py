#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import configparser
import os

from m_base import MBase
from tool import mkDir


class Grainer(MBase):
    def getMark(self):
        return 'grainer'

    def getRootUrl(self):
        return 'https://www.grainger.cn/'

