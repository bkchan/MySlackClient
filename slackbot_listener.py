import ConfigParser
import importlib
from slackutil.my_slackclient import my_slackclient
from slackutil.slackbot_handler import slackbot_handler

#if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.abspath(__file__)))

class slackbot_listener(object):

    def __init__(self, ini_file):
        self.config = ConfigParser.ConfigParser()       
        self.config.read(ini_file)

    def _get_lock(self):
        global lock_socket
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            lock_socket.bind('\0' + self.config.get('Configuration', 'daemon_name'))
        except socket.error:
            sys.exit()

    def run():
        self._get_lock()
        modules_location = self.config.get('Configuration', 'modules_location')
        handlers = []
        for handler_name in self.config.get('Configuration', 'handler_list').split():
            this_class = getattr(importlib.import_module(modules_location + '.' + handler_name), handler_name)
            handlers.append(this_class(self.config)
        token = self.config.get('Configuration', 'token')
        slackclient = my_slackclient(self.token)
