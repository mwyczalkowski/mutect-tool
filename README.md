# Mutect CWL Tool

Simple CWL wrapper for [mutect-1.1.7](https://software.broadinstitute.org/cancer/cga/mutect) for use with TinDaisy.
Based on [OpenGenomics/mutect-tool](https://github.com/OpenGenomics/mutect-tool)

For development and testing purposes, this project ships with test data and demonstration
scripts for running directly (in docker container), by calling docker image, and by calling CWL tool.
See ./testing for details.

Docker image: "dinglab2/mutect-tool:20200427"

## Memory issues

Jobs which die suddenly with "Killed" error output may be caused by running out of memory. 

There are three parameters to tweak in a cromwell run:
* Java parameter Xmx?g, maximum memory in g per job
* rammin - parameter passed to cromwell to request memory for container
* ncpu - number of jobs running at once

The hypothesis is that NCPU * Xmx <= RamMin, on the thinking that each thread requires Xmx and there will be NCPU of them,
so at least RamMin must be provided

Setting Xmx2g, rammin = 18, ncpu = 8 seems to be stable.

Contact: Matt Wyczalkowski (m.wyczalkowski@wustl.edu)
