import asynctest
from asynctest.mock import patch
from asynctest.mock import call
from charlesbot_rundeck.rundeck_job import RundeckJob


class TestLockUnlockRundeckJob(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        patcher2 = patch('charlesbot_rundeck.rundeck_lock.http_post_request')
        self.addCleanup(patcher2.stop)
        self.mock_http_post_request = patcher2.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])
        self.rd_job = RundeckJob(execution_enabled=False,
                                 href="job.com")
        self.headers = {
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": "token",
        }

    def test_lock_invalid_response(self):
        self.mock_http_post_request.side_effect = [""]
        yield from self.rd_lock.lock_or_unlock_rundeck_job(self.rd_job, True)
        calls = [
            call("job.com/execution/disable", self.headers)
        ]
        self.assertFalse(self.rd_job.execution_enabled)
        self.assertEqual(self.mock_http_post_request.mock_calls, calls)

    def test_lock_valid_response(self):
        self.mock_http_post_request.side_effect = ["200"]
        yield from self.rd_lock.lock_or_unlock_rundeck_job(self.rd_job, True)
        calls = [
            call("job.com/execution/disable", self.headers)
        ]
        self.assertTrue(self.rd_job.execution_enabled)
        self.assertEqual(self.mock_http_post_request.mock_calls, calls)

    def test_unlock_valid_response(self):
        self.rd_job.execution_enabled = True
        self.mock_http_post_request.side_effect = ["200"]
        yield from self.rd_lock.lock_or_unlock_rundeck_job(self.rd_job, False)
        calls = [
            call("job.com/execution/enable", self.headers)
        ]
        self.assertFalse(self.rd_job.execution_enabled)
        self.assertEqual(self.mock_http_post_request.mock_calls, calls)
