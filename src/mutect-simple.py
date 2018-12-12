#!/usr/bin/env python

from __future__ import print_function

import sys
import re
import os
import shutil
import subprocess
import tempfile
import vcf
import argparse
import logging
from string import Template
from multiprocessing import Pool

def run_mutect(args):

    vcf_writer = None
    vcf_reader = vcf.Reader(filename=args['infn'])
    print("Reading %s" % args['infn'])
    if vcf_writer is None:
        vcf_writer = vcf.Writer(open(os.path.join(args['vcf']), "w"), vcf_reader)
    for record in vcf_reader:
	print("record.FILTER = %s", str(record.FILTER[0]))
        # discard REJECT records unless unless keeping filtered variants
        if (record.FILTER[0] != "REJECT" or args['keep_filtered']):
            vcf_writer.write_record(record)
    vcf_writer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mutect", help="Which Copy of Mutect", default="/opt/mutect-1.1.7.jar")

    parser.add_argument("--input_file:index:normal")
    parser.add_argument("--input_file:normal", required=True)
    parser.add_argument("--input_file:index:tumor")
    parser.add_argument("--input_file:tumor", required=True)
    parser.add_argument("--reference_sequence", required=True)
    parser.add_argument("--infn", required=True)  # the VCF we will process
    parser.add_argument("--ncpus", type=int, default=8)
    parser.add_argument("--workdir", default="/tmp")
    parser.add_argument("--cosmic")
    parser.add_argument("--dbsnp")
    parser.add_argument("--out", default=None)
    parser.add_argument("--coverage_file", default=None)

    parser.add_argument("--fraction_contamination", default=None)
    parser.add_argument("--fraction_contamination-file", default=None)
    parser.add_argument("--tumor_lod", type=float, default=6.3)
    parser.add_argument("--initial_tumor_lod", type=float, default=4.0)
    parser.add_argument("--vcf", required=True)
    parser.add_argument("--no-clean", action="store_true", default=False)
    parser.add_argument("--java", default="/usr/bin/java")
    parser.add_argument("--keep_filtered", action="store_true", default=False)

    parser.add_argument("-b", type=long, help="Parallel Block Size", default=50000000)

    parser.add_argument("--dict-jar", default="/opt/picard/CreateSequenceDictionary.jar")

    args = parser.parse_args()
    run_mutect(vars(args))
