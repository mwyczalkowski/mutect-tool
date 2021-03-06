# Example command to run within docker.  Typically, start docker first with 0_start_docker.sh

NORMAL="/data/HCC1954.NORMAL.30x.compare.COST16011_region.bam"
TUMOR="/data/G15512.HCC1954.1.COST16011_region.bam"
REF="/data/Homo_sapiens_assembly19.COST16011_region.fa"
OUT="mutect_result.vcf"
ARGS="--ncpus 1" #  keep things simple for testing
ARGS="$ARGS --tumor_lod 33 --initial_tumor_lod 22 --artifact_detection_mode"

# * tumor_lod and initial_tumor_lod are optional arguments.  Do not use mutect-tool defaults 
# * implement --artifact_detection_mode

/opt/mutect-tool/src/mutect-tool.py $ARGS --input_file:normal $NORMAL --input_file:tumor $TUMOR --reference_sequence $REF --vcf $OUT --keep_filtered

echo Written to $OUT
