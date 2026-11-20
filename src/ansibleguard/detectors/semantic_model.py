"""Lazy shared NLP model for optional cohesion detectors."""

from functools import lru_cache


@lru_cache(maxsize=1)
def get_nlp():
    import spacy

    return spacy.load("en_core_web_lg")
