from charlesbot.base_plugin import BasePlugin
from charlesbot.config import configuration
from charlesbot.util.parse import parse_msg_with_prefix
from charlesbot.util.parse import does_msg_contain_prefix
from charlesbot.slack.slack_user import SlackUser
from charlesbot.slack.slack_message import SlackMessage
from charlesbot.slack.slack_connection import SlackConnection
from charlesbot_rundeck.http import http_get_request
from charlesbot_rundeck.http import http_post_request
import asyncio
import json
import logging


class RundeckLock(object):

    def __init__(self, token, url, channel):
        self.log = logging.getLogger(__name__)
        self.rundeck_token = token
        self.rundeck_url = url
        self.topic_channel = channel
        self.topic_channel_id = None
        self.slack = SlackConnection()
        self.locked_by_user = ""

    @asyncio.coroutine
    def toggle_rundeck_lock(self, slack_message):
        """
        Coordinating function to toggle the Rundeck lock from open to locked,
        or visa versa. This is the user-triggered function.
        """
        slack_user = SlackUser()
        yield from slack_user.retrieve_slack_user_info(self.slack,
                                                       slack_message.user)

        if not self.is_user_authorized_to_lock(slack_user):
            fail_msg = "Sorry <@%s>, you are not allowed to lock Rundeck executions"
            self.log.warn(fail_msg)
            yield from self.slack.send_channel_message(slack_message.channel,
                                                       full_slack_msg)
            return

        executions_allowed = yield from self.are_rundeck_executions_allowed()
        executions_allowed = not executions_allowed
        yield from self.toggle_rundeck_active_mode(slack_user, executions_allowed)
        self.log.info("Rundeck execution state enabled? %s" % str(executions_allowed))
        self.log.info("Rundeck execution state toggled by @%s" % slack_user.name)

        # To verify the current execution state
        executions_allowed = yield from self.are_rundeck_executions_allowed()

        full_slack_msg = self.get_execution_status_message(executions_allowed)
        yield from self.set_channel_topic(executions_allowed)
        yield from self.slack.send_channel_message(slack_message.channel,
                                                   full_slack_msg)

    @asyncio.coroutine
    def get_topic_channel_id(self):
        if not self.topic_channel:
            return None

        if self.topic_channel_id:
            return self.topic_channel_id

        channel_list = yield from self.slack.api_call('channels.list',
                                                      exclude_archived=1)
        json_list = json.loads(channel_list)
        for channel in json_list['channels']:
            if channel['name'] == self.topic_channel:
                self.topic_channel_id = channel['id']
                return self.topic_channel_id
        return None

    def get_locked_by_user(self):
        return self.locked_by_user

    @asyncio.coroutine
    def toggle_rundeck_active_mode(self, slack_user_obj, enable_active_mode=True):
        """
        Call the appropriate Rundeck endpoint to enable or disable active mode
        """
        if enable_active_mode:
            verb = "enable"
            self.locked_by_user = ""
        else:
            verb = "disable"
            self.locked_by_user = slack_user_obj.name

        url = "%s/api/14/system/executions/%s" % (self.rundeck_url, verb)
        headers = {
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": self.rundeck_token,
        }
        yield from http_post_request(url, headers)

    @asyncio.coroutine
    def are_rundeck_executions_allowed(self):
        """
        Return a truthy or falsy value, depending on whether rundeck executions
        are allowed
        """
        url = "%s/api/15/system/info" % self.rundeck_url
        headers = {
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": self.rundeck_token,
        }
        response = yield from http_get_request(url, headers)
        return response.get('system', {}).get('executions', {}).get('active', False)

    def get_execution_status_message(self, executions_allowed):
        """
        Return an appropriate user-facing message
        """
        locked_by_user = self.get_locked_by_user()
        if executions_allowed:
            return "Rundeck executions enabled! :white_check_mark:"
        return ":lock: Rundeck executions locked by <@%s> :lock:" % locked_by_user

    @asyncio.coroutine
    def set_channel_topic(self, executions_allowed):
        topic_channel_id = yield from self.get_topic_channel_id()
        locked_by_user = self.get_locked_by_user()
        if not topic_channel_id:
            return
        topic_message = ""
        if not executions_allowed:
            topic_message = ":lock: Rundeck executions locked by @%s :lock:" % locked_by_user
        yield from self.slack.api_call('channels.setTopic',
                                       channel=topic_channel_id,
                                       topic=topic_message)

    @asyncio.coroutine
    def print_lock_status(self, slack_message):
        """
        Print the status of the Rundeck lock (whether open or locked)
        """
        executions_allowed = yield from self.are_rundeck_executions_allowed()
        out_message = self.get_execution_status_message(executions_allowed)
        yield from self.slack.send_channel_message(slack_message.channel,
                                                   out_message)

    def is_user_authorized_to_lock(self, slack_user_obj):
        """
        Returns True or False, depending on whether this user is authorized to
        lock rundeck executions.
        """
        return slack_user_obj.is_admin
