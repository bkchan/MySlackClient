## slackutil

### Summary

`slackutil` is designed to be a suite of utilities to ease the task of writing a bot to interface with Slack in Python.

* [`my_slackclient`](my_slackclient.py) is an extension to the popular [SlackClient](https://github.com/slackhq/python-slackclient/tree/master/slackclient) that already abstracts most of the Slack APIs.
  * `post_message`: simply send a message to a channel as the user attached to the API token
  * `show_is_typing`: using an undocumented RTM method, send a message to indicate that the bot is "typing"
  * `get_user`: gets the name of a passed-in user ID; if not found, returns the passed-in user ID
  * `upload_file`: uses curl to upload a local file as the bot; note that this occurs in a subprocess, so the file cannot be removed immediately
* [`slackbot_handler`](slackbot_Handler.py) is an abstract base class that needs to implement just four methods to act as a handler for [`slackbot_listener`](slackbot_listener.py).
* [`slackbot_listener`](slackbot_listener.py) uses a specified configuration file to specify how the bot should respond.  The configuration file will specify handlers that will first be asked if it can handle the input and, if so, to handle the input.

### Dependencies

* Python on Linux (verified to work on Ubuntu and Python 2.7) -- this does not work on Windows or Python 3; will work to correct this, but my only use case is Ubuntu and Python 2.7
* [SlackClient](https://github.com/slackhq/python-slackclient/tree/master/slackclient) -- note that revisions since the the snapshot I took may have incompatible changes -- I will work to address this
* An .ini file whose structure will be defined below
* Handlers to be implemented by deriving from [`slackbot_handler`](slackbot_Handler.py)
* A Slack API key
* The ability to run the bot as a cronjob that runs every minute (it will check if it's already running and exit immediately if so)

### .ini File Format

The following must appear in a `[Configuration]` section, but other sections are possible, especially if there are configuration values for handlers.

* `token`: This is something available from Slack and is the key that Slack grants for bots.  (Note that the key for a regular user account shouldn't be used here.)
* `daemon_name`: This is a unique name for the bot.  [`slackbot_listener`](slackbot_listener.py) will connect to a UNIX socket with this name and fail if it does not get the socket because there is another process that has it -- this is a good mechanism for Python applications to check if they are running already on a Linux box.  This mechanism allows the bot to run as a cronjob so that it "wakes up" after a crash.
* `modules_location`: This is a subdirectory off your main application that will house all the code for handlers you may have.
* `handler_list`: This is a space-separated list of handlers that are in the directory specified by `modules_location`.  These handlers are checked in the specified order to handle incoming input.
* `keywords`: This is a space-separated list of possible keywords that the input must begin with in order to trigger the bot (there is one exception noted below).  If this list is empty, then [`slackbot_listener`](slackbot_listener.py) will attempt to evaluate all input.
* `helpword`: This is a single word that will trigger a listing of all available handlers and their commands as specified in the `get_commands_and_examples` method for each handler.  This will work only if there is at least one keyword specified in `keywords`.
* `adminword`: This is a single word that will trigger admin functionality with special arguemnts like `__preview__` and `__broadcast__` -- this will be triggered regardless of whether a keyword exists or not, so choose the `admin_word` wisely to avoid potential collisions with text normally used on this Slack team.
* `adminusers`: This is a space-separated list of usernames that are allowed the admin functionality.

### Handlers

The handler should be defined in a manner that the statement `from <modules_location>.<module_name> import <module_name>` will work, where `<modules_location>` is the relative directory specified in the .ini file and `<module_name>` is the name of the module.

* The constructor can take exactly one parameter, which is the name of the .ini file.  This must be passed to the parent class.
* `get_handler_name` returns the name of the handler for display purposes.
* `get_comamnds_and_examples` returns a tuple of two arrays; the first array are the possible commands while the second are possible examples.  This function is called when the helpword is triggered.
* `can_handle` indicates whether or not this handler is going to handle the input.
* `handle` handles the input to do something with it.
