# Variables
DATE := $(shell date "+%y%m%d")
RANDOM = $(shell bash -c 'echo $$RANDOM')
IMAGE_NAME = cavity
CPUS = 15
MEMS = 45G
PWD := $(shell pwd)
TOOLS = 

# Options
VOLUME_OPTS = --volume $(abspath Output):/Output --volume $(abspath Data):/Data
RUN_OPTS = --tty --cpus="$(CPUS)" --memory="$(MEMS)"

# General
all:
.PHONY += all

log Output Docker/Tools:
	mkdir $@

# Tools
Docker/Tools/Mothur.zip: | Docker/Tools
	wget "https://github.com/mothur/mothur/releases/download/v1.44.2/Mothur.Ubuntu_18.zip" -O $@
TOOLS += Docker/Tools/Mothur.zip

TOOLS += $(wildcard Docker/Python/*)

# Docker
DOCKER = docker run --rm $(VOLUME_OPTS) $(RUN_OPTS) $(IMAGE_NAME)

build.log: Docker/Dockerfile $(TOOLS) | log Output
	rm -fv $@
	docker images | grep $(IMAGE_NAME) && docker rmi $(IMAGE_NAME) || true
	docker build --rm --tag $(IMAGE_NAME) $(<D) | tee $@

build: build.log
.PHONY += build

interactive: build.log
	docker run --rm $(VOLUME_OPTS) $(RUN_OPTS) --interactive $(IMAGE_NAME) /bin/bash
.PHONY += interactive

delete: build.log
	docker rmi $(IMAGE_NAME)
	rm -rfv build.log log
.PHONY += delete

stop:
	docker rm $(CONTAINER_NAME)

# SGE
tmp.sh: build.log
	echo "make -C $(PWD) latest" > tmp.sh

run: tmp.sh | log Output
	qsub -cwd -l h_vmem=$(MEMS) -m abe -M "230@fumire.moe" -N Cavity_$(DATE) -pe smp $(CPUS) -o $(abspath log) -e $(abspath log) $<
.PHONY += run

# Actual
latest: qiime
.PHONY += latest

# qiime
Output/whole.manifest.tsv: $(wildcard Data/1811AHP-0075/*_1.fastq.gz Data/1811AHP-0075/*_2.fastq.gz) | build.log
	$(DOCKER) python3 /Tools/make_manifest.py $(addprefix /,$^) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@)

Output/%.qza: Output/%.manifest.tsv | build.log
	$(DOCKER) qiime tools import --type SampleData[PairedEndSequencesWithQuality] --input-format PairedEndFastqManifestPhred33V2 --input-path $(addprefix /,$<) --output-path $(addprefix /,$@)

Output/%.qzv: Output/%.qza | build.log
	$(DOCKER) qiime demux summarize --i-data $(addprefix /,$<) --o-visualization $(addprefix /,$@)

qiime: Output/whole.qzv
.PHONY += qiime
