import asynctest
import json
from asynctest.mock import patch
from asynctest.mock import call


class TestSetChannelTopic(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        patcher2 = patch('charlesbot.slack.slack_connection.SlackConnection.api_call')  # NOQA
        self.addCleanup(patcher2.stop)
        self.mock_api_call = patcher2.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])

    def test_topic_channel_not_set(self):
        self.rd_lock.topic_channel = None
        yield from self.rd_lock.set_channel_topic(True)
        self.assertEqual(self.mock_api_call.mock_calls, [])

    def test_topic_channel_id_already_set(self):
        self.rd_lock.locked_by_user = "bob"
        self.rd_lock.topic_channel = "chan1"
        self.rd_lock.topic_channel_id = "C1234"
        yield from self.rd_lock.set_channel_topic(True)
        calls = [
            call("channels.setTopic",
                 channel="C1234",
                 topic=":lock: Rundeck executions locked by @bob :lock:")
        ]
        self.assertEqual(self.mock_api_call.mock_calls, calls)

    def test_topic_channel_not_found(self):
        channels = {
            "ok": True,
            "channels": [
                {
                    "name": "chan1",
                },
                {
                    "name": "chan2",
                },
                {
                    "name": "chan3",
                },
            ]
        }
        self.rd_lock.locked_by_user = "bob"
        self.rd_lock.topic_channel = "chan4"
        self.mock_api_call.side_effect = [json.dumps(channels), None]
        yield from self.rd_lock.set_channel_topic(True)
        calls = [
            call("channels.list", exclude_archived=1),
        ]
        self.assertEqual(self.mock_api_call.mock_calls, calls)

    def test_topic_channel_found(self):
        channels = {
            "ok": True,
            "channels": [
                {
                    "name": "chan1",
                    "id": "C1",
                },
                {
                    "name": "chan2",
                    "id": "C2",
                },
                {
                    "name": "chan3",
                    "id": "C3",
                },
            ]
        }
        self.rd_lock.locked_by_user = "bob"
        self.rd_lock.topic_channel = "chan2"
        self.mock_api_call.side_effect = [json.dumps(channels), None]
        yield from self.rd_lock.set_channel_topic(False)
        calls = [
            call("channels.list", exclude_archived=1),
            call("channels.setTopic",
                 channel="C2",
                 topic="")
        ]
        self.assertEqual(self.mock_api_call.mock_calls, calls)
