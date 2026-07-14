"""Round-trip YAML helpers for detectors that need source coordinates."""

from ruamel.yaml import YAML


def load_with_lines(path):
    parser = YAML(typ="rt")
    parser.allow_duplicate_keys = True
    try:
        with open(path, "r", encoding="utf-8") as stream:
            return parser.load(stream)
    except Exception:
        return None


def source_line(node, key=None, fallback=1):
    lc = getattr(node, "lc", None)
    if lc is None:
        return fallback
    if key is not None:
        try:
            return lc.key(key)[0] + 1
        except (KeyError, TypeError, AttributeError):
            pass
    try:
        return lc.line + 1
    except (TypeError, AttributeError):
        return fallback
