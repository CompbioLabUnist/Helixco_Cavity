# Variables
DATE := $(shell date "+%y%m%d")
RANDOM := $(shell bash -c 'echo $$RANDOM')
IMAGE_NAME = cavity:latest
CPUS = 20
MEMS = 100G
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
	docker run --rm $(VOLUME_OPTS) $(RUN_OPTS) --interactive $(IMAGE_NAME) /bin/bash || true
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
latest: step10
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

Output/manifest/whole.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/*_1.fastq.gz Data/1811AHP-0075/*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/Normal.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/N*_1.fastq.gz Data/1811AHP-0075/N*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/NormalSaliva.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/N*S*_1.fastq.gz Data/1811AHP-0075/N*S*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/NormalPlaque.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/N*P*_1.fastq.gz Data/1811AHP-0075/N*P*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/Cavity.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/C*_1.fastq.gz Data/1811AHP-0075/C*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/CavitySaliva.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/C*S*_1.fastq.gz Data/1811AHP-0075/C*S*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

Output/manifest/CavityPlaque.manifest.tsv: Python/make_manifest.py $(wildcard Data/1811AHP-0075/C*P*_1.fastq.gz Data/1811AHP-0075/C*P*_2.fastq.gz) | Output/manifest build.log
	$(DOCKER) python3 $(addprefix /,$^) > $@

step02: Output/manifest/test.manifest.tsv Output/manifest/whole.manifest.tsv Output/manifest/Normal.manifest.tsv Output/manifest/NormalSaliva.manifest.tsv Output/manifest/NormalPlaque.manifest.tsv Output/manifest/Cavity.manifest.tsv Output/manifest/CavitySaliva.manifest.tsv Output/manifest/CavityPlaque.manifest.tsv
.PHONY += step02

# Step 03 (Make basic QZA/QZV file)
Output/demux:
	mkdir -p $@

Output/demux/%.qza: Output/manifest/%.manifest.tsv | Output/demux build.log
	$(DOCKER) qiime tools import --type "SampleData[PairedEndSequencesWithQuality]" --input-format "PairedEndFastqManifestPhred33V2" --input-path $(addprefix /,$<) --output-path $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

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

step06: Output/Deblur/test.table.qza Output/Deblur/whole.table.qza
.PHONY += step06

# Step 07 (Build metadata)
Output/metadata:
	mkdir -p $@

Output/metadata/test.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) "C1P-001" > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/whole.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/Normal.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/N* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/Cavity.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/C* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/NormalSaliva.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/N*S* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/NormalPlaque.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/N*P* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/CavitySaliva.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/C*S* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

Output/metadata/CavityPlaque.tsv: Python/make_metadata.py | Output/metadata build.log
	$(DOCKER) python3 $(addprefix /,$<) $(sort $(shell ls -1 Data/1811AHP-0075/C*P* | cut --delimiter / --fields 3 | cut --delimiter _ --fields 1)) > $@
	$(DOCKER) qiime tools inspect-metadata --tsv $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

step07: Output/metadata/test.tsv Output/metadata/whole.tsv Output/metadata/Normal.tsv Output/metadata/Cavity.tsv Output/metadata/NormalSaliva.tsv Output/metadata/NormalPlaque.tsv Output/metadata/CavitySaliva.tsv Output/metadata/CavityPlaque.tsv
.PHONY += step07

# Step 08 (Feature Table Summary)
Output/FeatureTable:
	mkdir -p $@

Output/FeatureTable/%.Deblur.qzv: Output/Deblur/%.table.qza Output/metadata/%.tsv | Output/FeatureTable build.log
	$(DOCKER) qiime feature-table summarize --i-table $(addprefix /,$(word 1,$^)) --m-sample-metadata-file $(addprefix /,$(word 2,$^)) --o-visualization $(addprefix /,$@) 1> $@.stdout 2> $@.stderr

step08: Output/FeatureTable/test.Deblur.qzv Output/FeatureTable/whole.Deblur.qzv Output/FeatureTable/Normal.Deblur.qzv Output/FeatureTable/Cavity.Deblur.qzv Output/FeatureTable/NormalSaliva.Deblur.qzv Output/FeatureTable/NormalCavity.Deblur.qzv Output/FeatureTable/CavitySaliva.Deblur.qzv Output/FeatureTable/CavityPlaque.qzv
.PHONY += step08

# Step 09 (Phylogenetic tree with fasttree)
Output/Phylogenetic/fasttree:
	mkdir -p $@

Output/Phylogenetic/fasttree/%.Deblur.alignment.qza Output/Phylogenetic/fasttree/%.Deblur.masked_alignment.qza Output/Phylogenetic/fasttree/%.Deblur.tree.qza Output/Phylogenetic/fasttree/%.Deblur.rooted_tree.qza: Output/Deblur/%.seq.qza | Output/Phylogenetic/fasttree build.log
	$(DOCKER) qiime phylogeny align-to-tree-mafft-fasttree --p-n-threads $(CPUS) --i-sequences $(addprefix /,$<) --o-alignment $(addprefix /,$(basename $(basename $@))).alignment.qza --o-masked-alignment $(addprefix /,$(basename $(basename $@))).masked_alignment.qza --o-tree $(addprefix /,$(basename $(basename $@))).tree.qza --o-rooted-tree $(addprefix /,$(basename $(basename $@))).rooted_tree.qza 1> $@.stdout 2> $@.stderr

step09: Output/Phylogenetic/fasttree/whole.Deblur.rooted_tree.qza
.PHONY += step09

#Step 10 (Get TSV for machine-learning)
Output/Taxonomy:
	mkdir -p $@

Output/Taxonomy/silva.qza: | Output/Taxonomy build.log
	wget "https://data.qiime2.org/2020.6/common/silva-138-99-nb-classifier.qza" -O $@

Output/Taxonomy/gg.qza: | Output/Taxonomy build.log
	wget "https://data.qiime2.org/2020.6/common/gg-13-8-99-nb-classifier.qza" -O $@

Output/Taxonomy/%.silva.qza: Output/Taxonomy/silva.qza Output/Deblur/%.seq.qza | build.log
	$(DOCKER) qiime feature-classifier classify-sklearn --i-classifier $(addprefix /,$(word 1,$^)) --i-reads $(addprefix /,$(word 2,$^)) --p-n-jobs $(CPUS) --o-classification $(addprefix /,$@)

Output/Taxonomy/%.gg.qza: Output/Taxonomy/gg.qza Output/Deblur/%.seq.qza | build.log
	$(DOCKER) qiime feature-classifier classify-sklearn --i-classifier $(addprefix /,$(word 1,$^)) --i-reads $(addprefix /,$(word 2,$^)) --p-n-jobs $(CPUS) --o-classification $(addprefix /,$@)

step10: Output/Taxonomy/whole.silva.qza Output/Taxonomy/whole.gg.qza
.PHONY += step10

# Step 11 (Get TSV for Machine-Learning)
Output/TSV:
	mkdir -p $@

Output/TSV/%.deblur.silva.tsv: Output/Deblur/%.table.qza Output/Taxonomy/%.silva.qza | Output/TSV build.log
	$(DOCKER) qiime tools export --input-path $(addprefix /,$(word 1,$^)) --output-path /Output/TSV/$(RANDOM)
	$(DOCKER) qiime tools export --input-path $(addprefix /,$(word 2,$^)) --output-path /Output/TSV/$(RANDOM)
	$(DOCKER) sed --in-place "1c#OTU ID\ttaxonomy\tconfidence" /Output/TSV/$(RANDOM)/taxonomy.tsv
	$(DOCKER) biom add-metadata --input-fp /Output/TSV/$(RANDOM)/feature-table.biom --observation-metadata-fp /Output/TSV/$(RANDOM)/taxonomy.tsv --output-fp /Output/TSV/$(RANDOM)/tmp.biom --sc-separated "taxonomy"
	$(DOCKER) biom convert --input-fp /Output/TSV/$(RANDOM)/tmp.biom --output-fp $(addprefix /,$@) --to-tsv --process-obs-metadata "taxonomy" --tsv-metadata-formatter "sc_separated" --header-key "taxonomy"
	$(DOCKER) rm -rfv /Output/TSV/$(RANDOM)

Output/TSV/%.deblur.gg.tsv: Output/Deblur/%.table.qza Output/Taxonomy/%.gg.qza | Output/TSV build.log
	$(DOCKER) qiime tools export --input-path $(addprefix /,$(word 1,$^)) --output-path /Output/TSV/$(RANDOM)
	$(DOCKER) qiime tools export --input-path $(addprefix /,$(word 2,$^)) --output-path /Output/TSV/$(RANDOM)
	$(DOCKER) sed --in-place "1c#OTU ID\ttaxonomy\tconfidence" /Output/TSV/$(RANDOM)/taxonomy.tsv
	$(DOCKER) biom add-metadata --input-fp /Output/TSV/$(RANDOM)/feature-table.biom --observation-metadata-fp /Output/TSV/$(RANDOM)/taxonomy.tsv --output-fp /Output/TSV/$(RANDOM)/tmp.biom --sc-separated "taxonomy"
	$(DOCKER) biom convert --input-fp /Output/TSV/$(RANDOM)/tmp.biom --output-fp $(addprefix /,$@) --to-tsv --process-obs-metadata "taxonomy" --tsv-metadata-formatter "sc_separated" --header-key "taxonomy"
	$(DOCKER) rm -rfv /Output/TSV/$(RANDOM)

step11: Output/TSV/whole.deblur.silva.tsv Output/TSV/whole.deblur.gg.tsv
.PHONY += step11

# Step 12 (Read raw TSV file and make PKL file)
Output/python/step12:
	mkdir -p $@

Output/python/step12/%.pkl.gz: Python/step12.py Output/TSV/%.tsv | Output/python/step12 build.log
	$(DOCKER) python3 $(addprefix /,$(word 1,$^)) --input $(addprefix /,$(word 2,$^)) --output $(addprefix /,$@)

step12: Output/python/step12/whole.deblur.silva.pkl.gz Output/python/step12/whole.deblur.gg.pkl.gz
.PHONY += step12
