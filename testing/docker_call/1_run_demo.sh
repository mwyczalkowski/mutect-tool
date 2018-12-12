
IMAGE="dinglab2/mutect-tool:latest"
#DATD="/Users/mwyczalk/Projects/Rabix/somatic_sv_workflow/testing/demo_data"
DATD="../demo_data"
#ADATD=$(readlink -f $DATD)

# Using python to get absolute path of DATD.  On Linux `readlink -f` works, but on Mac this is not always available
# see https://stackoverflow.com/questions/1055671/how-can-i-get-the-behavior-of-gnus-readlink-f-on-a-mac
ADATD=$(python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' $DATD)

# Example command to run within docker.  Typically, start docker first with 0_start_docker.sh

NORMAL="/data/HCC1954.NORMAL.30x.compare.COST16011_region.bam"
TUMOR="/data/G15512.HCC1954.1.COST16011_region.bam"
REF="/data/Homo_sapiens_assembly19.COST16011_region.fa"
OUT="mutect_result.vcf"

CMD="/opt/mutect-tool/src/mutect-tool.py --input_file:normal $NORMAL --input_file:tumor $TUMOR --reference_sequence $REF --vcf $OUT "
#/opt/mutect-tool/src/mutect-tool.py --input_file:normal $NORMAL --input_file:tumor $TUMOR --reference_sequence $REF --vcf $OUT 


docker run -v $ADATD:/data -it $IMAGE $CMD
