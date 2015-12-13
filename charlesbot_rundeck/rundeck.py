from charlesbot.base_plugin import BasePlugin
from charlesbot.config import configuration
from charlesbot.util.parse import parse_msg_with_prefix
from charlesbot.util.parse import does_msg_contain_prefix
from charlesbot.slack.slack_message import SlackMessage
from charlesbot_rundeck.rundeck_lock import RundeckLock
import asyncio


class Rundeck(BasePlugin):

    def __init__(self):
        super().__init__("Rundeck")
        self.load_config()
        self.rundeck_lock = RundeckLock(self.rundeck_token,
                                        self.rundeck_url,
                                        self.topic_channel,
                                        self.rd_jobs_raw_list)

    def load_config(self):  # pragma: no cover
        config_dict = configuration.get()
        self.rundeck_token = config_dict['rundeck']['token']
        self.rundeck_url = config_dict['rundeck']['url']
        try:
            # It's okay if this key isn't set
            self.topic_channel = config_dict['rundeck']['deployment_status_channel']  # NOQA
        except KeyError:
            self.topic_channel = None
        self.rd_jobs_raw_list = config_dict['rundeck']['lock_jobs']

    def get_help_message(self):
        help_msg = []
        help_msg.append("!lock status - Prints the status of the Rundeck deployment lock")  # NOQA
        help_msg.append("!lock acquire - Acquires the Rundeck deployment lock (only available to Slack admins)")  # NOQA
        help_msg.append("!lock release - Releases the Rundeck deployment lock (only available to Slack admins)")  # NOQA
        return "\n".join(help_msg)

    @asyncio.coroutine
    def process_message(self, message):
        """
        Main method that handles all messages sent to this plugin
        """
        if not type(message) is SlackMessage:
            return

        parsed_message = parse_msg_with_prefix("!lock", message.text)
        if not parsed_message:  # pragma: no cover
            return

        if does_msg_contain_prefix("acquire", parsed_message):
            yield from self.rundeck_lock.toggle_rundeck_lock(message,
                                                             lock_job=True)
        elif does_msg_contain_prefix("release", parsed_message):
            yield from self.rundeck_lock.toggle_rundeck_lock(message,
                                                             lock_job=False)
        elif does_msg_contain_prefix("status", parsed_message):
            yield from self.rundeck_lock.print_lock_status(message)
