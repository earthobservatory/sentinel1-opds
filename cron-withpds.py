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
import time
from qquery.utilities import config, get_aois
from hysds_commons.job_utils import submit_mozart_job
from hysds.celery import app
from shapely.geometry import Polygon, Point


def outlier(opds_polygon, bbox):
    # checks if an point of the target polygon lies outside of the OPDS polygon
    for lonlat in bbox:
        lon = lonlat[0]
        lat = lonlat[1]
        point = Point(lon, lat)
        if not opds_polygon.intersects(point):
            return True
    return False


def submit_qquery_job(region, query_endpoint, dns_list, qquery_rtag, sling_rtag, pds_queue=None):

    # set query priority
    priority = 0
    if "priority" in region["metadata"].keys():
        priority = int(region["metadata"]["priority"])

    # determine qquery job submission branch
    job_header = 'job-qquery-opds' if pds_queue else 'job-qquery'
    job_spec = job_header + ":" + qquery_rtag

    # determine the repo to query from the types_map in the aoi
    for qtype in region["metadata"]["query"].keys():  # list of endpoints to query
        if qtype != query_endpoint:
            continue
        p = priority
        if priority == 0 and "priority" in region["metadata"]["query"][qtype].keys():
            p = int(region["metadata"]["query"][qtype]["priority"])

        rtime = datetime.datetime.utcnow()
        job_name = "%s-%s-%s-%s" % (job_spec, qtype, region["id"], rtime.strftime("%d_%b_%Y_%H:%M:%S"))
        job_name = job_name.lstrip('job-')
        # Setup input arguments here
        rule = {
            "rule_name": "qquery",
            "queue": "factotum-job_worker-%s_throttled" % qtype,  # job submission queue
            "priority": p,
            "kwargs": '{}'
        }
        params = [
            {"name": "aoi",
             "from": "value",
             "value": "{}".format(region["id"]),
             },
            {"name": "endpoint",
             "from": "value",
             "value": "{}".format(qtype),
             },
            {"name": "dns_list",
             "from": "value",
             "value": "{}".format(dns_list),
             },
            {"name": "sling_version",
             "from": "value",
             "value": "{}".format(sling_rtag),
             }
        ]
        if pds_queue:
            queue = {"name": "pds_queue",
                     "from": "value",
                     "value": "{}".format(pds_queue),
                     }
            params.append(queue)

        # for each aoi and endpoint, submit a query job
        print("{0: <60}:  {1}".format("Submitting %s query job for %s over aoi" % (job_header, qtype), region["id"]))
        submit_mozart_job({}, rule,
                          hysdsio={"id": "internal-temporary-wiring",
                                   "params": params,
                                   "job-specification": job_spec},
                          job_name=job_name, enable_dedup=False)


if __name__ == "__main__":
    '''
    Main program that is run by cron to submit a query job
    '''

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qtype", help="query endpoint, e.g. (asf|scihub|unavco)")
    parser.add_argument("--dns_list", help="dns list for qtype to use from .netrc, comma separated", required=True)
    parser.add_argument("--qquery_tag", help="Standard Qquery PGE docker image tag (release, version, " +
                                      "or branch) to propagate", default="master", required=False)
    parser.add_argument("--sling_tag", help="Standard sling PGE docker image tag (release, version, " +
                                      "or branch) to propagate", required=False)
    parser.add_argument("--opds_tag", help="Opendataset qquery / sling PGE docker image tag (release, version, " +
                                      "or branch) to propagate", default="master")
    parser.add_argument("--opds_aoi", help="OpenDataset AOI name")
    parser.add_argument("--opds_queue", help="OpenDataset Autoscaling queue")

    args = parser.parse_args()

    query_endpoint = args.qtype
    dns_list = args.dns_list
    qquery_rtag = args.qquery_tag
    sling_rtag = qquery_rtag if args.sling_tag is None else args.sling_tag
    opds_rtag = args.opds_tag
    opds_aoi_name = args.opds_aoi
    opds_queue = args.opds_queue
    is_asf = query_endpoint is "asf"

    cfg = config()
    aoi = get_aois(cfg) #retrieves a list of aois that match the grq values in settings.cfg

    opds_aoi_ind = None
    for ind, region in enumerate(aoi):
        if region['id'] == opds_aoi_name:
            opds_aoi_ind = ind
            break

    if opds_aoi_ind is None:
        print("Opendataset AOI name not found in list of AOIs. Check the field --opds_aoi!")

    # Pop the Opendataset AOI
    opds_aoi = aoi.pop(opds_aoi_ind)
    opds_polygon = Polygon(opds_aoi['location']['coordinates'][0])

    if is_asf:
        # Submit the OPDS qquery first if it's ASF endpoint
        submit_qquery_job(opds_aoi, query_endpoint, dns_list, opds_rtag, opds_rtag, opds_queue)
        time.sleep(180)

    aois = sorted(aoi,key=lambda aoi: 0 if (not "metadata" in aoi or not "priority" in aoi["metadata"]) else aoi["metadata"]["priority"],reverse=True)

    for region in aois:
        region_bbox = region['location']['coordinates'][0]
        #for each aoi
        user_tags = region.get('metadata', {}).get('user_tags', [])
        if "inactive" in user_tags:
            #if the region is inactive, skip
            print("{0: <60}:  {1}".format("AOI marked as inactive. Skipping", region["id"]))
            continue

        if is_asf and not outlier(opds_polygon, region_bbox):
            # if endpoint is asf and the region is fully within OPDS AOI, skip
            print("{0: <60}:  {1}".format("AOI is fully within Opendataset Polygon. Skipping", region["id"]))
            continue

        #skip regions without types_types map
        if "query" not in region["metadata"].keys():
            continue

        #submit qquery for sling to own bucket
        submit_qquery_job(region, query_endpoint, dns_list, qquery_rtag, sling_rtag)




