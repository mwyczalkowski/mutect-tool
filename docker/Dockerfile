
FROM java:7

RUN apt-get update
RUN apt-get install -y zip wget
#
# Install samtools and the python vcf libraries for wrapper code
#
RUN apt-get install -y samtools python-pip
RUN pip install PyVCF

# We'll be working in /opt from now on
WORKDIR /opt

#
# Download and unpack Mutect and picard
#
# Use v1.1.7 for consistency with SomaticWrapper
# This URL saves with given file on browser, but need to specify name explicitly for wget
RUN wget https://software.broadinstitute.org/gatk/download/auth?package=M1 -O mutect-1.1.7.jar.zip
RUN unzip mutect-1.1.7.jar.zip

RUN wget https://github.com/broadinstitute/picard/releases/download/1.122/picard-tools-1.122.zip
RUN unzip picard-tools-1.122.zip
RUN ln -s picard-tools-1.122 picard

#COPY src/mutect.py /opt/
ENV foo=1
RUN git clone https://github.com/mwyczalkowski/mutect-tool.git
