import asynctest
from asynctest.mock import patch
from asynctest.mock import CoroutineMock
from asynctest.mock import call
from charlesbot.slack.slack_message import SlackMessage
from charlesbot_rundeck.rundeck_job import RundeckJob


class TestPrintLockStatus(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])
        self.rd_lock.slack.send_channel_message = CoroutineMock()
        self.rd_lock.trigger_rundeck_executions_allowed_update = CoroutineMock()  # NOQA
        self.sm = SlackMessage(channel="sixchan")

    def test_empty_job_list(self):
        self.rd_lock.rundeck_jobs = []
        expected_slack_msg_raw = []
        expected_slack_msg_raw.append("*Rundeck Job Lock Report*")
        expected_slack_msg_raw.append("```")
        expected_slack_msg_raw.append("```")
        expected_slack_msg = "\n".join(expected_slack_msg_raw)
        expected_call = call("sixchan", expected_slack_msg)
        yield from self.rd_lock.print_lock_status(self.sm)
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         [expected_call])

    def test_single_enabled_job(self):
        self.rd_lock.rundeck_jobs = [
            RundeckJob(friendly_name="job1", execution_enabled=True)
        ]
        expected_slack_msg_raw = []
        expected_slack_msg_raw.append("*Rundeck Job Lock Report*")
        expected_slack_msg_raw.append("```")
        expected_slack_msg_raw.append("job1: unlocked")
        expected_slack_msg_raw.append("```")
        expected_slack_msg = "\n".join(expected_slack_msg_raw)
        expected_call = call("sixchan", expected_slack_msg)
        yield from self.rd_lock.print_lock_status(self.sm)
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         [expected_call])

    def test_single_disabled_job(self):
        self.rd_lock.rundeck_jobs = [
            RundeckJob(friendly_name="job1", execution_enabled=False)
        ]
        expected_slack_msg_raw = []
        expected_slack_msg_raw.append("*Rundeck Job Lock Report*")
        expected_slack_msg_raw.append("```")
        expected_slack_msg_raw.append("job1: locked")
        expected_slack_msg_raw.append("```")
        expected_slack_msg = "\n".join(expected_slack_msg_raw)
        expected_call = call("sixchan", expected_slack_msg)
        yield from self.rd_lock.print_lock_status(self.sm)
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         [expected_call])

    def test_multiple_mixed_jobs(self):
        self.rd_lock.rundeck_jobs = [
            RundeckJob(friendly_name="job1", execution_enabled=False),
            RundeckJob(friendly_name="job3", execution_enabled=True),
            RundeckJob(friendly_name="job2", execution_enabled=False)
        ]
        expected_slack_msg_raw = []
        expected_slack_msg_raw.append("*Rundeck Job Lock Report*")
        expected_slack_msg_raw.append("```")
        expected_slack_msg_raw.append("job1: locked")
        expected_slack_msg_raw.append("job3: unlocked")
        expected_slack_msg_raw.append("job2: locked")
        expected_slack_msg_raw.append("```")
        expected_slack_msg = "\n".join(expected_slack_msg_raw)
        expected_call = call("sixchan", expected_slack_msg)
        yield from self.rd_lock.print_lock_status(self.sm)
        self.assertEqual(self.rd_lock.slack.send_channel_message.mock_calls,
                         [expected_call])
