import asynctest
from asynctest.mock import patch
import json


class TestRundeckJob(asynctest.TestCase):

    def setUp(self):
        patcher1 = patch('charlesbot_rundeck.rundeck_job.http_get_request')
        self.addCleanup(patcher1.stop)
        self.mock_http_get_request = patcher1.start()

        from charlesbot_rundeck.rundeck_job import RundeckJob
        self.rd_job = RundeckJob()

    def test_invalid_rundeck_json_response(self):
        self.mock_http_get_request.side_effect = ["{}"]
        success = yield from self.rd_job.retrieve_rundeck_job_info(
            "token",
            "baseurl",
            "project name",
            "job name"
        )
        self.assertFalse(success)

    def test_empty_rundeck_response(self):
        self.mock_http_get_request.side_effect = ["[]"]
        success = yield from self.rd_job.retrieve_rundeck_job_info(
            "token",
            "baseurl",
            "project name",
            "job name"
        )
        self.assertFalse(success)

    def test_single_rundeck_response(self):
        response = [
            {
                "id": "rd1",
                "name": "rundeckone",
            }
        ]
        self.mock_http_get_request.side_effect = [json.dumps(response)]
        success = yield from self.rd_job.retrieve_rundeck_job_info(
            "token",
            "baseurl",
            "project name",
            "job name"
        )
        self.assertTrue(success)
        self.assertEqual(self.rd_job.id, "rd1")
        self.assertEqual(self.rd_job.name, "rundeckone")
        self.assertEqual(self.rd_job.friendly_name, "")

    def test_multiple_rundeck_responses(self):
        response = [
            {
                "id": "rd1",
                "name": "rundeckone",
            },
            {
                "id": "rd2",
                "name": "rundecktwo",
            }
        ]
        self.mock_http_get_request.side_effect = [json.dumps(response)]
        success = yield from self.rd_job.retrieve_rundeck_job_info(
            "token",
            "baseurl",
            "project name",
            "job name"
        )
        self.assertFalse(success)
