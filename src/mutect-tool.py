#!/usr/bin/env python

# Notes on memory issues
# mutect-tool.py shipped with java memory allocation as defined with "-Xmx7g"
# This can cause docker container to die with out of memory issues
# Memory (and any other java) parameters are read from JAVA_OPTS environemnt parameter
# The hypothesis is that NCPU * Xmx <= RamMin, on the thinking that each thread requires Xmx and there will be NCPU of them,
# so at least RamMin must be provided to docker container

# Implementing changes 20200427:
# * tumor_lod and initial_tumor_lod are optional arguments.  Do not use mutect-tool defaults 
# * implement --artifact_detection_mode
# * send all errors to stdout

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

def fai_chunk(path, blocksize):
    seq_map = {}
    with open( path ) as handle:
        for line in handle:
            tmp = line.split("\t")
            seq_map[tmp[0]] = long(tmp[1])

    for seq in seq_map:
        l = seq_map[seq]
        for i in xrange(1, l, blocksize):
            yield (seq, i, min(i+blocksize-1, l))

def cmd_caller(cmd):
    logging.info("mutect-tool.py running: %s", cmd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print("Failed job: %s", cmd, file=sys.stderr)
        print("--stdout--", file=sys.stderr)
        print(stdout, file=sys.stderr)
        print("--stderr--", file=sys.stderr)
        print(stderr, file=sys.stderr)
    return p.returncode

def cmds_runner(cmds, cpus):
    p = Pool(cpus)
    values = p.map(cmd_caller, cmds, 1)

def call_cmd_iter(java, mutect, ref_seq, block_size, tumor_bam, normal_bam,
    output_base, cosmic, dbsnp,
    contamination, tumor_lod, initial_tumor_lod, artifact_detection_mode):

    contamination_line = ""
    if contamination is not None:
        contamination_line = "--fraction_contamination %s" % (contamination)

# From SomaticWrapper, using v1.1.7:
# "java  \${JAVA_OPTS} -jar "."$mutect1  -T MuTect -R $h38_REF -L $chr1 --dbsnp $DB_SNP_MUTECT --cosmic $DB_COSMIC_MUTECT -I:normal \${NBAM} -I:tumor \${TBAM} --artifact_detection_mode -vcf \${rawvcf}\n";


# Obtain all arguments: java -Xmx4g -jar mutect-1.1.7.jar -h
# By defalt, JAVA_OPTS was "-Xmx7g"

    template = Template("""
${JAVA}
${JAVA_OPTS} -XX:ParallelGCThreads=2 -jar ${MUTECT}
--analysis_type MuTect
--reference_sequence ${REF_SEQ}
--intervals '${INTERVAL}'
--input_file:normal ${NORMAL_BAM}
--input_file:tumor ${TUMOR_BAM}
--out ${OUTPUT_BASE}.${BLOCK_NUM}.out
${COSMIC_LINE}
${DBSNP_LINE}
${CONTAMINATION_LINE}
${TUMOR_LOD_LINE}
${INITIAL_TUMOR_LOD_LINE}
${ARTIFACT_DETECTION_MODE_LINE}
--coverage_file ${OUTPUT_BASE}.${BLOCK_NUM}.coverage
--vcf ${OUTPUT_BASE}.${BLOCK_NUM}.vcf
--tumor_sample_name TUMOR
--normal_sample_name NORMAL
""".replace("\n", " "))
# Was:
# --tumor_lod ${TUMOR_LOD}
# --initial_tumor_lod ${INITIAL_TUMOR_LOD}

    if "JAVA_OPTS" in os.environ:
        jo = os.environ['JAVA_OPTS']
    else:
        jo = ""

    for i, block in enumerate(fai_chunk( ref_seq + ".fai", block_size ) ):
        cosmic_line = ""
        if cosmic is not None:
            cosmic_line = "--cosmic %s" % (cosmic)
        dbsnp_line = ""
        if dbsnp is not None:
            dbsnp_line = "--dbsnp %s" % (dbsnp)

        tumor_lod_line = ""
        if tumor_lod is not None:
            tumor_lod_line = "--tumor_lod %s" % (tumor_lod)
        initial_tumor_lod_line = ""
        if initial_tumor_lod is not None:
            initial_tumor_lod_line = "--initial_tumor_lod %s" % (initial_tumor_lod)

        artifact_detection_mode_line = ""
        if artifact_detection_mode :
            artifact_detection_mode_line = "--artifact_detection_mode"

        cmd = template.substitute(
            dict(
                JAVA=java,
                JAVA_OPTS=jo,
                REF_SEQ=ref_seq,
                BLOCK_NUM=i,
                INTERVAL="%s:%s-%s" % (block[0], block[1], block[2]) ),
                MUTECT=mutect,
                TUMOR_BAM=tumor_bam,
                NORMAL_BAM=normal_bam,
                OUTPUT_BASE=output_base,
                COSMIC_LINE=cosmic_line,
                DBSNP_LINE=dbsnp_line,
                CONTAMINATION_LINE=contamination_line,
                TUMOR_LOD_LINE=tumor_lod_line,
                INITIAL_TUMOR_LOD_LINE=initial_tumor_lod_line,
                ARTIFACT_DETECTION_MODE_LINE=artifact_detection_mode_line
        )
        yield cmd, "%s.%s" % (output_base, i)



def run_mutect(args):

    workdir = tempfile.mkdtemp(dir=args['workdir'], prefix="mutect_work_")

    tumor_bam = os.path.join(workdir, "tumor.bam")
    normal_bam = os.path.join(workdir, "normal.bam")
    os.symlink(os.path.abspath(args["input_file:normal"]), normal_bam)
    os.symlink(os.path.abspath(args['input_file:tumor']),  tumor_bam)

    if args['input_file:index:normal'] is not None:
        os.symlink(os.path.abspath(args["input_file:index:normal"]), normal_bam + ".bai")
    elif os.path.exists(os.path.abspath(args["input_file:normal"]) + ".bai"):
        os.symlink(os.path.abspath(args["input_file:normal"]) + ".bai", normal_bam + ".bai")
    else:
        subprocess.check_call( ["/usr/bin/samtools", "index", normal_bam] )

    if args['input_file:index:tumor'] is not None:
        os.symlink(os.path.abspath(args["input_file:index:tumor"]), tumor_bam + ".bai")
    elif os.path.exists(os.path.abspath(args["input_file:tumor"]) + ".bai"):
        os.symlink(os.path.abspath(args["input_file:tumor"]) + ".bai", tumor_bam + ".bai")
    else:
        subprocess.check_call( ["/usr/bin/samtools", "index", tumor_bam] )

    ref_seq = os.path.join(workdir, "ref_genome.fasta")
    ref_dict = os.path.join(workdir, "ref_genome.dict")
    os.symlink(os.path.abspath(args['reference_sequence']), ref_seq)
    subprocess.check_call( ["/usr/bin/samtools", "faidx", ref_seq] )
    subprocess.check_call( [args['java'], "-jar",
        args['dict_jar'],
        "R=%s" % (ref_seq),
        "O=%s" % (ref_dict)
    ])

    contamination = None
    if args["fraction_contamination"] is not None:
        contamination = args["fraction_contamination"]
    if args["fraction_contamination_file"] is not None:
        with open(args["fraction_contamination_file"]) as handle:
            line = handle.readline()
            contamination = line.split()[0]

    cmds = list(call_cmd_iter(ref_seq=ref_seq,
        java=args['java'],
        mutect=args['mutect'],
        block_size=args['b'],
        tumor_bam=tumor_bam,
        normal_bam=normal_bam,
        output_base=os.path.join(workdir, "output.file"),
        cosmic=args['cosmic'],
        dbsnp=args['dbsnp'],
        contamination = contamination,
        tumor_lod=args['tumor_lod'],
        initial_tumor_lod=args['initial_tumor_lod'],
        artifact_detection_mode=args['artifact_detection_mode']
        )
    )

    rvals = cmds_runner(list(a[0] for a in cmds), args['ncpus'])

    vcf_writer = None
    for cmd, file in cmds:
        vcf_reader = vcf.Reader(filename=file + ".vcf")
        if vcf_writer is None:
            vcf_writer = vcf.Writer(open(os.path.join(args['vcf']), "w"), vcf_reader)
        for record in vcf_reader:
            # discard REJECT records unless unless keeping filtered variants
            # specific code borrowed from https://pyvcf.readthedocs.io/en/latest/_modules/vcf/model.html#_Record
            if record.FILTER is None or len(record.FILTER) == 0 or args['keep_filtered']:
                vcf_writer.write_record(record)
    vcf_writer.close()

    if args['out'] is not None:
        with open(args['out'], "w") as handle:
            for cmd, file in cmds:
                with open(file + ".out") as ihandle:
                    for line in ihandle:
                        handle.write(line)

    first_file = True
    if args['coverage_file'] is not None:
        with open(args['coverage_file'], "w") as handle:
            for cmd, file in cmds:
                with open(file + ".coverage") as ihandle:
                    first_line = True
                    for line in ihandle:
                        if first_line:
                            if first_file:
                                handle.write(line)
                                first_line = False
                                first_file = False
                        else:
                            handle.write(line)


    if not args['no_clean']:
        shutil.rmtree(workdir, ignore_errors=True)



if __name__ == "__main__":
    # All logging output to stderr
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mutect", help="Which Copy of Mutect", default="/opt/mutect-1.1.7.jar")

    parser.add_argument("--input_file:index:normal")
    parser.add_argument("--input_file:normal", required=True)
    parser.add_argument("--input_file:index:tumor")
    parser.add_argument("--input_file:tumor", required=True)
    parser.add_argument("--reference_sequence", required=True)
    parser.add_argument("--ncpus", type=int, default=8)
    parser.add_argument("--workdir", default="/tmp")
    parser.add_argument("--cosmic")
    parser.add_argument("--dbsnp")
    parser.add_argument("--out", default=None)
    parser.add_argument("--coverage_file", default=None)

    parser.add_argument("--fraction_contamination", default=None)
    parser.add_argument("--fraction_contamination-file", default=None)
    # parser.add_argument("--tumor_lod", type=float, default=6.3)
    # parser.add_argument("--initial_tumor_lod", type=float, default=4.0)
    parser.add_argument("--tumor_lod", type=float, default=None)
    parser.add_argument("--initial_tumor_lod", type=float, default=None)
    parser.add_argument("--artifact_detection_mode", action="store_true", default=False)

    parser.add_argument("--vcf", required=True)
    parser.add_argument("--no-clean", action="store_true", default=False)
    parser.add_argument("--java", default="/usr/bin/java")
    parser.add_argument("--keep_filtered", action="store_true", default=False)

    parser.add_argument("-b", type=long, help="Parallel Block Size", default=50000000)

    parser.add_argument("--dict-jar", default="/opt/picard/CreateSequenceDictionary.jar")

    args = parser.parse_args()
    run_mutect(vars(args))
