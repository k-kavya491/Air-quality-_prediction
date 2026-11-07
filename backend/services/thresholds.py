DEFAULT_THRESHOLD = 150

# AQI level at which each sensitive group is alerted.
# These are starting values, not medical standards. Adjust them as needed.
SENSITIVITY_CATEGORIES = {
    "asthma": {"label": "Asthma", "threshold": 100},
    "elderly": {"label": "Elderly", "threshold": 100},
    "child": {"label": "Child", "threshold": 100},
}


def compute_threshold(has_asthma, is_elderly, is_child, custom=None):
    """A custom user threshold wins. Otherwise use the lowest threshold
    among the user's sensitivity groups, or the default for everyone else."""
    if custom is not None:
        return custom

    selected = []
    if has_asthma:
        selected.append(SENSITIVITY_CATEGORIES["asthma"]["threshold"])
    if is_elderly:
        selected.append(SENSITIVITY_CATEGORIES["elderly"]["threshold"])
    if is_child:
        selected.append(SENSITIVITY_CATEGORIES["child"]["threshold"])

    return min(selected) if selected else DEFAULT_THRESHOLD