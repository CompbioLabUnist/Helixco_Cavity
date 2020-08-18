# Variables
DATE := $(shell date "+%y%m%d")
RANDOM = $(shell bash -c 'echo $$RANDOM')
IMAGE_NAME = cavity:latest
CPUS = 15
MEMS = 45G
PWD := $(shell pwd)
TOOLS = 
DOCKER = docker run --rm $(VOLUME_OPTS) $(RUN_OPTS) $(IMAGE_NAME)

# Options
VOLUME_OPTS = --volume $(abspath Output):/Output --volume $(abspath Data):/Data --volume $(abspath Python):/Python
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
TOOLS += $(wildcard Docker/*)
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
latest: step06
.PHONY += latest

# Step 01 (FastQC for given FASTQ.gz)
Output/FastQC:
	mkdir -p $@

Output/FastQC/%_fastqc.zip: Data/1811AHP-0075/%.fastq.gz Data/1811AHP-0075/%.fastq.gz | Output/FastQC build.log
	$(DOCKER) fastqc --outdir $(addprefix /,$(@D)) --noextract --format fastq --threads $(CPUS) $(addprefix /,$^) 1> $@.stdout 2> $@.stderr

Output/FastQC/summary.tsv Output/FastQC/summary.tex: Python/aggregate_fastqc.py $(addprefix Output/FastQC/,$(addsuffix _1_fastqc.zip,$(sort $(shell ls -1 Data/1811AHP-0075 | cut --fields 1 --delimiter _)))) $(addprefix Output/FastQC/,$(addsuffix _2_fastqc.zip,$(sort $(shell ls -1 Data/1811AHP-0075 | cut --fields 1 --delimiter _)))) | build.log
	$(DOCKER) python3 $(addprefix /,$^)

step01: Output/FastQC/summary.tsv
.PHONY += step01

# Step 02 (Make manifest files)
Output/manifest:
	mkdir -p $@

Output/manifest/test.manifest.tsv: Python/make_manifest.py Data/1811AHP-0075/C1P-001_1.fastq.gz Data/1811AHP-0075/C1P-001_2.fastq.gz | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/manifest/whole.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/*_1.fastq.gz Data/1811AHP-0075/*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

step02: Output/manifest/whole.manifest.tsv
.PHONY += step02

# Step 03 (Make basic QZA/QZV file)
Output/demux:
	mkdir -p $@

Output/demux/%.qza: Output/manifest/%.manifest.tsv | Output/demux build.log
	$(DOCKER) qiime tools import --type SampleData[PairedEndSequencesWithQuality] --input-format PairedEndFastqManifestPhred33V2 --input-path $(addprefix /,$<) --output-path $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/demux/%.qzv: Output/demux/%.demux.qza | Output/demux build.log
	$(DOCKER) qiime demux summarize --i-data $(addprefix /,$<) --o-visualization $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

step03: Output/demux/test.qzv Output/demux/whole.qzv
.PHONY += step03

# Step 04 (Quality filter)
Output/filter:
	mkdir -p $@

Output/filter/%.seq.qza Output/filter/%.stat.qza: Output/demux/%.qza | Output/filter build.log
	$(DOCKER) qiime quality-filter q-score --i-demux $(addprefix /,$<) --o-filtered-sequences $(addprefix /,$(basename $(basename $@))).seq.qza --o-filter-stats $(addprefix /,$(basename $(basename $@))).stat.qza 1> $@.stdout 2> $@.stderr

step04: Output/filter/test.seq.qza Output/filter/whole.seq.qza
.PHONY += step04

# Step 05 (DADA2 denoising)
Output/DADA2:
	mkdir -p $@

Output/DADA2/%.table.qza Output/DADA2/%.seq.qza Output/DADA2/%.stat.qza: Output/demux/%.qza | Output/DADA2 build.log
	$(DOCKER) qiime dada2 denoise-paired --i-demultiplexed-seqs $(addprefix /,$<) --p-n-threads $(CPUS) --p-trunc-len-f 240 --p-trunc-len-r 240 --o-table $(addprefix /,$(basename $(basename $@))).table.qza --o-representative-sequences $(addprefix /,$(basename $(basename $@))).seq.qza --o-denoising-stats $(addprefix /,$(basename $(basename $@))).stat.qza 1> $@.stdout 2> $@.stderr

step05: Output/DADA2/test.seq.qza Output/DADA2/whole.seq.qza
.PHONY += step05

# Step 06 (Deblur denoising)
Output/Deblur:
	mkdir -p $@

Output/Deblur/%.table.qza Output/Deblur/%.seq.qza Output/Deblur/%.stat.qza: Output/filter/%.seq.qza | Output/Deblur build.log
	$(DOCKER) qiime deblur denoise-16S --i-demultiplexed-seqs $(addprefix /,$<) --p-trim-length 240 --p-jobs-to-start $(CPUS) --o-table $(addprefix /,$(basename $(basename $@))).table.qza --o-representative-sequences $(addprefix /,$(basename $(basename $@))).seq.qza --o-stats $(addprefix /,$(basename $(basename $@))).stat.qza 1> $@.stdout 2> $@.stderr

step06: Output/Deblur/test.seq.qza Output/Deblur/whole.seq.qza
.PHONY += step06
