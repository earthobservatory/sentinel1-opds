#!/bin/env python
import json
import logging
import sys
import hysds_commons.request_utils
import hysds_commons.metadata_rest_utils
import osaka.main
from hysds.celery import app
import purge

# TODO: Setup logger for this job here.  Should log to STDOUT or STDERR as this is a job
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hysds")


if __name__ == "__main__":
    '''
    Main program of purge_products
    '''
    # encoding to a JSON object
    # decoded_string = sys.argv[1].decode('string_escape')
    # dec = decoded_string.replace('u""','"')
    # decoded_inp = dec.replace('""','"')
    decoded_inp = sys.argv[1]

    print decoded_inp
    if decoded_inp.startswith('{"query"') or decoded_inp.startswith("{u'query'") or decoded_inp.startswith("{'query'"):
        query_obj = json.loads(decoded_inp)
    else:
        query_obj["query"] = json.loads(decoded_inp)


    component = sys.argv[2]
    operation = sys.argv[3]
    s3_profile = sys.argv[4]

    if len(sys.argv) == 5:
        purge.purge_products(query_obj, component, operation, s3_profile)
    else:
        purge.purge_products(query_obj, component, operation, s3_profile, sys.argv[5])


