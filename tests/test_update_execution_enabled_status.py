import asynctest
from asynctest.mock import patch
from charlesbot_rundeck.rundeck_job import RundeckJob


class TestUpdateExecutionEnabledStatus(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        patcher2 = patch('charlesbot_rundeck.rundeck_lock.http_get_request')
        self.addCleanup(patcher2.stop)
        self.mock_http_get_request = patcher2.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])

    def test_empty_task_list(self):
        self.rd_lock.rundeck_jobs = []
        yield from self.rd_lock.trigger_rundeck_executions_allowed_update()
        self.assertEqual(self.mock_http_get_request.mock_calls, [])

    def test_multiple_tasks_execution_disabled(self):
        rd_job1 = RundeckJob(friendly_name="job1")
        rd_job2 = RundeckJob(friendly_name="job2")
        self.rd_lock.rundeck_jobs = [
            rd_job1,
            rd_job2
        ]
        side_effect = [
            "<joblist><job><description></description><executionEnabled>false</executionEnabled></job></joblist>",  # NOQA
            "<joblist><job><description></description><executionEnabled>false</executionEnabled></job></joblist>",  # NOQA
        ]
        self.mock_http_get_request.side_effect = side_effect
        yield from self.rd_lock.trigger_rundeck_executions_allowed_update()
        self.assertFalse(rd_job1.execution_enabled)
        self.assertFalse(rd_job2.execution_enabled)

    def test_multiple_tasks_execution_enabled(self):
        rd_job1 = RundeckJob(friendly_name="job1")
        rd_job2 = RundeckJob(friendly_name="job2")
        self.rd_lock.rundeck_jobs = [
            rd_job1,
            rd_job2
        ]
        side_effect = [
            "<joblist><job><description></description><executionEnabled>true</executionEnabled></job></joblist>",  # NOQA
            "<joblist><job><description></description><executionEnabled>true</executionEnabled></job></joblist>",  # NOQA
        ]
        self.mock_http_get_request.side_effect = side_effect
        yield from self.rd_lock.trigger_rundeck_executions_allowed_update()
        self.assertTrue(rd_job1.execution_enabled)
        self.assertTrue(rd_job2.execution_enabled)

    def test_multiple_tasks_mixed_execution_states(self):
        rd_job1 = RundeckJob(friendly_name="job1")
        rd_job2 = RundeckJob(friendly_name="job2")
        rd_job3 = RundeckJob(friendly_name="job3")
        rd_job4 = RundeckJob(friendly_name="job4")
        self.rd_lock.rundeck_jobs = [
            rd_job1,
            rd_job2,
            rd_job3,
            rd_job4
        ]
        side_effect = [
            "<joblist><job><description></description><executionEnabled>true</executionEnabled></job></joblist>",  # NOQA
            "<joblist><job><description></description><executionEnabled>true</executionEnabled></job></joblist>",  # NOQA
            "<joblist><job><description></description><executionEnabled>true</executionEnabled></job></joblist>",  # NOQA
            "<joblist><job><description></description><executionEnabled>false</executionEnabled></job></joblist>",  # NOQA
        ]
        self.mock_http_get_request.side_effect = side_effect
        yield from self.rd_lock.trigger_rundeck_executions_allowed_update()
        self.assertTrue(rd_job1.execution_enabled)
        self.assertTrue(rd_job2.execution_enabled)
        self.assertTrue(rd_job3.execution_enabled)
        self.assertFalse(rd_job4.execution_enabled)
