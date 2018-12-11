
IMAGE="dinglab2/mutect-tool:latest"
DATD="../demo_data"
#ADATD=$(readlink -f $DATD)

# Using python to get absolute path of DATD.  On Linux `readlink -f` works, but on Mac this is not always available
# see https://stackoverflow.com/questions/1055671/how-can-i-get-the-behavior-of-gnus-readlink-f-on-a-mac
ADATD=$(python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' $DATD)

docker run -v $ADATD:/data -it $IMAGE /bin/bash

# Example command to run within docker:
# ./mutect.py --input_file:normal /data/HCC1954.NORMAL.30x.compare.COST16011_region.bam --input_file:tumor /data/G15512.HCC1954.1.COST16011_region.bam --reference_sequence /data/Homo_sapiens_assembly19.COST16011_region.fa --vcf out.vcf
