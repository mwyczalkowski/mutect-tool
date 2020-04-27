
IMAGE="dinglab2/mutect-tool:latest"
DATD="../demo_data"

# options for running mutect.  These may be defined at `docker run`-time or prior to executing mutect directly in docker
#JAVA_OPTS="-Xms512m -Xmx512m"
JAVA_OPTS="-Xm1g"
#ADATD=$(readlink -f $DATD)

# Using python to get absolute path of DATD.  On Linux `readlink -f` works, but on Mac this is not always available
# see https://stackoverflow.com/questions/1055671/how-can-i-get-the-behavior-of-gnus-readlink-f-on-a-mac
ADATD=$(python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' $DATD)

docker run -e JAVA_OPTS="$JAVA_OPTS" -v $ADATD:/data -it $IMAGE /bin/bash
