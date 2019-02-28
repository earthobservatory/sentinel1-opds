#!/usr/bin/env python
"""
Bootstrap the generation of a canonical product by downloading data
from the repository, creating the skeleton directory structure for
the product and leveraging the configured metadata extractor defined
for the product in datasets JSON config.
"""

import os, sys, shutil, argparse, json, logging, time, traceback
import osaka
import sling_extract


log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("download_url", help="url of the localized file")
    parser.add_argument("file", help="localized product file")
    parser.add_argument("prod_name", help="product name to use for " +
                                          " canonical product directory")
    parser.add_argument("prod_date", help="product date to use for " +
                                          " canonical product directory")
    args = parser.parse_args()
    download_url = args.download_url
    try:
        filename, file_extension = os.path.splitext(args.file)
        logging.info("download_url : %s \nfile : %s" % (download_url, args.file))
        try:
            logging.info("calling osaka")
            osaka.main.get(download_url, args.file)
            logging.info("calling osaka successful")
        except:
            logging.info("calling osaka failed. sleeping ..")
            time.sleep(100)
            logging.info("calling osaka again")
            osaka.main.get(download_url, args.file)
            logging.info("calling osaka successful")

        # Corrects input dataset to input file, if supplied input dataset
        if os.path.isdir(args.file):
            shutil.move(os.path.join(args.file, args.file), "./tmp")
            shutil.rmtree(args.file)
            shutil.move("./tmp", args.file)

        # Check for Zero Sized File
        if not sling_extract.is_non_zero_file(args.file):
            raise Exception("File Not Found or Empty File : %s" % args.file)

        # TODO: ensure OPDS prefix is here for ingestion into opendataset bucket
        sling_extract.create_product(args.file, args.prod_name, args.prod_date)

        # Tag this job to open dataset with met.json
        prod_path = os.path.abspath(args.prod_name)
        metadata_file = os.path.join(prod_path, '%s.met.json' % os.path.basename(prod_path))

        if os.path.exists(metadata_file):
            with open(metadata_file) as f:
                metadata = json.load(f)
                metadata['tags'] = 'opendataset'

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        else:
            logging.warning("Can't tag download as opendataset. Met.json not found!")
            sys.exit(1)

    except Exception as e:
        with open('_alt_error.txt', 'a') as f:
            f.write("%s\n" % str(e))
        with open('_alt_traceback.txt', 'a') as f:
            f.write("%s\n" % traceback.format_exc())
        raise
