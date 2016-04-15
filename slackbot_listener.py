import calendar
import ConfigParser
import importlib
import json
import socket
import sys
import time
import traceback
import unicodedata
from slackutil.my_slackclient import my_slackclient
from slackutil.slackbot_handler import slackbot_handler
from time import strftime

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.abspath(__file__)))

class slackbot_listener(object):

    def __init__(self, ini_file):
        self._config = ConfigParser.ConfigParser()
        self._config.read(ini_file)

    def _get_lock(self):
        global lock_socket
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            lock_socket.bind('\0' + self._config.get('Configuration', 'daemon_name'))
        except socket.error:
            sys.exit()

    def run(self):
        self._get_lock()

        modules_location = self._config.get('Configuration', 'modules_location')
        handlers = []
        for handler_name in self._config.get('Configuration', 'handler_list').split():
            this_class = getattr(importlib.import_module(modules_location + '.' + handler_name), handler_name)
            handlers.append(this_class(self._config))

        slackclient = my_slackclient(self._config.get('Configuration', 'token'))

        myself = None
        json_data = json.loads(slackclient.api_call('auth.test'))
        if 'ok' in json_data and 'user_id' in json_data:
            myself = json_data['user_id']
        if myself:
            print "myself: " + myself
        else:
            print "error getting user_id of bot"

        helpmessage = ''
        for handler in handlers:
            name = handler.get_handler_name()
            commands, examples = handler.get_commands_and_examples()
            helpmessage += '*' + name + '*\n'
            for command in commands:
                helpmessage += '\t' + command + '\n'

        helpmessage += '\nExamples:\n'

        for handler in handlers:
            commands, examples = handler.get_commands_and_examples()
            for example in examples:
                helpmessage += '\t`' + example + '`\n'

        keywords = self._config.get('Configuration', 'keywords').split()
        helpword = self._config.get('Configuration', 'helpword')
        adminword = self._config.get('Configuration', 'adminword')
        adminusers = self._config.get('Configuration', 'adminusers').split()
        broadcast_text = None

        while True:
            time_now = calendar.timegm(time.gmtime())
            print "connecting at time " + str(time_now)
            if slackclient.rtm_connect():
                print "connected"
                while True:
                    sys.stdout.flush()
                    data = slackclient.rtm_read()
                    if data:
                        for item in data:
                            channel = None
                            text = None
                            user = None
                            edited = False
                            if ('type' in item and item['type'] == 'message') and ('channel' in item):
                                channel = item['channel']
                                if ('subtype' in item and item['subtype'] == 'message_changed') and ('message' in item and 'text' in item['message'] and 'type' in item['message'] and item['message']['type'] == 'message' and 'user' in item['message'] and item['message']['user'] != myself):
                                    text = item['message']['text']
                                    user = item['message']['user']
                                    edited = True
                                elif 'text' in item and 'user' in item and item['user'] != myself:
                                    text = item['text']
                                    user = item['user']
                                if text:
                                    found = False if keywords else True
                                    for keyword in keywords:
                                        if text == keyword or text.startswith(keyword + ' '):
                                            found = True
                                            break

                                    if found:
                                        user = slackclient.get_user(user)
                                    else:
                                        text = None

                            if channel and text and user and not user['is_bot']:
                                text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
                                if int(float(item['ts'])) >= time_now:
                                    tokens = text.split()
                                    if text in keywords and helpword:
                                        slackclient.show_is_typing(channel)
                                        slackclient.post_message(channel, 'Please follow `' + text + '` with a command.  Use `' + text + ' ' + helpword + '` to show available commands.')
                                    elif keywords and tokens[1] == helpword:
                                        slackclient.show_is_typing(channel)
                                        slackclient.post_message(channel, helpmessage);

                                    elif adminword and ((keywords and tokens[1] == adminword) or (not keywords and tokens[0] == adminword)) and user['name'] in
                                        if keywords:
                                            del tokens[0]
                                        del tokens[0]
                                        if tokens[0] == '__preview__':
                                            del tokens[0]
                                            broadcast_text = ' '.join(tokens)
                                            if not broadcast_text:
                                                broadcast_text = None
                                            else:
                                                slackclient.post_message(channel, 'PREVIEW: ' + broadcast_text)
                                        elif broadcast_text and tokens[0] == '__broadcast__':
                                            new_slackclient = my_slackclient(self._config.get('Configuration', 'token'))
                                            reply = new_slackclient.server.api_requester.do(self._config.get('Configuration', 'token'), "rtm.start")
                                            if reply.code == 200:
                                                login_data = json.loads(reply.read().decode('utf-8'))
                                                if login_data["ok"]:
                                                    channels = []
                                                    for c in login_data['channels']:
                                                        if c['is_member']:
                                                            channels.append(c)
                                                    channels.extend(login_data['groups'])
                                                    channels.extend(login_data['ims'])
                                                    for c in channels:
                                                        slackclient.post_message(c['id'], broadcast_text)
                                                    broadcast_text = None

                                    else:
                                        if keywords:
                                            slackclient.show_is_typing(channel)
                                            slackclient.post_message(channel, '@' + user['name'] + ', I am working on your request: `' + text + '`')
                                            print '[' + strftime("%Y-%m-%d %H:%M:%S") + ']: received on ' + channel + ' from @' + user['name'] + ': ' + text
                                            sys.stdout.flush()

                                        handled = False
                                        error = False
                                        for handler in handlers:
                                            if handler.can_handle(text, tokens, edited):
                                                slackclient.show_is_typing(channel)
                                                handled = True
                                                try:
                                                    print '[' + strftime("%Y-%m-%d %H:%M:%S") + ']: ' + handler.get_handler_name() + ' to handle request on ' + channel + ' from @' + user['name'] + ': ' + text
                                                    sys.stdout.flush()
                                                    error = handler.handle(text, tokens, slackclient, channel, user)
                                                except Exception as e:
                                                    error = True
                                                    traceback.print_exc()
                                                break
                                        if error:
                                            slackclient.post_message(channel, 'Sorry, I encountered an error handling your request!')
                                        if keywords and not handled:
                                            slackclient.post_message(channel, 'Sorry, I didn\'t recognize `' + tokens[1] + '`.  Please use `' + tokens[0] + ' ' + helpword + '` for a list of commands.')

                    time.sleep(0.5)
            else:
                print 'connection failed, invalid token?'
                break
            print 'exited loop, sleeping 5 seconds'
            time.sleep(5)
