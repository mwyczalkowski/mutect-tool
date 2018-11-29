# Currently built on denali

#IMAGE="mwyczalkowski/somatic-wrapper:cwl"
IMAGE="mwyczalkowski/mutect:latest"

cd ..
docker build -t $IMAGE -f docker/Dockerfile .
