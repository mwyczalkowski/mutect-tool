# Currently built on denali

#IMAGE="mwyczalkowski/somatic-wrapper:cwl"
IMAGE="dinglab2/mutect-tool:latest"

cd ..
docker build -t $IMAGE -f docker/Dockerfile .
