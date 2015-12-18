import asynctest
from asynctest.mock import patch


class TestLoadRundeckJobs(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_lock.RundeckLock.seed_job_list')  # NOQA
        self.addCleanup(patcher1.stop)
        self.mock_seed_job_list = patcher1.start()

        patcher2 = patch('charlesbot_rundeck.rundeck_lock.RundeckJob.retrieve_rundeck_job_info')  # NOQA
        self.addCleanup(patcher2.stop)
        self.mock_rundeck_job = patcher2.start()

        from charlesbot_rundeck.rundeck_lock import RundeckLock
        self.rd_lock = RundeckLock("token",
                                   "url",
                                   "channel",
                                   [])

    def test_empty_raw_job_list(self):
        self.rd_lock.rd_jobs_raw_list = []
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(self.rd_lock.rundeck_jobs, [])

    def test_friendly_name_key_not_present(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "key1": "val1",
            }
        ]
        with self.assertRaises(KeyError):
            yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(self.rd_lock.rundeck_jobs, [])

    def test_single_unsuccessful_job(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "friendly_name": "fname1",
                "project": "project1",
                "name": "name1",
            }
        ]
        self.mock_rundeck_job.side_effect = [False]
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(self.rd_lock.rundeck_jobs, [])

    def test_multiple_mixed_success_job_1(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "friendly_name": "fname1",
                "project": "project1",
                "name": "name1",
            },
            {
                "friendly_name": "fname2",
                "project": "project2",
                "name": "name2",
            },
            {
                "friendly_name": "fname3",
                "project": "project3",
                "name": "name3",
            },
        ]
        self.mock_rundeck_job.side_effect = [True, False, True]
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(len(self.rd_lock.rundeck_jobs), 2)

    def test_multiple_mixed_success_job_2(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "friendly_name": "fname1",
                "project": "project1",
                "name": "name1",
            },
            {
                "friendly_name": "fname2",
                "project": "project2",
                "name": "name2",
            },
            {
                "friendly_name": "fname3",
                "project": "project3",
                "name": "name3",
            },
        ]
        self.mock_rundeck_job.side_effect = [False, True, True]
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(len(self.rd_lock.rundeck_jobs), 2)

    def test_multiple_mixed_success_job_3(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "friendly_name": "fname1",
                "project": "project1",
                "name": "name1",
            },
            {
                "friendly_name": "fname2",
                "project": "project2",
                "name": "name2",
            },
            {
                "friendly_name": "fname3",
                "project": "project3",
                "name": "name3",
            },
        ]
        self.mock_rundeck_job.side_effect = [True, True, False]
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(len(self.rd_lock.rundeck_jobs), 2)

    def test_multiple_successful_jobs(self):
        self.rd_lock.rd_jobs_raw_list = [
            {
                "friendly_name": "fname1",
                "project": "project1",
                "name": "name1",
            },
            {
                "friendly_name": "fname2",
                "project": "project2",
                "name": "name2",
            },
            {
                "friendly_name": "fname3",
                "project": "project3",
                "name": "name3",
            },
        ]
        self.mock_rundeck_job.side_effect = [True, True, True]
        yield from self.rd_lock.load_rundeck_jobs()
        self.assertEqual(len(self.rd_lock.rundeck_jobs), 3)
