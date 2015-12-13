from charlesbot.base_plugin import BasePlugin
from charlesbot.config import configuration
from charlesbot.util.parse import parse_msg_with_prefix
from charlesbot.util.parse import does_msg_contain_prefix
from charlesbot.slack.slack_user import SlackUser
from charlesbot.slack.slack_message import SlackMessage
from charlesbot.slack.slack_connection import SlackConnection
from charlesbot_rundeck.http import http_get_request
from charlesbot_rundeck.http import http_get_xml_request
from charlesbot_rundeck.http import http_post_request
import xml.etree.ElementTree as etree
import asyncio
import json
import logging


class RundeckLock(object):

    def __init__(self, token, url, channel, jobs):
        self.log = logging.getLogger(__name__)
        self.rundeck_token = token
        self.rundeck_url = url
        self.topic_channel = channel
        self.topic_channel_id = None
        self.slack = SlackConnection()
        self.locked_by_user = ""
        self.rundeck_jobs = jobs

    @asyncio.coroutine
    def toggle_rundeck_lock(self, slack_message, lock_job):
        """
        Coordinating function to toggle the Rundeck lock from open to locked,
        or visa versa. This is the user-triggered function.
        """
        slack_user = SlackUser()
        yield from slack_user.retrieve_slack_user_info(self.slack,
                                                       slack_message.user)

        if not self.is_user_authorized_to_lock(slack_user):
            fail_msg = "Sorry <@%s>, you are not allowed to lock Rundeck executions." % slack_user.name
            self.log.warning(fail_msg)
            yield from self.slack.send_channel_message(slack_message.channel,
                                                       fail_msg)
            return
        self.locked_by_user = slack_user.name

        tasks = []
        for job in self.rundeck_jobs:
            tasks.append(self.lock_or_unlock_rundeck_job(job, lock_job))
        yield from asyncio.gather(*tasks)

        self.log.info("Rundeck jobs locked: %s" % lock_job)
        self.log.info("Job state toggled by @%s" % slack_user.name)

        # To verify the current execution state
        yield from self.trigger_rundeck_executions_allowed_update()

        full_slack_msg = self.get_execution_status_message(lock_job)
        yield from self.set_channel_topic(lock_job)
        yield from self.slack.send_channel_message(slack_message.channel,
                                                   full_slack_msg)
        yield from self.print_lock_status(slack_message)

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
    def lock_or_unlock_rundeck_job(self, rundeck_job_obj, lock_job):
        """
        Lock the job associated with this RundeckJob object
        """
        verb = "enable"
        if lock_job:
            verb = "disable"

        url = "%s/execution/%s" % (rundeck_job_obj.href, verb)
        headers = {
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": self.rundeck_token,
        }
        yield from http_post_request(url, headers)
        rundeck_job_obj.execution_enabled = lock_job

    @asyncio.coroutine
    def trigger_rundeck_executions_allowed_update(self):
        tasks = []
        for job in self.rundeck_jobs:
            tasks.append(self.update_rundeck_job_execution_enabled_status(job))
        yield from asyncio.gather(*tasks)

    @asyncio.coroutine
    def update_rundeck_job_execution_enabled_status(self, rundeck_job_obj):
        """
        Update the execution_enabled flag for this RundeckJob object to reflect
        reality
        """
        url = "%s" % rundeck_job_obj.href
        headers = {
            "Accept": "application/xml",  # As of Rundeck 2.6.2, this endpoint
                                          # does not return json :(
            "X-Rundeck-Auth-Token": self.rundeck_token,
        }
        response = yield from http_get_xml_request(url, headers)
        xml_root = etree.fromstring(response)
        execution_enabled = xml_root[0].find("executionEnabled").text
        rundeck_job_obj.execution_enabled = False
        if execution_enabled == "true":
            rundeck_job_obj.execution_enabled = True

    def get_execution_status_message(self, lock_job):
        """
        Return an appropriate user-facing message
        """
        locked_by_user = self.get_locked_by_user()
        if lock_job:
            return ":lock: Rundeck executions locked by <@%s> :lock:" % locked_by_user
        return "Rundeck executions enabled! :white_check_mark:"

    @asyncio.coroutine
    def set_channel_topic(self, lock_job):
        topic_channel_id = yield from self.get_topic_channel_id()
        locked_by_user = self.get_locked_by_user()
        if not topic_channel_id:
            return
        topic_message = ""
        if lock_job:
            topic_message = ":lock: Rundeck executions locked by @%s :lock:" % locked_by_user
        yield from self.slack.api_call('channels.setTopic',
                                       channel=topic_channel_id,
                                       topic=topic_message)

    @asyncio.coroutine
    def print_lock_status(self, slack_message):
        """
        Print the status of the Rundeck lock (whether open or locked)
        """
        yield from self.trigger_rundeck_executions_allowed_update()
        out_message = []
        out_message.append("*Rundeck Job Lock Report*")
        out_message.append("```")
        for job in self.rundeck_jobs:
            if job.execution_enabled:
                out_message.append("%s: No" % job.friendly_name)
            else:
                out_message.append("%s: Yes" % job.friendly_name)
        out_message.append("```")
        yield from self.slack.send_channel_message(slack_message.channel,
                                                   "\n".join(out_message))

    def is_user_authorized_to_lock(self, slack_user_obj):
        """
        Returns True or False, depending on whether this user is authorized to
        lock rundeck executions.
        """
        return slack_user_obj.is_admin
