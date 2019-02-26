#!/usr/bin/env bash

source $HOME/verdi/bin/activate


# Create the pseudo met json to tag this as opds


${BASE_PATH}/sling_extract.py ${ZIP_FILE} $JOB_DIR > \
                                     ${JOB_DIR}/split_swath_products.log 2>&1