FROM qiime2/core:2020.6
LABEL maintainer="jwlee230@unist.ac.kr"

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN apt-get update && apt-get upgrade -y && apt-get install -y make gcc g++ zlib1g-dev libbz2-dev liblzma-dev libncurses5-dev unzip libcurl4-openssl-dev

RUN mkdir /Tools
ADD Python /Tools
RUN pip install --requirement /Tools/requirements.txt

# Mothur
ADD Tools/Mothur.zip /Tools
RUN cd /Tools && unzip Mothur.zip
ENV PATH="/Tools/mothur:$PATH"

CMD ["/bin/bash"]
