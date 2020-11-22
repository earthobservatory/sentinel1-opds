#!/usr/bin/env python

from builtins import str
import os, sys, time, json, requests, logging, traceback
import acquisition_localizer_multi, acquisition_localizer_single

# set logger
log_format = "[%(asctime)s: %(levelname)s/%(name)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

class LogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'id'): record.id = '--'
        return True

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
logger.setLevel(logging.INFO)
logger.addFilter(LogFilter())

def query_acquisitions(starttime, endtime, geoshape):
    """Query ES for active AOIs that intersect starttime and endtime and
       find acquisitions that intersect the AOI polygon for the platform."""
    es_index = "grq_*_*acquisition*"
    query = {
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "dataset_type.raw": "acquisition"
                                }
                            },
                            {
                                "range": {
                                    "starttime": {
                                        "lte": endtime
                                    }
                                }
                            },
                            {
                                "range": {
                                    "endtime": {
                                        "gte": starttime
                                    }
                                }
                            }
                        ]
                    }
                },
                "filter": {
                    "geo_shape": {
                        "location": {
                            "shape": geoshape
                       }
                    }
                }
            }
        },
        "partial_fields" : {
            "partial" : {
                "include" : [ "id", "dataset_type", "dataset", "metadata" ]
            }
        }
    }
    print(query)
    acqs = [i['fields']['partial'][0]['id']for i in acquisition_localizer_single.query_es(query, es_index)]
    acquisition_localizer_multi.logger.info("Acquistions to localize: {}".format(json.dumps(acqs, indent=2)))
    return acqs

def get_aoi(aoi_name):
    es_index = "grq_*_*area_of_interest*"
    query = {
        "query":{
            "bool":{
                "must":[
                    { "term":{ "_id": aoi_name } },
                    {
                        "term": {
                            "dataset_type.raw": "area_of_interest"
                        }
                    },
                ]
            }
        },
       "partial_fields" : {
            "partial" : {
                "include" : [ "id", "starttime", "endtime", "location",
                              "metadata.user_tags", "metadata.priority" ]
            }
        }
    }
    print(json.dumps(query))
    aois = acquisition_localizer_single.query_es(query, es_index)
    return aois[0]['fields']['partial'][0]


def resolve_source(ctx_file):
    """Resolve best URL from acquisition."""

    # get settingsnano
    # read in context
    with open(ctx_file) as f:
        ctx = json.load(f)

    acq_info = {}

    start = ctx['starttime']
    end = ctx['endtime']
    aoi_name = ctx['aoi_name']

    aoi = get_aoi(aoi_name)
    acq_list = query_acquisitions(start, end, aoi['location'])


    # acq_list = ctx['products'] if isinstance(ctx['products'], list) else [ctx['products']]
    logger.info("Acq List Type : %s" % type(acq_list))

    spyddder_sling_extract_version = ctx.get('opds_sling_extract_version', 'develop')

    asf_ngap_download_queue = ctx['asf_ngap_download_queue']
    esa_download_queue = ctx['esa_download_queue']

    job_priority = ctx["job_priority"]
    job_type, job_version = ctx['job_specification']['id'].split(':')
    acquisition_localizer_version = job_version

    queues = []  # where should we get the queue value
    identifiers = []
    prod_dates = []
    index_suffix = "S1-IW_ACQ"

    return acquisition_localizer_multi.sling(acq_list, spyddder_sling_extract_version, acquisition_localizer_version, esa_download_queue,
                 asf_ngap_download_queue, job_priority, job_type, job_version)

def main():
    context_file = os.path.abspath("_context.json")
    if not os.path.exists(context_file):
        raise RuntimeError
    resolve_source(context_file)


if __name__ == '__main__':
    try:
        status = main()
    except Exception as e:
        with open('_alt_error.txt', 'w') as f:
            f.write("%s\n" % str(e))
        with open('_alt_traceback.txt', 'w') as f:
            f.write("%s\n" % traceback.format_exc())
        raise
    sys.exit(status)
