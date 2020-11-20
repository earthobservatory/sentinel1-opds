#!/usr/bin/env python
"""
Cron script to submit qquery jobs.
"""

from __future__ import print_function

import json
import os
import sys
import requests
from datetime import datetime, timedelta
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


def get_job_params(job_type, starttime, endtime, aoi_name, sling_extract_tag):

    rule = {
        "rule_name": job_type.lstrip('job-'),
        "queue": "factotum-job_worker-apihub_scraper_throttled",
        "priority": 5,
        "kwargs": '{}'
    }
    params = [
        {
            "name": "starttime",
            "from": "value",
            "value": starttime
        },
        {
            "name": "endtime",
            "from": "value",
            "value": endtime
        },
        {
            "name": "aoi_name",
            "from": "value",
            "value": aoi_name
        },
        {
            "name": "asf_ngap_download_queue",
            "from": "value",
            "value": "opds-job_worker-small"
        },
        {
            "name": "esa_download_queue",
            "from": "value",
            "value": "factotum-job_worker-scihub_throttled",
        },
        {
            "name": "opds_sling_extract_version",
            "from": "value",
            "value": sling_extract_tag
        }
    ]

    return rule, params




def validate_temporal_input(starttime, endtime, hours_delta):
    '''

    :param starttime:
    :param hours_delta:
    :param days_delta:
    :return:
    '''
    if isinstance(hours_delta, int):
        raise Exception("Please make sure the delta specified is a number")

    if starttime is None and hours_delta is not None:
        return "{}Z".format((datetime.utcnow() - timedelta(hours=hours_delta)).isoformat()), "{}Z".format((datetime.utcnow().isoformat()))
    elif starttime is not None and hours_delta is None:
        if not endtime:
            raise Exception("Please specify endtime!")
        else:
            return starttime, endtime
    elif starttime is None and hours_delta is None:
        raise Exception("None of the time parameters were specified. Must specify either start time, delta of hours")
    else:
        raise Exception("only one of the time parameters should be specified. "
                        "start time: {} delta of hours:{}"
                        .format(starttime, hours_delta))

if __name__ == "__main__":
    '''
    Main program that is run by cron to submit a query job
    '''

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", help="start time for qquery of acuisitions within AOI in YYYY-MM-DDTHH:MM:SSZ", required=False, default=None)
    parser.add_argument("--end", help="end time for qquery of acuisitions within AOI in YYYY-MM-DDTHH:MM:SSZ", required=False, default=None)
    parser.add_argument("--hours", help="number of hoyrs before current time for qquery of acuisitions within AOI", required=False, default=None)
    parser.add_argument("--aoi_name", help="AOI name for bounding box to qquery for acquisitions", required=True)
    parser.add_argument("--tag", help="Release for Opendataset Acquisition Localizer - Qquery job",required=True)
    parser.add_argument("--opds_sling_extract_version", help="release for sling-extract job", required=True)

    args = parser.parse_args()
    start, end = validate_temporal_input(args.start, args.end, args.hours)

    job_type = "job-opendataset_acquisition_localizer_qquery"
    job_spec = "{}:{}".format(job_type, args.tag)
    rtime = datetime.utcnow()

    job_name = "%s-%s-%s-%s" % (job_spec, start.replace("-", "").replace(":", ""),
                                end.replace("-", "").replace(":", ""),
                                rtime.strftime("%d_%b_%Y_%H:%M:%S"))

    job_name = job_name.lstrip('job-')

    # Setup input arguments here
    rule, params = get_job_params(job_type, start, end,  args.aoi_name, args.opds_sling_extract_version)

    print("submitting job of type {} for {}".format(job_spec, qtype))
    submit_mozart_job({}, rule,
        hysdsio={"id": "internal-temporary-wiring",
                 "params": params,
                 "job-specification": job_spec},
        job_name=job_name)



