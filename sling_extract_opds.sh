#!/bin/bash
set -x
source $HOME/verdi/bin/activate


BASE_PATH=$(dirname "${BASH_SOURCE}")


echo "##########################################" 1>&2
echo -n "create OpenDataset tag for met.json: " 1>&2
date 1>&2
MET_FILE = $(./"${3}"/"${3}".met.json)

if [ -e $MET_FILE ]; then
  echo "File $MET_FILE already exists!"
else
  echo '{"tags": "opendataset"}' >> $MET_FILE
fi

echo -n "Slinging and extracting file ${2}: " 1>&2
date 1>&2
python $BASE_PATH/sling_extract.py --localize_url ${1} --file ${2} --prod_name ${3} --prod_date ${4}> sling_extract.log 2>&1
STATUS=$?

echo -n "Finished sling and extraction: " 1>&2
date 1>&2
if [ $STATUS -ne 0 ]; then
  echo "Failed to sling and extract." 1>&2
  cat sling_extract.log 1>&2
  echo "{}"
  exit $STATUS
fi



exit 0