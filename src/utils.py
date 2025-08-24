from textwrap import TextWrapper


def wrap_paragraphs(text, width=79):
    """Wrap text paragraph-by-paragraph, preserving blank lines.

    Parameters
    ----------
    text : str
        The text to wrap
    width : int
        Wrap width

    Returns
    -------
    str
        Wrapped text
    """
    wrapper = TextWrapper(
        width=width,
        replace_whitespace=True,
        drop_whitespace=True,
        break_long_words=False,
        break_on_hyphens=False,
    )
    out_lines = []
    paragraph = []

    def flush():
        if not paragraph:
            return

        para_text = " ".join(line.strip() for line in paragraph).strip()
        out_lines.extend(line.rstrip() for line in wrapper.wrap(para_text))
        paragraph.clear()

    for line in text.splitlines():
        if line.strip() == "":
            flush()
            out_lines.append("")
        else:
            paragraph.append(line)

    flush()

    return "\n".join(out_lines).rstrip("\n")


def flatten_config(config, parent_key="", sep="_"):
    """Flatten a nested config dictionary.

    Parameters
    ----------
    config : dict
        Configuration parameters
    parent_key : str
        Parent key for nested parameters
    sep : str
        Separator for parent key and nested key

    Returns
    -------
    dict
        The flattened config
    """
    items = []
    for k, v in config.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_config(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)
