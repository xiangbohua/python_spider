#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import configparser
import os

from tool import mkDir


class Grainer(object):
    mainPage = None

    def __init__(self):
        self.url = 'http://www.vipmro.com'
        self.conf = configparser.ConfigParser()
        if not os.path.exists('conf.ini'):
            raise FileNotFoundError
        self.conf.read('conf.ini')

        self.base_path = self.getConfig('db_image_path')
        mkDir(self.base_path)


