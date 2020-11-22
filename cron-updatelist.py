#!/usr/bin/env python
"""
Cron script to update OpenDataset Scene Catalog in
http://sentinel1-slc-seasia-pds.s3-website-ap-southeast-1.amazonaws.com/datasets/slc/v1.1/catalog.csv
"""

from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import dateutil.parser
from datetime import datetime, timedelta
import argparse
import csv
import os
import boto3
import types
import json
import urllib.parse
import botocore

S3_BUCKET = "sentinel1-slc-seasia-pds"
S3_PREFIX = "datasets/slc/v1.1/"
OPENDATSET_URL = "http://{}.s3-website-ap-southeast-1.amazonaws.com/".format(S3_BUCKET)
CATALOG_FILE = "catalog.csv"


def date_subdirs(start_time, end_time):
    date = start_time
    datelist = [start_time.strftime("%Y/%m/%d/")]

    while date <= end_time:
        date += timedelta(days=1)
        datelist.append(date.strftime("%Y/%m/%d/"))
    return datelist


def get_matching_s3_objects(client, bucket, prefix='', suffix=''):
    """Return list of objects under an s3 prefix per
       https://alexwlchan.net/2018/01/listing-s3-keys-redux/."""

    kwargs = {'Bucket': bucket}
    if isinstance(prefix, (str,)):
        kwargs['Prefix'] = prefix
    while True:
        resp = client.list_objects_v2(**kwargs)
        try: contents = resp['Contents']
        except KeyError: return
        for obj in contents:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                print("We found one %s" % key)
                yield obj
        try: kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError: break


def read_catalog_file(resource, local_file):
    key = "{}{}".format(S3_PREFIX, CATALOG_FILE)
    try:
        resource.Bucket(S3_BUCKET).download_file(key, local_file)
        print("Downloaded {} from {}:{}".format(local_file, S3_BUCKET, key))

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    with open(local_file, 'r') as rf:
        reader = csv.reader(rf, delimiter=',')
        id = []
        for row in reader:
            id.append(row[0])
    return id


def upload_catalog_file(resource, local_file):
    key = "{}{}".format(S3_PREFIX, CATALOG_FILE)
    with open(local_file, 'rb') as data:
        resource.Bucket(S3_BUCKET).put_object(Key=key, Body=data)
        print("Uploaded {} to {}:{}".format(local_file,S3_BUCKET, key))


def gather_scenes(start_time, end_time):
    session = boto3.session.Session(profile_name='opendataset')
    s3_client = session.client('s3')
    s3_resource = session.resource('s3')
    datelist = date_subdirs(start_time, end_time)

    local_file = os.path.join(os.path.expanduser('~'), CATALOG_FILE)
    scenes_in_file = read_catalog_file(s3_resource, local_file)

    scenes = []

    for day in datelist:
        # scrub all folders to find zip and metadata for listing
        prefix = os.path.join(S3_PREFIX, day)
        print(prefix)
        obj_list = get_matching_s3_objects(s3_client, S3_BUCKET, prefix=prefix, suffix="met.json")

        for obj in obj_list:
            content_obj = s3_resource.Object(S3_BUCKET, obj['Key'])
            metadata = json.loads(content_obj.get()['Body'].read().decode('utf-8'))
            this_id = os.path.splitext(metadata['archive_filename'])[0]

            if this_id not in scenes_in_file:
                metadata["id"] = this_id
                metadata["download_url"] = urllib.parse.urljoin(urllib.parse.urljoin(OPENDATSET_URL, obj['Key']),
                                                            "./{}".format(metadata['archive_filename']))
                latitudes = [xy[0] for xy in metadata['bbox']]
                longitudes = [xy[1] for xy in metadata['bbox']]
                metadata["minLat"] = min(latitudes)
                metadata["maxLat"] = max(latitudes)
                metadata["minLon"] = min(longitudes)
                metadata["maxLon"] = max(longitudes)
                print("%s not found in current scene list, appending." % this_id)
                scenes.append(metadata)

            else:
                print("%s found in current scene list. Skipping..." % this_id)

    print("We have to update %s scenes in the catalog. Runtime: %s" % (len(scenes), datetime.utcnow().isoformat()))

    with open(local_file, 'a') as fd:
        writer = csv.writer(fd)

        for metadata in scenes:
            # id,platform,orbitNumber,orbitRepeat,trackNumber,direction,
            # sensingStart,sensingStop,minLat,minLon,maxLat,maxLon,download_url
            row = [metadata['id'],
                   metadata['platform'],
                   metadata['orbitNumber'],
                   metadata['orbitRepeat'],
                   metadata['trackNumber'],
                   metadata['direction'],
                   metadata['sensingStart'],
                   metadata['sensingStop'],
                   metadata['minLat'],
                   metadata['minLon'],
                   metadata['maxLat'],
                   metadata['maxLon'],
                   metadata['download_url']
                   ]
            writer.writerow(row)

    fd.close()

    upload_catalog_file(s3_resource, local_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("starttime", help="Start time in ISO8601 format", nargs='?',
                        default="%sZ" % (datetime.utcnow()-timedelta(days=5)).isoformat())
    parser.add_argument("endtime", help="End time in ISO8601 format", nargs='?',
                        default="%sZ" % datetime.utcnow().isoformat())
    args = parser.parse_args()
    gather_scenes(dateutil.parser.parse(args.starttime), dateutil.parser.parse(args.endtime))




