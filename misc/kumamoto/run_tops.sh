#
#  make all the interferograms. can run them in parallel.
#
#!/bin/bash

for n in 1 2 3
do
    echo $PWD
    cd F${n}
    files=($PWD/raw/*.SLC)
    echo $PWD
    file_1=$(basename -- ${files[0]})
    file_2=$(basename -- ${files[1]})
    echo $file_1
    p2p_S1_TOPS.csh "${file_1%.*}" "${file_2%.*}" config.s1a.txt
    cd ..
done

