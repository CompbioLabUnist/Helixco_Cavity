# Variables
DATE := $(shell date "+%y%m%d")
RANDOM = $(shell bash -c 'echo $$RANDOM')
IMAGE_NAME = cavity:latest
CPUS = 15
MEMS = 45G
PWD := $(shell pwd)
TOOLS = 
DOCKER = docker run --rm $(VOLUME_OPTS) $(RUN_OPTS) $(IMAGE_NAME)
PYTHON_PREFIX = /Python

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

Docker/Tools/FastQC.zip: | Docker/Tools
	wget "https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9.zip" -O $@
TOOLS += Docker/Tools/FastQC.zip
#
# Docker
TOOLS += $(wildcard Docker/Python/*)
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
latest: step01
.PHONY += latest

# Step 01 (FastQC for given FASTQ.gz)
Output/FastQC:
	mkdir -p $@

Output/FastQC/%_fastqc.zip Output/FastQC/%_fastqc.html: Data/1811AHP-0075/%_1.fastq.gz Data/1811AHP-0075/%_2.fastq.gz | Output/FastQC build.log
	$(DOCKER) fastqc --outdir $(addprefix /,$(@D)) --noextract --format fastq --threads $(CPUS) $(addprefix /,$^)

step01: $(addprefix Output/FastQC/,$(addsuffix _fastqc.zip,$(sort $(shell ls -1 Data/1811AHP-0075 | cut --fields 1 --delimiter _))))
.PHONY += step01

# Step 02 (Make basic QZA/QZV file)
Output/whole.manifest.tsv: Docker/Python/make_manifest.py $(wildcard Data/1811AHP-0075/*_1.fastq.gz Data/1811AHP-0075/*_2.fastq.gz) | build.log
	$(DOCKER) python3 $(PYTHON_PREFIX)/$(notdir $<) $(addprefix /,$(filter %.fastq.gz,$^)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@)

Output/%.qza: Output/%.manifest.tsv | build.log
	$(DOCKER) qiime tools import --type SampleData[PairedEndSequencesWithQuality] --input-format PairedEndFastqManifestPhred33V2 --input-path $(addprefix /,$<) --output-path $(addprefix /,$@)

Output/%.demux.qzv: Output/%.qza | build.log
	$(DOCKER) qiime demux summarize --i-data $(addprefix /,$<) --o-visualization $(addprefix /,$@)

step02: Output/whole.demux.qzv
.PHONY += step02

Output/%.demux/data/forward-seven-number-summaries.tsv Output/%.demux/data/reverse-seven-number-summaries.tsv: Output/%.demux.qzv
	unzip $< -d $(basename $<)
	mv $(basename $<)/*/* $(basename $<)
	touch $(dir $@)/*
