#!/bin/bash

# clone ariamh to be moved to its final location by docker builder
git clone https://github.com/earthobservatory/ariamh.git -b sling_opds

git clone https://github.com/earthobservatory/qquery.git -b sling-opds

# Pulls in ARIA repos outside qquery
scihub_url="https://github.com/hysds/scihub.git"
asf_url="https://github.com/hysds/asf-query.git"
unavco_url="https://github.com/hysds/unavco-query.git"
apihub_url="https://github.com/hysds/apihub.git"
git clone $scihub_url "scihub"
git clone $asf_url "asf"
git clone $unavco_url "unavco"
git clone $apihub_url "apihub"

