#!/usr/bin/env python3

import os
import glob
import argparse
import json
import numpy as np
import urllib.parse
import re, shutil
import datetime
import requests
import subprocess as sp

SCIHUB_PROD_QUERY = "https://scihub.copernicus.eu/dhus/search?q=%s&format=json"
OPDS_PROD_AWS = "s3://sentinel1-slc-seasia-pds/datasets/slc/v1.1/{year}/{month}/{day}/{slc_id}/{slc_id}.zip"
OPS_PROD_HTTP = "http://sentinel1-slc-seasia-pds.s3-website-ap-southeast-1.amazonaws.com/datasets/slc/v1.1/{year}/{month}/{day}/{slc_id}/{slc_id}.zip"
OPDS_ID_RE = "(?P<spacecraft>S1\w)_IW_SLC__(?P<misc>.*?)_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})(?P<timestamp>.+)$"

def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(
        description='For checking md5sums of s3 objects against scihub.')
    parser.add_argument('-l', dest='slc_list', type=str, default='',
                        help='list of slcs to check, comma-seperated')
    parser.add_argument('-dl', dest='s3_dl', help="Download from AWS OpenDataset to do full md5 sum check",
                        action='store_true', default=False)

    return parser.parse_args()

def get_zip_md(slc_id):
    # print("SLC: %s" % slc_id)

    req_url = requests.get(SCIHUB_PROD_QUERY % slc_id)
    req_url.raise_for_status()

    prod_url = req_url.json()["feed"]["entry"]["link"][1]["href"]
    # print("URL: %s" % prod_url)

    req_md = requests.get(prod_url)
    req_md.raise_for_status()
    content = req_md.text
    md5_res = re.search('\<d:Value\>(.*)\<\/d:Value\>', content, re.MULTILINE | re.DOTALL)
    md5 = md5_res.group(1).lower()
    size_res = re.search('\<d:ContentLength\>(.*)\<\/d:ContentLength\>', content, re.MULTILINE | re.DOTALL)
    size = size_res.group(1)


    return md5,size

def get_opds_md(slc_id, scihub_md5="", dl = False):
    slc_res = re.search(OPDS_ID_RE, slc_id)
    year = slc_res.group('year')
    month = slc_res.group('month')
    day = slc_res.group('day')
    slc_s3 = OPDS_PROD_AWS.format(year=year, month=month, day=day, slc_id=slc_id)
    slc_http = OPS_PROD_HTTP.format(year=year, month=month, day=day, slc_id=slc_id)
    resp = requests.head(slc_http)
    size = resp.headers['Content-Length']
    md5 = ""

    if dl:
        if os.path.exists("{}.zip".format(slc_id)) and sp.check_output("md5sum {}.zip".format(slc_id), shell=True).decode("utf-8").split()[0] in scihub_md5:
            md5 = scihub_md5
        else:
            sp.check_call("aws s3 cp {} .".format(slc_s3), shell=True)
            # sp.check_call("wget -c --no-check-certificate {}".format(slc_http), shell=True)
            md5 = sp.check_output("md5sum {}.zip".format(slc_id), shell=True).decode("utf-8").split()[0]

    return md5, size



if __name__ == '__main__':
    inps = cmdLineParse()

    slc_str = inps.slc_list
    slc_list = [item.strip() for item in slc_str.split(',')]

    for slc_id in slc_list:
        (md5_scihub, size_scihub) = get_zip_md(slc_id)
        print("SCIHUB: %70s %34s %12s"% (slc_id, md5_scihub, size_scihub))
        (md5_aws, size_aws) = get_opds_md(slc_id, md5_scihub, inps.s3_dl)
        print("AWS:    %70s %34s %12s"% (slc_id, md5_aws, size_aws))

