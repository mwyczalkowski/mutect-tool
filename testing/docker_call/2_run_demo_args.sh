
IMAGE="dinglab2/mutect-tool:20200427"

NORMAL="/data/HCC1954.NORMAL.30x.compare.COST16011_region.bam"
TUMOR="/data/G15512.HCC1954.1.COST16011_region.bam"
REF="/data/Homo_sapiens_assembly19.COST16011_region.fa"
OUT="/data/mutect_result.run2.vcf"
ARGS="--tumor_lod 33 --initial_tumor_lod 22 --artifact_detection_mode"

CMD="/opt/mutect-tool/src/mutect-tool.py --input_file:normal $NORMAL --input_file:tumor $TUMOR --reference_sequence $REF --vcf $OUT --keep_filtered $ARGS"

# This sets options for java execution running mutect
#JAVA_OPTS="-Xmx7g"  # fails on straight docker on katmai
JAVA_OPTS="-Xmx1g"

#docker run -e JAVA_OPTS="$JAVA_OPTS" -v $ADATD:/data -it $IMAGE $CMD
# running with no JAVA_OPTS
# docker run -v $ADATD:/data -it $IMAGE $CMD


# running WUDocker

SYSTEM=docker   # MGI and compute1
START_DOCKERD="~/Projects/WUDocker"  # https://github.com/ding-lab/WUDocker.git

VOLUME_MAPPING="../demo_data:/data"

# Also need: /storage1/fs1/dinglab/Active/CPTAC3/Common/CPTAC3.catalog
>&2 echo Launching $IMAGE on $SYSTEM
CMD="bash $START_DOCKERD/start_docker.sh -I $IMAGE -M $SYSTEM -c \"$CMD\" $@ $VOLUME_MAPPING "
echo Running: $CMD
eval $CMD

