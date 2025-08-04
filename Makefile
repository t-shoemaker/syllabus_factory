MAKEFLAGS += --jobs
FILTER_DIR := $(realpath filters)
SYLLABUS_DIR := $(realpath syllabi)
INPUT_FILES := $(wildcard docs/*.md)
DOCX_REF := $(realpath assets/template.docx)

ifdef CONFIG
    CONFIG_NAME := $(basename $(notdir $(CONFIG)))
    MD_OUTPUT := $(SYLLABUS_DIR)/md/$(CONFIG_NAME).md
    DOCX_OUTPUT := $(SYLLABUS_DIR)/docx/$(CONFIG_NAME).docx
    HTML_OUTPUT := $(SYLLABUS_DIR)/html/$(CONFIG_NAME).html
endif

.PHONY: compile render open clean clean-all get-ref help

define check-files
    @test -n "$(CONFIG)" || (echo "CONFIG is required. Usage: make $@ CONFIG=<name>" && exit 1)
    @test -n "$(INPUT_FILES)" || (echo "No input files found" && exit 1)
    @test -f "$(DOCX_REF)" || (echo "No docx reference document" && exit 1)
    @test -f "$(CONFIG)" || (echo "Config file $(CONFIG) not found" && exit 1)
endef

$(MD_OUTPUT): $(CONFIG) $(INPUT_FILES)
	$(check-files)
	@python3 src/main.py -c $(CONFIG) -f $(INPUT_FILES) > $(MD_OUTPUT)

$(DOCX_OUTPUT): $(MD_OUTPUT)
	$(check-files)
	@pandoc -s $(MD_OUTPUT) \
		-f markdown -t docx \
		--reference-doc=$(DOCX_REF) \
		--lua-filter=$(FILTER_DIR)/linebreaks.lua \
		--lua-filter=$(FILTER_DIR)/tables.lua \
		-o $(DOCX_OUTPUT)

$(HTML_OUTPUT): $(MD_OUTPUT)
	$(check-files)
	@pandoc -s $(MD_OUTPUT) \
		-f markdown -t html \
		--lua-filter=$(FILTER_DIR)/linebreaks.lua \
		--lua-filter=$(FILTER_DIR)/tables.lua \
		-o $(HTML_OUTPUT)

md: $(MD_OUTPUT)
docx: $(DOCX_OUTPUT)
html: $(HTML_OUTPUT)

open: $(DOCX_OUTPUT)
	@open $<

clean:
	@test -n "$(CONFIG)" || (echo "CONFIG is required. Usage: make $@ CONFIG=<name>" && exit 1)
	rm -f $(MD_OUTPUT) $(DOCX_OUTPUT) $(HTML_OUTPUT)

clean-all:
	@echo "Removing all files from syllabi/"
	rm -rf $(SYLLABUS_DIR)/md/* $(SYLLABUS_DIR)/docx/* $(SYLLABUS_DIR)/html/*

get-ref:
	@python3 src/template.py -f $(DOCX_REF)

help:
	@echo "Available targets:"
	@echo "  md CONFIG=<name>           - Compile markdown"
	@echo "  docx CONFIG=<name>         - Render to docx"
	@echo "  html CONFIG=<name>         - Render to html"
	@echo "  clean CONFIG=<name>        - Clean a config's generated files"
	@echo "  clean-all                  - Clean all generated files"
	@echo "  get-ref                    - Download reference docx template"
