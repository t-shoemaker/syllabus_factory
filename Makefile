.PHONY: md docx html open clean clean-all get-ref help
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

FILTER_DIR   := $(realpath filters)
SYLLABUS_DIR := $(realpath syllabi)
INPUT_FILES  := $(wildcard docs/*.md)
DOCX_REF     := $(realpath assets/template.docx)

ifdef CONFIG
    CONFIG_NAME := $(basename $(notdir $(CONFIG)))
    MD_OUTPUT   := $(SYLLABUS_DIR)/md/$(CONFIG_NAME).md
    DOCX_OUTPUT := $(SYLLABUS_DIR)/docx/$(CONFIG_NAME).docx
    HTML_OUTPUT := $(SYLLABUS_DIR)/html/$(CONFIG_NAME).html
    LAST_OPENED := $(SYLLABUS_DIR)/.last-opened.$(CONFIG_NAME)
endif

define require-config
	@test -n "$(CONFIG)" || { echo "CONFIG is required. Usage: make $(1) CONFIG=<name>"; exit 1; }
endef

define check-input-files
	@test -n "$(INPUT_FILES)" || { echo "No input files found in docs/" >&2; exit 1; }
endef

define check-docx-ref
	@test -f "$(DOCX_REF)" || { echo "Missing reference docx: $(DOCX_REF). Run: make get-ref" >&2; exit 1; }
endef

$(SYLLABUS_DIR)/md $(SYLLABUS_DIR)/docx $(SYLLABUS_DIR)/html:
	@mkdir -p $@

$(MD_OUTPUT): $(CONFIG) $(INPUT_FILES) | $(SYLLABUS_DIR)/md
	$(call check-input-files)
	@python3 src/main.py -c $(CONFIG) -f $(INPUT_FILES) > $(MD_OUTPUT)

$(DOCX_OUTPUT): $(MD_OUTPUT) | $(SYLLABUS_DIR)/docx
	$(call check-docx-ref)
	@pandoc -s $(MD_OUTPUT) \
		-f markdown -t docx \
		--reference-doc=$(DOCX_REF) \
		--lua-filter=$(FILTER_DIR)/linebreaks.lua \
		--lua-filter=$(FILTER_DIR)/tables.lua \
		-o $(DOCX_OUTPUT)

$(HTML_OUTPUT): $(MD_OUTPUT) | $(SYLLABUS_DIR)/html
	@pandoc -s $(MD_OUTPUT) \
		-f markdown -t html \
		--lua-filter=$(FILTER_DIR)/linebreaks.lua \
		--lua-filter=$(FILTER_DIR)/tables.lua \
		-o $(HTML_OUTPUT)

md: $(MD_OUTPUT)
	$(call require-config,$@)
	@echo "md" > $(LAST_OPENED)

docx: $(DOCX_OUTPUT)
	$(call require-config,$@)
	@echo "docx" > $(LAST_OPENED)

html: $(HTML_OUTPUT)
	$(call require-config,$@)
	@echo "html" > $(LAST_OPENED)

# State tracking enables dynamic file opening based on the filetype. Each of
# the above aliases records its associated filetype, which open draws from when
# called
open:
	$(call require-config,$@)
	@if [ -f "$(LAST_OPENED)" ]; then \
		format=$$(cat "$(LAST_OPENED)"); \
		case $$format in \
			md)   f="$(MD_OUTPUT)" ;; \
			docx) f="$(DOCX_OUTPUT)" ;; \
			html) f="$(HTML_OUTPUT)" ;; \
			*) echo "Unknown format recorded: $$format" >&2; exit 1 ;; \
		esac; \
		[ -f "$$f" ] || { echo "File does not exist: $$f" >&2; exit 1; }; \
		$(OPEN_CMD) "$$f"; \
	else \
		echo "No recorded format for $(CONFIG_NAME). Run: make <md|docx|html> CONFIG=..." >&2; \
		exit 1; \
	fi

clean:
	$(call require-config,$@)
	rm -f $(MD_OUTPUT) $(DOCX_OUTPUT) $(HTML_OUTPUT) $(LAST_OPENED)

clean-all:
	@echo "Removing all files from syllabi/"
	rm -rf $(SYLLABUS_DIR)/md/* $(SYLLABUS_DIR)/docx/* $(SYLLABUS_DIR)/html/* $(SYLLABUS_DIR)/.last-opened.*

get-ref:
	@python3 src/template.py -f $(DOCX_REF)

help:
	@echo "Available targets:"
	@echo "  md CONFIG=<name>     - Compile markdown"
	@echo "  docx CONFIG=<name>   - Render to docx"
	@echo "  html CONFIG=<name>   - Render to html"
	@echo "  open CONFIG=<name>   - Open the last rendered file"
	@echo "  clean CONFIG=<name>  - Clean a config's generated files"
	@echo "  clean-all            - Clean all generated files"
	@echo "  get-ref              - Download reference docx template"
