from charlesbot.base_object import BaseObject
from charlesbot_rundeck.http import http_get_request
import asyncio
import json


class RundeckJob(BaseObject):

    properties = ['id',
                  'project',
                  'name',
                  'friendly_name',
                  'href',
                  'description',
                  'execution_enabled']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @asyncio.coroutine
    def retrieve_rundeck_job_info(self,
                                  rd_token,
                                  rd_baseurl,
                                  project_name,
                                  job_name):
        url = "%s/api/14/project/%s/jobs" % (rd_baseurl, project_name)
        headers = {
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": rd_token,
        }
        params = {
            "jobExactFilter": job_name,
        }
        result = yield from http_get_request(url, headers, params)
        result = json.loads(result)
        self.load(result[0])
