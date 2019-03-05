#!/usr/bin/env python
"""
Cron script to submit qquery jobs.
"""

from __future__ import print_function

import json
import os
import sys
import requests
import datetime
import argparse

from utilities import config, get_aois
from hysds_commons.job_utils import submit_mozart_job
from hysds.celery import app


if __name__ == "__main__":
    '''
    Main program that is run by cron to submit a query job
    '''

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qtype", help="query endpoint, e.g. (asf|scihub|unavco)")
    parser.add_argument("--dns_list", help="dns list for qtype to use from .netrc, comma separated", required=True)
    parser.add_argument("--tag", help="PGE docker image tag (release, version, " +
                                      "or branch) to propagate",
                        default="master", required=False)
    parser.add_argument("--sling_tag", help="sling PGE docker image tag (release, version, " +
                                      "or branch) to propagate", required=False)
    args = parser.parse_args()

    query_endpoint = args.qtype
    dns_list = args.dns_list
    qquery_rtag = args.tag
    sling_rtag = qquery_rtag if args.sling_tag is None else args.sling_tag

    cfg = config()
    aoi = get_aois(cfg) #retrieves a list of aois that match the grq values in settings.cfg
    aois = sorted(aoi,key=lambda aoi: 0 if (not "metadata" in aoi or not "priority" in aoi["metadata"]) else aoi["metadata"]["priority"],reverse=True)
    for region in aois:
        #for each aoi
        user_tags = region.get('metadata', {}).get('user_tags', [])
        if "inactive" in user_tags:
            #if the region is inactive, skip
            print("AOI {0} marked as inactive. Skipping".format(region["id"]))
            continue

        #skip regions without types_types map
        if "query" not in region["metadata"].keys():
            continue

        #set query priority
        priority = 0
        if "priority" in region["metadata"].keys():
            priority = int(region["metadata"]["priority"])

        #determine qquery job submission branch
        job_spec = 'job-qquery:'+qquery_rtag

        #determine the repo to query from the types_map in the aoi
        for qtype in region["metadata"]["query"].keys(): #list of endpoints to query
            if qtype != query_endpoint:
                continue
            p = priority
            if priority == 0 and "priority" in region["metadata"]["query"][qtype].keys():
                p = int(region["metadata"]["query"][qtype]["priority"])
            rtime = datetime.datetime.utcnow()
            job_name = "%s-%s-%s-%s" % (job_spec,qtype,region["id"],rtime.strftime("%d_%b_%Y_%H:%M:%S"))
            job_name = job_name.lstrip('job-')
            #Setup input arguments here
            rule = {
                "rule_name": "qquery",
                "queue": "factotum-job_worker-%s_throttled" % qtype, # job submission queue
                "priority": p,
                "kwargs":'{}'
            }
            params = [
                { "name": "aoi",
                  "from": "value",
                  "value": "{}".format(region["id"]),
                },
                { "name": "endpoint",
                  "from": "value",
                  "value": "{}".format(qtype),
                },
                {"name": "dns_list",
                 "from": "value",
                 "value": "{}".format(dns_list),
                 },
                { "name": "sling_version",
                  "from": "value",
                  "value": "{}".format(sling_rtag),
                }
            ]
            #for each aoi and endpoint, submit a query job
            print("submitting query job for %s over aoi: %s" % (qtype, region["id"]))
            submit_mozart_job({}, rule,
                hysdsio={"id": "internal-temporary-wiring",
                         "params": params,
                         "job-specification": job_spec},
                job_name=job_name, enable_dedup=False)
