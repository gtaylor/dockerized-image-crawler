from twisted.web.server import Site
from twisted.application import internet

from crawler.webapi_service.resources.job_detail import JobResource
from crawler.webapi_service.resources.root import RootResource


def get_web_service(broadcast_svc):

    root = RootResource(broadcast_svc)
    root.putChild("job", JobResource(broadcast_svc))
    factory = Site(root)
    factory.amqp = broadcast_svc
    # noinspection PyUnresolvedReferences
    webserver = internet.TCPServer(8000, factory)
    return webserver
