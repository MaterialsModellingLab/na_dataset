THIS_MAKEFILE := $(firstword $(MAKEFILE_LIST))
THIS_MAKEFILE_ABS := $(abspath $(THIS_MAKEFILE))
THIS_MAKEFILE_DIR := $(dir $(THIS_MAKEFILE_ABS))

INPUT_DIR := ${THIS_MAKEFILE_DIR}
OUTPUT_DIR := ${THIS_MAKEFILE_DIR}/output
POTENTIAL_URL := https://www.ctcms.nist.gov/potentials/Download/2009--Purja-Pun-G-P-Mishin-Y--Ni-Al/2/Mishin-Ni-Al-2009.eam.alloy
POTENTIAL_FILE := ${INPUT_DIR}/Mishin-Ni-Al-2009.eam.alloy

# NOTE that the melting point of given potential assumed to be 1700K
OUTPUT_FCC_DIR = $(OUTPUT_DIR)/fcc
OUTPUT_LIQ_DIR = $(OUTPUT_DIR)/liquid

TARGET_FCC_TEMPS := 600  700  800  900  1000 1100 1200 1300 1400 1500 1600 1700
TARGET_LIQ_TEMPS := 1500 1600 1700 1800 1900 2000 2100 2200 2300 2400 2500 2600

.PHONY: default all clean
default: data
all: data rdf cna ptm
clean:
	@rm -rf $(OUTPUT_DIR)

help:
	@echo "Makefile for LAMMPS"
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  pre         - Preprocessing to generate restart files"
	@echo "  data        - Generate LAMMPS data files at target temperatures"
	@echo "  rdf         - Calculate RDF for generated data files"
	@echo "  cna         - Calculate CNA for generated data files"
	@echo "  ptm         - Calculate PTM for generated data files"
	@echo "  all         - Run all steps: pre, data, rdf, ptm"
	@echo "  clean       - Clean all generated files"
	@echo "  compress    - Compress output directory into a zip file"

$(POTENTIAL_FILE):
	@echo "Downloading potential file"
	@mkdir -p $(OUTPUT_DIR)
	wget -O $(POTENTIAL_FILE) $(POTENTIAL_URL)

# ===== Preprocessing Macro =====
$(OUTPUT_FCC_DIR)/restart.pre1000K: $(POTENTIAL_FILE)
	@echo "Running LAMMPS Preprocessing for FCC at temperature 1000K"
	@mkdir -p $(OUTPUT_FCC_DIR)
	@cd $(OUTPUT_FCC_DIR) && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.pre \
			-v temp 1000 \
			-v pfile $(POTENTIAL_FILE) \

$(OUTPUT_LIQ_DIR)/restart.pre4000K: $(POTENTIAL_FILE)
	@echo "Running LAMMPS Preprocessing for liquid at temperature 4000K"
	@mkdir -p $(OUTPUT_LIQ_DIR)
	@cd $(OUTPUT_LIQ_DIR) && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.pre \
			-v temp 4000 \
			-v pfile $(POTENTIAL_FILE)

.PHONY: pre clean_pre
pre: $(OUTPUT_FCC_DIR)/restart.pre1000K $(OUTPUT_LIQ_DIR)/restart.pre4000K
clean_pre:
	@echo "Cleaning up preprocessed files"
	@rm -f $(OUTPUT_FCC_DIR)/restart.pre1000K
	@rm -f $(OUTPUT_LIQ_DIR)/restart.pre4000K
# === End of Preprocessing Macro =====

# ===== LAMMPS Data Generation Macro =====
DATA_FCC_FILES = $(addsuffix K,$(addprefix ${OUTPUT_FCC_DIR}/data.,${TARGET_FCC_TEMPS}))
$(OUTPUT_FCC_DIR)/data.%K: $(OUTPUT_FCC_DIR)/restart.pre1000K $(POTENTIAL_FILE)
	@echo "Running LAMMPS for FCC at temperature $*"
	@cd $(OUTPUT_FCC_DIR) && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.target \
			-v rfile $< \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)
DATA_LIQ_FILES = $(addsuffix K,$(addprefix ${OUTPUT_LIQ_DIR}/data.,${TARGET_LIQ_TEMPS}))
$(OUTPUT_LIQ_DIR)/data.%K: $(OUTPUT_LIQ_DIR)/restart.pre4000K $(POTENTIAL_FILE)
	@echo "Running LAMMPS for liquid at temperature $*"
	@cd $(OUTPUT_LIQ_DIR) && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.target \
			-v rfile $< \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)

.PHONY: data clean_data
data: $(DATA_FCC_FILES) $(DATA_LIQ_FILES)
clean_data:
	@echo "Cleaning up data files"
	@rm -rf $(DATA_FCC_FILES)
	@rm -rf $(DATA_LIQ_FILES)
# === End of LAMMPS Data Generation Macro =====

# ===== RDF Macro =====
RDF_FCC_FILES = $(addsuffix K.txt,$(addprefix ${OUTPUT_FCC_DIR}/rdf,${TARGET_FCC_TEMPS}))
$(OUTPUT_FCC_DIR)/rdf%K.txt: ${OUTPUT_FCC_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS RDF calculation for FCC at temperature $*K"
	@cd ${OUTPUT_FCC_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.rdf \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE) \
			-v nbin 1000 \
			-v skin 0.6287210000000000E+01 \
			-v cutoff 12.0
RDF_LIQ_FILES = $(addsuffix K.txt,$(addprefix ${OUTPUT_LIQ_DIR}/rdf,${TARGET_LIQ_TEMPS}))
$(OUTPUT_LIQ_DIR)/rdf%K.txt: ${OUTPUT_LIQ_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS RDF calculation for liquid at temperature $*K"
	@cd ${OUTPUT_LIQ_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.rdf \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE) \
			-v nbin 1000 \
			-v skin 0.6287210000000000E+01 \
			-v cutoff 12.0

.PHONY: rdf clean_rdf
rdf: $(RDF_FCC_FILES) $(RDF_LIQ_FILES)
clean_rdf:
	@echo "Cleaning up RDF files"
	@rm -f $(RDF_FCC_FILES) $(RDF_LIQ_FILES)
# === End of RDF Macro =====

# ===== CNA Macro =====
CNA_FCC_FILES = $(addsuffix K.yaml,$(addprefix ${OUTPUT_FCC_DIR}/cna,${TARGET_FCC_TEMPS}))
${OUTPUT_FCC_DIR}/cna%K.yaml: ${OUTPUT_FCC_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS CNA calculation for FCC at temperature $*K"
	@cd ${OUTPUT_FCC_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.cna \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)
CNA_LIQ_FILES = $(addsuffix K.yaml,$(addprefix ${OUTPUT_LIQ_DIR}/cna,${TARGET_LIQ_TEMPS}))
${OUTPUT_LIQ_DIR}/cna%K.yaml: ${OUTPUT_LIQ_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS CNA calculation for liquid at temperature $*K"
	@cd ${OUTPUT_LIQ_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.cna \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)

.PHONY: cna clean_cna
cna: $(CNA_FCC_FILES) $(CNA_LIQ_FILES)
clean_cna:
	@echo "Cleaning up CNA files"
	@rm -f $(CNA_FCC_FILES) $(CNA_LIQ_FILES)
# ===== End of CNA Macro =====

# ===== PTM Macro =====
PTM_FCC_FILES = $(addsuffix K.yaml,$(addprefix ${OUTPUT_FCC_DIR}/ptm,${TARGET_FCC_TEMPS}))
${OUTPUT_FCC_DIR}/ptm%K.yaml: ${OUTPUT_FCC_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS PTM calculation for FCC at temperature $*K"
	@cd ${OUTPUT_FCC_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.ptm \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)
PTM_LIQ_FILES = $(addsuffix K.yaml,$(addprefix ${OUTPUT_LIQ_DIR}/ptm,${TARGET_LIQ_TEMPS}))
${OUTPUT_LIQ_DIR}/ptm%K.yaml: ${OUTPUT_LIQ_DIR}/data.%K $(POTENTIAL_FILE)
	@echo "Running LAMMPS PTM calculation for liquid at temperature $*K"
	@cd ${OUTPUT_LIQ_DIR} && \
		${INPUT_DIR}/run-lammps.sh \
			-i $(INPUT_DIR)/in.ptm \
			-v temp $* \
			-v pfile $(POTENTIAL_FILE)

.PHONY: ptm clean_ptm
ptm: $(PTM_FCC_FILES) $(PTM_LIQ_FILES)
clean_ptm:
	@echo "Cleaning up PTM files"
	@rm -f $(PTM_FCC_FILES) $(PTM_LIQ_FILES)
# ===== End of PTM Macro =====

# ===== Compress Output =====
compress:
	@${INPUT_DIR}/compress.sh $(OUTPUT_DIR)
# ===== End of Compress Output =====
