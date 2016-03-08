import calendar
import json
import random
import socket
import sys
import time
import urllib
from abc import ABCMeta, abstractmethod

class slackbot_handler(object):
    __metaclass__  = ABCMeta

    def __init__(self, config):
        self.config = config

    @staticmethod
    def _run_command(command):
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    @staticmethod
    def get_json_data_through_rest(url, timeout = 30):
        socket.setdefaulttimeout(timeout)
        try:
            json_data = urllib.urlopen(url).read()
            if (json_data):
                return json.loads(json_data)
            return None
        except Exception as e:
            return None

    def _download_file(self, url, extension, timeout = 30):
        socket.setdefaulttimeout(timeout)
        filename = '/tmp/' + self.get_handler_name() + '-' + str(calendar.timegm(time.gmtime())) + '-' + str(random.randint(1, sys.maxint)) + '.' + extension;
        try:
            urllib.urlretrieve(url, filename)
            return filename
        except:
            return None

    @abstractmethod
    def get_handler_name(self):
        pass

    @abstractmethod
    def show_commands(self):
        pass

    @abstractmethod
    def can_handle(self, fulltext, tokens):
        pass

    @abstractmethod
    def handle(self, fulltext, tokens, slackclient, channel, user):
        pass
