# MySlackClient
Builds upon [SlackClient](https://github.com/slackhq/python-slackclient) for commonly used actions for bots.

* `post_message`: simply send a message to a channel as the user attached to the API token
* `show_is_typing`: using an undocumented RTM method, send a message to indicate that the bot is "typing"
* `get_user`: gets the name of a passed-in user ID; if not found, returns the passed-in user ID
* `upload_file`: uses curl to upload a local file as the bot; note that this occurs in a subprocess, so the file cannot be removed immediately
