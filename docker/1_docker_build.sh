
#IMAGE="mwyczalkowski/somatic-wrapper:cwl"
IMAGE="dinglab2/mutect-tool:20190317"

cd ..
docker build -t $IMAGE -f docker/Dockerfile .
