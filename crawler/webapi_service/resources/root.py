"""
It's kind of awkward to only have this module be devoted to one Resource,
but you'd conceivably expand this as the crawler grew.
"""

from twisted.web.resource import Resource

from crawler.webapi_service.resources.job_submission import \
    JobSubmissionResource


class RootResource(Resource):
    """
    The entrypoint for the URL routing.
    """

    def __init__(self, broadcast_svc):
        Resource.__init__(self)

        self.broadcast_svc = broadcast_svc

    def getChild(self, path, request):
        if not path:
            # Root-level: /
            return JobSubmissionResource(self.broadcast_svc)
