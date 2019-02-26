import os, sys, re, requests, json, logging, traceback, argparse, shutil
import tarfile, zipfile
from urlparse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

import boto

import osaka.main
# TODO: remeove this!
sys.path.append("/Users/chinshitong/myGitRepos/hysds/hysds")
import sling, extract

# from hysds.orchestrator import submit_job
# import hysds.orchestrator
# from hysds.celery import app
# from hysds.dataset_ingest import ingest
# from hysds_commons.job_rest_utils import single_process_and_submission

# disable warnings for SSL verification
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

# all file types
ALL_TYPES = []

# zip types
ZIP_TYPE = [ "zip" ]
ALL_TYPES.extend(ZIP_TYPE)

# tar types
TAR_TYPE = [ "tbz2", "tgz", "bz2", "gz" ]
ALL_TYPES.extend(TAR_TYPE)

# class SlingAndExtract(object):
#
#     # def sling(self, download_url, repo_url, prod_name, file_type, prod_date, prod_met=None,
#     #           oauth_url=None, force=False, force_extract=False):
#     #     super(sling.Sling,self).sling(download_url, repo_url, prod_name, file_type, prod_date, prod_met,
#     #           oauth_url, force, force_extract)
#
#     def extract(self):
#         pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("download_url", help="download file URL " +
                                             "(credentials stored " +
                                             "in .netrc)")
    parser.add_argument("repo_url", help="repository file URL")
    parser.add_argument("prod_name", help="product name to use for " +
                                          " canonical product directory")
    parser.add_argument("file_type", help="download file type to verify",
                        choices=ALL_TYPES)
    parser.add_argument("prod_date", help="product date to use for " +
                                          " canonical product directory")
    #parser.add_argument("prod_met", help="context json which " +
    #                                         "contains metadata " +
    #                                         "information for the incoming data")
    parser.add_argument("--oauth_url", help="OAuth authentication URL " +
                                            "(credentials stored in " +
                                            ".netrc)", required=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--force", help="force download from source, " +
                                              "upload to repository, and " +
                                              "extract-ingest job " +
                                              "submission; by default, " +
                                              "nothing is done if the " +
                                              "repo_url exists",
                                              action='store_true')
    group.add_argument("-e", "--force_extract", help="force extract-ingest " +
                                              "job submission; if repo_url " +
                                              "exists, skip download from " +
                                              "source and use whatever is " +
                                              "at repo_url", action='store_true')
    args = parser.parse_args()
    #load prod_met as string
    j = json.loads(open("_context.json", "r").read())
    prod_met = json.dumps(j["prod_met"])

    try:
        path, localize_url = \
            sling.sling(args.download_url, args.repo_url, args.file_type, args.oauth_url, args.force, args.force_extract)
        file = os.path.basename(localize_url)

        # Corrects input dataset to input file, if supplied input dataset
        if os.path.isdir(file):
            shutil.move(os.path.join(file, file), "./tmp")
            shutil.rmtree(file)
            shutil.move("./tmp", file)

        extract.create_product(path, args.prod_name, args.prod_date)

    except Exception as e:
        with open('_alt_error.txt', 'a') as f:
            f.write("%s\n" % str(e))
        with open('_alt_traceback.txt', 'a') as f:
            f.write("%s\n" % traceback.format_exc())
        raise
