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
