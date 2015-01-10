import cgi
import json

from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from crawler.lib.data_store import create_job
from crawler.webapi_service.lib.job_queue import enqueue_crawling_job
from crawler.lib.misc_utils import remove_cr_and_lf
from crawler.lib.json_encoder import JobDataEncoder
from crawler.webapi_service.lib.url_parse_fsm import parse_linebreakless_url_str


class JobSubmissionResource(Resource):
    """
    URL: /

    This is not at all RESTful, but POSTing to the API's root-level endpoint
    is used to submit jobs. The body is a not form-encoded.

    The original test case for this project submitted URLs via curl such that
    there'd be no spaces or linebreaks between unique URLs. You'll see that
    we have to do our best with this, it's not fool-proof.

    Valid responses and errors are both returned with in JSON.
    """

    def __init__(self, broadcast_svc):
        Resource.__init__(self)

        self.broadcast_svc = broadcast_svc

    def render_POST(self, request):
        # Read their whole request body in at once. If we were serious, we'd
        # probably buffer this and make sure our front-facing proxy protects us.
        body = cgi.escape(request.content.read())
        # We aren't expecting CRs or LRs. Strip any out just in case.
        body = remove_cr_and_lf(body)
        # Do our best to figure out which URLs to crawl.
        urls_to_crawl = parse_linebreakless_url_str(body)
        create_job(urls_to_crawl)\
            .addCallback(self._handle_success, request)\
            .addErrback(self._handle_error, request)
        return NOT_DONE_YET

    def _handle_success(self, job_data, request):
        job_json = json.dumps(job_data, cls=JobDataEncoder)
        request.write(job_json)
        request.finish()
        # Create the job in the data store, announce the URLs to the workers.
        enqueue_crawling_job(
            self.broadcast_svc,
            job_data['id'],
            job_data['all_urls'],
            depth=0)
        log.msg("New job ({job_id}) created with {url_count} URL(s) enqueued.".format(
            job_id=job_data['id'], url_count=len(job_data['all_urls'])))

    def _handle_error(self, err, request):
        exc = err.trap(ValueError)
        if exc == ValueError:
            request.setResponseCode(400)
            error_json = json.dumps({
                'message': exc.message,
            })
        else:
            log.err("Error encountered when creating new job.")
            log.err(exc)

            request.setResponseCode(500)
            error_json = json.dumps({
                    'message': "An error was encountered while creating new job.",
            }, cls=JobDataEncoder)

        request.setHeader('Content-Type', 'application/json')
        request.write(error_json)
        request.finish()
