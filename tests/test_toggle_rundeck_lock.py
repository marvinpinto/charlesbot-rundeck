import asynctest
from asynctest.mock import patch
from asynctest.mock import CoroutineMock
from asynctest.mock import call
from charlesbot.slack.slack_user import SlackUser
from charlesbot.slack.slack_message import SlackMessage
from charlesbot_rundeck.rundeck_job import RundeckJob


class TestToggleRundeckLock(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])

        self.rd_lock.rundeck_jobs = [RundeckJob(friendly_name="job1")]
        self.rd_lock.populate_slack_user_object = CoroutineMock()
        self.rd_lock.slack.send_channel_message = CoroutineMock()
        self.rd_lock.lock_or_unlock_rundeck_job = CoroutineMock()
        self.rd_lock.set_channel_topic = CoroutineMock()
        self.rd_lock.print_lock_status = CoroutineMock()
        self.sm = SlackMessage(user="bob", channel="C001")
        self.su = SlackUser(name="suser", is_admin=True)

    def test_unauthorized_user(self):
        self.su.is_admin = False
        self.rd_lock.populate_slack_user_object.side_effect = [self.su]
        yield from self.rd_lock.toggle_rundeck_lock(self.sm, True)
        calls = [
            call("C001", "Sorry <@suser>, you are not allowed to lock Rundeck executions.")  # NOQA
        ]
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         calls)

    def test_authorized_user_unlock(self):
        self.rd_lock.populate_slack_user_object.side_effect = [self.su]
        yield from self.rd_lock.toggle_rundeck_lock(self.sm, False)
        self.assertEqual(self.rd_lock.set_channel_topic.mock_calls,
                         [call(False)])
        send_channel_msg_calls = [
	    call("C001", ":white_check_mark: Rundeck executions enabled! :white_check_mark:")  # NOQA
        ]
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         send_channel_msg_calls)
        self.assertEqual(self.rd_lock.print_lock_status.mock_calls,
                         [call(self.sm)])

    def test_authorized_user_lock(self):
        self.rd_lock.populate_slack_user_object.side_effect = [self.su]
        yield from self.rd_lock.toggle_rundeck_lock(self.sm, True)
        self.assertEqual(self.rd_lock.set_channel_topic.mock_calls,
                         [call(True)])
        send_channel_msg_calls = [
            call("C001", ":lock: Rundeck executions locked by <@suser> :lock:")
        ]
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         send_channel_msg_calls)
        self.assertEqual(self.rd_lock.print_lock_status.mock_calls,
                         [call(self.sm)])
