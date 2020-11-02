#!/usr/bin/env python
"""
Bootstrap the generation of a canonical product by downloading data
from the repository, creating the skeleton directory structure for
the product and leveraging the configured metadata extractor defined
for the product in datasets JSON config.
"""

from builtins import str
import os, sys, shutil, argparse, json, logging, time, traceback
import sling_extract_asf as sea


log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description=__doc__)
    # parser.add_argument("download_url", help="url of the localized file")
    # parser.add_argument("file", help="localized product file")
    # parser.add_argument("prod_name", help="product name to use for " +
    #                                       " canonical product directory")
    # parser.add_argument("prod_date", help="product date to use for " +
    #                                       " canonical product directory")
    # args = parser.parse_args()
    # download_url = args.download_url
    # try:
    #     filename, file_extension = os.path.splitext(args.file)
    #     logging.info("download_url : %s \nfile : %s" % (download_url, args.file))
    #     try:
    #         logging.info("calling osaka")
    #         osaka.main.get(download_url, args.file)
    #         logging.info("calling osaka successful")
    #     except:
    #         logging.info("calling osaka failed. sleeping ..")
    #         time.sleep(100)
    #         logging.info("calling osaka again")
    #         osaka.main.get(download_url, args.file)
    #         logging.info("calling osaka successful")
    #
    #     # Corrects input dataset to input file, if supplied input dataset
    #     if os.path.isdir(args.file):
    #         shutil.move(os.path.join(args.file, args.file), "./tmp")
    #         shutil.rmtree(args.file)
    #         shutil.move("./tmp", args.file)
    #
    #     # Check for Zero Sized File
    #     if not sling_extract.is_non_zero_file(args.file):
    #         raise Exception("File Not Found or Empty File : %s" % args.file)
    # sling_extract.create_product(args.file, args.prod_name, args.prod_date)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slc_id", help="id of the localized file")
    args = parser.parse_args()
    prod_date = time.strftime('%Y-%m-%d')
    slc_prod_name = args.slc_id.strip()+"-pds"

    if sea.check_slc_status(slc_prod_name):
        logging.info("Existing as we FOUND slc id : %s in ES query" % args.slc_id)
        exit(0)

    time.sleep(5)
    # Recheck as this method sometime does not work
    if sea.check_slc_status(slc_prod_name):
        logging.info("Existing as we FOUND slc id : %s in ES query" % args.slc_id)
        exit(0)

    acq_datas = sea.get_acquisition_data_from_slc(args.slc_id)
    if len(acq_datas) < 1:
        raise RuntimeError("No Non-Deprecated Acquisition Found for SLC: {}".format(args.slc_id))

    acq_data = acq_datas[0]
    if len(acq_datas) > 1:
        for x in range(len(acq_datas)):
            acq_data = acq_datas[x]
            logging.info("Processing : {}".format(acq_data['_id']))
            if 'esa_scihub' in acq_data['_id']:
                break

    logging.info("Acquisition : {}".format(acq_data['_id']))
    acq_data = acq_data['fields']['partial'][0]
    download_url = acq_data['metadata']['download_url']
    archive_filename = acq_data['metadata']['archive_filename']
    logging.info("download_url : %s" % download_url)
    logging.info("archive_filename : %s" % archive_filename)
    logging.info("acq_data['metadata']['id'] : %s" % acq_data['metadata']['id'])

    # get md5 checksum from ASF sci-hub
    asf_md5_hash = sea.get_slc_checksum_md5_asf(args.slc_id)

    source = "asf"
    localize_url = None
    if source.lower() == "asf":
        localize_url = "https://datapool.asf.alaska.edu/SLC/SA/{}.zip".format(args.slc_id)
    else:
        localize_url = download_url

    try:
        filename, file_extension = os.path.splitext(archive_filename)
        logging.info("localize_url : %s \nfile : %s" % (localize_url, archive_filename))

        sea.localize_file(localize_url, archive_filename, False)

        # update context.json with localize file info as it is used later
        sea.update_context_file(localize_url, archive_filename, args.slc_id, prod_date, download_url)

        # getting the checksum value of the localized file
        os.path.abspath(archive_filename)
        # slc_file_path = os.path.join(os.path.abspath(args.slc_id), archive_filename)
        slc_file_path = os.path.join(os.getcwd(), archive_filename)
        localized_md5_checksum = sea.get_md5_from_localized_file(slc_file_path)

        # comparing localized md5 hash with asf's md5 hash
        if localized_md5_checksum != asf_md5_hash:
            raise RuntimeError(
                "Checksums DO NOT match SLC id {} : SLC checksum {}. local checksum {}".format(args.slc_id,
                                                                                               asf_md5_hash,
                                                                                               localized_md5_checksum))

        '''
        try:
            logging.info("calling osaka")
            osaka.main.get(localize_url, archive_filename)
            logging.info("calling osaka successful")
        except:
            logging.info("calling osaka failed. sleeping ..")
            time.sleep(100)
            logging.info("calling osaka again")
            osaka.main.get(localize_url, archive_filename)
            logging.info("calling osaka successful")
         '''
        # Corrects input dataset to input file, if supplied input dataset
        if os.path.isdir(archive_filename):
            shutil.move(os.path.join(archive_filename, archive_filename), "./tmp")
            shutil.rmtree(archive_filename)
            shutil.move("./tmp", archive_filename)

        # Check for Zero Sized File
        if not sea.is_non_zero_file(archive_filename):
            raise Exception("File Not Found or Empty File : %s" % archive_filename)

        sea.create_product(archive_filename, localize_url, slc_prod_name, prod_date, asf_md5_hash)
        # TODO: ensure OPDS prefix is here for ingestion into opendataset bucket

        # Tag this job to open dataset with met.json
        prod_path = os.path.abspath(slc_prod_name)
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
