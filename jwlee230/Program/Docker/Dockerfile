FROM qiime2/core:2020.6
LABEL maintainer="jwlee230@unist.ac.kr"

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN apt-get update && apt-get upgrade -y && apt-get install -y make gcc g++ zlib1g-dev libbz2-dev liblzma-dev libncurses5-dev unzip libcurl4-openssl-dev

RUN mkdir /Tools

# Mothur
ADD Tools/Mothur.zip /Tools
RUN cd /Tools && unzip Mothur.zip
ENV PATH="/Tools/mothur:$PATH"

# Bowtie
ADD Tools/Bowtie.zip /Tools
RUN cd /Tools && unzip Bowtie.zip
ENV PATH="/Tools/bowtie-1.3.0-linux-x86_64:$PATH"

# Bowtie2
ADD Tools/Bowtie2.zip /Tools
RUN cd /Tools && unzip Bowtie2.zip
ENV PATH="/Tools/bowtie2-2.4.1-linux-x86_64:$PATH"

# BWA
ADD Tools/BWA.tar.bz2 /Tools
RUN cd /Tools/bwa-0.7.17 && make -j
ENV PATH="/Tools/bwa-0.7.17:$PATH"

# Samtools
ADD Tools/samtools.tar.bz2 /Tools
RUN cd /Tools/samtools-1.10 && make -j
ENV PATH="/Tools/samtools-1.10:$PATH"

CMD ["/bin/bash"]
