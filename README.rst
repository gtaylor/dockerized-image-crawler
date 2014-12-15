Dockerized Image Crawler
========================

:Author: Greg Taylor
:License: BSD

This is an example image crawling application that has been split up into
multiple networked Docker_ containers using fig_. While the application
is very basic, and could be improved in many ways, it should serve as a
useful sample for a multi-container Python application.

Architecture
------------

The crawler is composed of two primary components:

* ``webapi_service`` - Dual-purpose HTTP API server and ZeroMQ message broker.
* ``crawler_worker`` - Receives crawling jobs via ZeroMQ pull, hits the URLs
    and stores the results.

All data is stored in Redis, which is the third and final container.

How to use
----------

This example does not at all follow RESTful principals, but you can submit
crawling jobs like so::

    #!/bin/bash
    curl -X POST -d@- http://boot2docker:8000 << EOF
    http://www.docker.com/
    http://www.clemson.edu/
    EOF
    echo ""

This will return some JSON output with details on the job. Grab the ID and
check up on a job::

    curl http://localhost:8000/job/9c48b4d7-346f-4fa3-a3be-1f28aa33f5fc

This will show the same JSON structure that you saw during submission, but
probably with updated information if the workers have started on it.

Why so many pieces?
-------------------

It'd certainly be possible to combine all of this into a single daemon and
a Redis container. However, if there was any expectation of speed and
throughput, we'd need to use threading/multiprocessing. Even then, we couldn't
scale beyond one instance without getting pretty complicated.

With the HTTP API separate from the workers, we can add as many workers as we'd
like. With some minor modifications, we could even allow for multiple HTTP API
services running (the workers would need to bind to multiple HTTP API/broker
containers, or we'd switch to a proper messaging queue like Rabbit/Kafka).

Since our workers run separately from the HTTP API, another cool benefit is
that when crawling a page, any ``<a href>`` tags we find can be tossed back
into the job queue for any other idle workers to pick up. We could recursively
follow all links in one invocation, but our stack could get huge, and it'd
be slower if we have more than one Docker crawler worker container running.

On what could be improved
-------------------------

* Add unit tests! There aren't any. This was a hastily contrived example for fun,
  so I cheated.
* Replace ZeroMQ with a proper message broker. I used ZeroMQ for the sake
  of simplicity. We don't get strong delivery guarantees or persistence out
  of the box, so you won't be getting any of that as-is.
* The HTTP API should probably be RESTful. And we should probably require
  a more structured input format.
* Configuration of ports/addresses is still using the old env vars that
  fig no longer recommends.
* GET'ing an invalid job ID shows the correct output, but throws a weird
  error that I haven't spent much time diagnosing in the process's stdout.
* In a production setting, we'd probably be creating debs of the various
  dependencies instead of pip installing them. The container provisioning
  phase is pretty long right now, since we're compiling C extensions for
  Twisted, ZeroMQ, and I think SSL.

License
-------

This project, and all contributed code, are licensed under the BSD License.
A copy of the BSD License may be found in the repository.

.. _Docker: https://www.docker.com/
.. _Fig: http://www.fig.sh/index.html
