import calendar
import json
import random
import socket
import sys
import time
import urllib2
from abc import ABCMeta, abstractmethod

class slackbot_handler(object):
    __metaclass__  = ABCMeta

    def __init__(self, config):
        self._config = config

    @staticmethod
    def _run_command(command):
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    @staticmethod
    def _get_json_data_through_rest_get(url, timeout = 30):
        try:
            json_data = urllib2.urlopen(urllib2.Request(url), timeout=timeout).read()
            if (json_data):
                return json.loads(json_data)
            return None
        except Exception as e:
            return None

    @staticmethod
    def _get_json_data_through_authenticated_rest_get(url, username, password, timeout = 30):
        try:
            req = urllib2.Request(url)
            req.add_header('Authorization', "Basic " + (username + ':' + password).encode('base64').rstrip())
            json_data = urllib2.urlopen(req, timeout=timeout).read()
            if (json_data):
                return json.loads(json_data)
            return None
        except Exception as e:
            return None

    def _download_file(self, url, extension, timeout = 30):
        filename = '/tmp/' + self.get_handler_name() + '-' + str(calendar.timegm(time.gmtime())) + '-' + str(random.randint(1, sys.maxint)) + '.' + extension;
        try:
            data = urllib2.urlopen(urllib2.Request(url), timeout=timeout).read()
            with open(filename, "wb") as destfile:
                destfile.write(data)
            return filename
        except:
            return None

    @abstractmethod
    def get_handler_name(self):
        pass

    @abstractmethod
    def get_commands_and_examples(self):
        pass

    @abstractmethod
    def can_handle(self, fulltext, tokens, edited):
        pass

    @abstractmethod
    def handle(self, fulltext, tokens, slackclient, channel, user):
        pass
