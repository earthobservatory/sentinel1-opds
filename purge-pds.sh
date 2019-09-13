#!/bin/bash

source $HOME/verdi/bin/activate
BASE_PATH=$(dirname "${BASH_SOURCE}")



# check args
if [ "$#" -gt 3 ]; then
  query=$1
  component=$2
  operation=$3
  s3_profile=$4
else
  echo "Invalid number or arguments ($#) $*" 1>&2
  exit 1
fi

# purge products
echo "##########################################" 1>&2
echo -n "Purge/Stop/Revoke products: " 1>&2
date 1>&2

if [ "$#" -eq 4 ]; then
    python $BASE_PATH/purge-pds.py "$query" "$component" "$operation" "$s3_profile"> purge.log 2>&1
elif [ "$#" -eq 5 ]; then
    python $BASE_PATH/purge-pds.py "$query" "$component" "$operation" "$s3_profile" "$5"> purge.log 2>&1
fi
STATUS=$?
echo -n "Finished purging/revoking: " 1>&2
date 1>&2
if [ $STATUS -ne 0 ]; then
  echo "Failed to purge/revoke." 1>&2
  cat purge.log 1>&2
  echo "{}"
  exit $STATUS
fi

exit 0
