cd ../..

CWL="cwl/mutect.cwl"
YAML="testing/cwl_call/C3L-00004.katmai.yaml"

RESULTS="/diskmnt/Projects/cptac_downloads_4/Rabix"
mkdir -p $RESULTS
RABIX_ARGS="--basedir $RESULTS"

rabix $RABIX_ARGS $CWL $YAML

