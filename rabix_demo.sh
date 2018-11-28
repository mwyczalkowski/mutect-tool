CWL="mutect.cwl"
YAML="demo.yaml"

mkdir -p ../results
RABIX_ARGS="--basedir ../results"

rabix $RABIX_ARGS $CWL $YAML

