# Mutect CWL Tool

Based on [OpenGenomics/mutect-tool](https://github.com/OpenGenomics/mutect-tool)

## TODO

The generated file `mutect_call_stats.txt` is quite large (350Mb+ in testing), and should be compressed or possibly omitted 

## Testing

Execution testing takes place at 3 levels:
* `testing/run_direct`: Run `src/mutect.py` script directly inside of docker container.  
