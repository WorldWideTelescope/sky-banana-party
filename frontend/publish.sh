#! /bin/bash
# Copyright 2019 Peter Williams
# Licensed under the MIT License.
#
# Publish the frontend to production.

cd "$(dirname $0)"
set -x
exec gsutil -m cp *.css *.html *.ico *.js *.json *.png gs://skybanana.party/
