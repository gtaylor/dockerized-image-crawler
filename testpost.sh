#!/bin/bash
curl -X POST -d@- http://boot2docker:8000 << EOF
http://www.docker.com/
http://www.clemson.edu/
EOF
echo ""
