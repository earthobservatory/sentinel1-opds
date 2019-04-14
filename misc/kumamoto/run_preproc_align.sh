#!/bin/bash
#
# Script to pre-process a Sentinel-1a TOPS mode data set.  
#
#   Modified from examples here:
#   https://github.com/qingkaikong/blog/tree/master/29_Processing_InSAR_Sentinel
#   http://topex.ucsd.edu/gmtsar/downloads/
#
#   place the orbits and the *.SAFE directories in the orig directory
#
#  link the orbits, the xml files, and tiff files to the global raw directory
#  put the topo in the global topo directory
#

if [[ $# -eq 0 ]] ; then
    echo 'Usage ./run_preproc_align.sh  <SLC1.SAFE filename> <SLC2.SAFE filename> <POEORB1 EOF filename> <POEORB2 EOF filename>'
    exit 0
fi

SLC1=$1
SLC2=$2

PORB1=$3
PORB2=$4


mkdir raw
cd raw
cp ../orig/*.EOF* .
ln -s ../orig/${SLC1}/annotation/*.xml .
ln -s ../orig/${SLC1}/measurement/*.tiff .
ln -s ../orig/${SLC2}/annotation/*.xml .
ln -s ../orig/${SLC2}/measurement/*.tiff .
ln -s ../topo/dem.grd .

#
#  pre-process all three subswaths
#

for n in 1 2 3
do 
    file_1=$(basename -- $PWD/../orig/${SLC1}/annotation/*iw${n}-slc*.xml)
    file_2=$(basename -- $PWD/../orig/${SLC2}/annotation/*iw${n}-slc*.xml)
    base_1="${file_1%.*}"
    base_2="${file_2%.*}"
    align_tops_esd.csh $base_1 $PORB1 $base_2 $PORB2 dem.grd
done

#  check the config.s1a.txt and make sure it is processing from step 1 to evaluate orbital information
#
#  make the swath directories and link the appropriate stuff
#

cd ..

for n in 1 2 3
do
    rm -r F${n}/raw
    mkdir F${n}
    cd F${n}
    ln -s ../config.s1a.txt .
    mkdir raw
    cd raw
    ln -s ../../raw/*F${n}* .
    echo $n
    cd ..
    mkdir topo
    cd topo
    ln -s ../../topo/dem.grd .
    cd ../..
done
