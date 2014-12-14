"""
Web resources that are used to view job details.
"""

import json

from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from crawler.lib.data_store import get_job_data
from crawler.lib.json_encoder import JobDataEncoder


class JobResource(Resource):
    """
    URL: /job

    Since we don't POST to this endpoint, it will only ever be used for
    looking up jobs.
    """

    def __init__(self, broadcast_svc):
        Resource.__init__(self)

        self.broadcast_svc = broadcast_svc

    def getChild(self, path, request):
        return JobDetailResource(self.broadcast_svc, path)


# noinspection PyPep8Naming
class JobDetailResource(Resource):
    """
    URL: /job/<job-id-uuid>

    Retrieves a JSON dict of job data for the given ID.
    """

    def __init__(self, broadcast_svc, job_id):
        Resource.__init__(self)

        self.broadcast_svc = broadcast_svc
        self.job_id = job_id

    def render_GET(self, request):
        get_job_data(self.job_id)\
            .addCallback(self._handle_success, request)\
            .addErrback(self._handle_error, request)
        return NOT_DONE_YET

    def _handle_success(self, job_data, request):
        job_json = json.dumps(job_data, cls=JobDataEncoder)
        request.write(job_json)
        request.finish()

    def _handle_error(self, err, request):
        exc = err.trap(ValueError)
        if exc == ValueError:
            request.setResponseCode(404)
            error_json = json.dumps({
                    'message': "Invalid job ID.",
            })
            print "VALUERROR"
        else:
            log.err("Error encountered when retrieving job data.")
            log.err(exc)

            request.setResponseCode(500)
            error_json = json.dumps({
                    'message': "An error was encountered while retrieving job data.",
            }, cls=JobDataEncoder)

        request.setHeader('Content-Type', 'application/json')
        request.write(error_json)
        request.finish()
