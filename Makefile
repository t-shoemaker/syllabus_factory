MAKEFLAGS += --jobs
FILTER_DIR := $(realpath filters)
SYLLABUS_DIR := $(realpath syllabi)
INPUT_FILES := $(wildcard docs/*.md)
DOCX_REF := $(realpath assets/template.docx)

ifdef CONFIG
    CONFIG_NAME := $(basename $(notdir $(CONFIG)))
    MD_OUTPUT := $(SYLLABUS_DIR)/md/$(CONFIG_NAME).md
    DOCX_OUTPUT := $(SYLLABUS_DIR)/docx/$(CONFIG_NAME).docx
endif

.PHONY: compile render open clean clean-all get-ref help

define check-files
    @test -n "$(CONFIG)" || (echo "CONFIG is required. Usage: make $@ CONFIG=<name>" && exit 1)
    @test -n "$(INPUT_FILES)" || (echo "No input files found" && exit 1)
    @test -f "$(DOCX_REF)" || (echo "No docx reference document" && exit 1)
    @test -f "$(CONFIG)" || (echo "Config file $(CONFIG) not found" && exit 1)
endef

compile:
	$(check-files)
	@python3 src/main.py -c $(CONFIG) -f $(INPUT_FILES) > $(MD_OUTPUT)

render: 
	$(check-files)
	@pandoc -s $(MD_OUTPUT) \
		-f markdown -t docx \
		--reference-doc=$(DOCX_REF) \
		--lua-filter=$(FILTER_DIR)/linebreaks.lua \
		--lua-filter=$(FILTER_DIR)/tables.lua \
		-o $(DOCX_OUTPUT)

$(MD_OUTPUT): $(CONFIG) $(INPUT_FILES)
	@$(MAKE) compile CONFIG=$(CONFIG)

$(DOCX_OUTPUT): $(MD_OUTPUT)
	@$(MAKE) render CONFIG=$(CONFIG)

open: $(DOCX_OUTPUT)
	@open $(DOCX_OUTPUT)

clean:
	@test -n "$(CONFIG)" || (echo "CONFIG is required. Usage: make $@ CONFIG=<name>" && exit 1)
	rm -f $(MD_OUTPUT) $(DOCX_OUTPUT)

clean-all:
	@echo "Removing all files from syllabi/"
	rm -rf $(SYLLABUS_DIR)/md/* $(SYLLABUS_DIR)/docx/*

get-ref:
	@python3 src/download_ref.py -f $(DOCX_REF)

help:
	@echo "Available targets:"
	@echo "  compile CONFIG=<name>      - Compile markdown"
	@echo "  render CONFIG=<name>       - Render to docx"
	@echo "  clean CONFIG=<name>        - Clean specific config files"
	@echo "  clean-all                  - Clean all generated files"
	@echo "  get-ref                    - Download reference document"
