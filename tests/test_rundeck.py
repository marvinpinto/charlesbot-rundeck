import asynctest
from asynctest.mock import patch
from asynctest.mock import call
from asynctest.mock import MagicMock
from asynctest.mock import CoroutineMock
from charlesbot.slack.slack_message import SlackMessage


class TestRundeck(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck.Rundeck.load_config')
        self.addCleanup(patcher1.stop)
        self.mock_load_config = patcher1.start()

        from charlesbot_rundeck.rundeck import Rundeck
        self.rd = Rundeck()
        self.rd.rundeck_lock = MagicMock()
        self.rd.rundeck_lock.toggle_rundeck_lock = CoroutineMock()
        self.rd.rundeck_lock.print_lock_status = CoroutineMock()

    @asynctest.ignore_loop
    def test_help_msg_three_entries(self):
        help_msg = self.rd.get_help_message()
        self.assertEqual(help_msg.count('\n'), 2)

    def test_process_message_non_slack_message(self):
        message = "!lock and key"
        yield from self.rd.process_message(message)
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         [])
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_non_lock_message(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="Don't lock me out")
        yield from self.rd.process_message(message)
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         [])
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_lock_with_no_arguments(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="!lock")
        yield from self.rd.process_message(message)
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         [])
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_lock_with_invalid_argument(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="!lock please")
        yield from self.rd.process_message(message)
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         [])
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_lock_acquire(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="!lock acquire")
        yield from self.rd.process_message(message)
        expected_calls = [
            call(message, lock_job=True)
        ]
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         expected_calls)
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_lock_release(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="!lock release")
        yield from self.rd.process_message(message)
        expected_calls = [
            call(message, lock_job=False)
        ]
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         expected_calls)
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls, [])

    def test_process_message_lock_status(self):
        message = SlackMessage(type="message",
                               user="U001",
                               channel="C001",
                               text="!lock status")
        yield from self.rd.process_message(message)
        expected_calls = [
            call(message)
        ]
        self.assertEqual(self.rd.rundeck_lock.toggle_rundeck_lock.mock_calls,
                         [])
        self.assertEqual(self.rd.rundeck_lock.print_lock_status.mock_calls,
                         expected_calls)
