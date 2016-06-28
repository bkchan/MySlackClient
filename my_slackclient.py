import subprocess
from slackclient import SlackClient

class my_slackclient(SlackClient):

    def __init__(self, token):
        super(my_slackclient, self).__init__(token)

    @staticmethod
    def _run_command(command):
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    def post_message(self, channel, text):
        return self.api_call('chat.postMessage', channel = channel, text = text, as_user = True, unfurl_links = False, link_names = True)
        
    def update_message(self, channel, text, id):
        return self.api_call('chat.update', channel = channel, ts = id, text = text, as_user = True, unfurl_links = False, link_names = True)
        
    def delete_message(self, channel, ts):
        return self.api_call('chat.delete', channel = channel, ts = ts, as_user = True)

    def show_is_typing(self, channel):
        self.server.send_to_websocket({'type': 'typing', 'channel': channel, 'id': 1})

    def get_user(self, user):
        try:
            json_data = self.api_call('users.info', user = user)
            if 'ok' in json_data and json_data['ok'] and 'user' in json_data and 'name' in json_data['user']:
                return json_data['user']
        except Exception as e:
            pass
        return user

    def upload_file(self, channel, filename):
        command = 'curl -F file=@' + filename + ' -F channels=' + channel + ' -F token=' + self.token + ' https://slack.com/api/files.upload'
        self._run_command(command.split())
