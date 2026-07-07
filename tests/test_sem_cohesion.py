import tempfile
import os
import spacy
from ansibleguard.detectors import sem_cohesion


class FakeDoc:
    """Stands in for a spaCy Doc — lets us control has_vector precisely,
    so this test verifies OUR branching logic, not spaCy's current
    vocabulary (which can change across model versions)."""

    def __init__(self, has_vector):
        self.has_vector = has_vector

    def similarity(self, other):
        return 0.9  # arbitrary — only reached when both sides have vectors


def _write_temp_yaml(content):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(content)
        return f.name


def test_mixed_english_play_arabic_tasks_returns_none(monkeypatch):
    """Regression test for a real bug: the original fix tracked vector
    availability as ONE shared counter across plays and tasks combined.
    A file with a normal English play name ('Play') wrapping entirely
    non-English task names would have that one vectorizable play name
    mask that the task names specifically were never actually measured
    — silently falling through to 'average_similarity = 1' instead of
    the correct 'None' (unmeasurable). Fixed by tracking play-vector-
    availability and task-vector-availability as two separate groups."""
    vectorless_markers = ["تثبيت", "الحزمة", "إعادة", "تشغيل", "الخدمة"]

    def fake_nlp(text):
        has_vec = not any(marker in text for marker in vectorless_markers)
        return FakeDoc(has_vec)

    monkeypatch.setattr(sem_cohesion, "nlp", fake_nlp)

    path = _write_temp_yaml(
        """- name: Play
  hosts: all
  tasks:
    - name: تثبيت الحزمة
      debug: {msg: hi}
    - name: إعادة تشغيل الخدمة
      debug: {msg: hi}
"""
    )
    try:
        result = sem_cohesion.calculate_similarity(path)
        assert result is None
    finally:
        os.unlink(path)


def test_all_english_names_return_a_real_score(monkeypatch):
    """Confirms the fix didn't overcorrect — normal English names on both
    sides must still produce a real similarity score, not None."""
    monkeypatch.setattr(sem_cohesion, "nlp", lambda text: FakeDoc(True))

    path = _write_temp_yaml(
        """- name: Play
  hosts: all
  tasks:
    - name: Install nginx
      debug: {msg: hi}
    - name: Restart nginx
      debug: {msg: hi}
"""
    )
    try:
        result = sem_cohesion.calculate_similarity(path)
        assert result == 0.9
    finally:
        os.unlink(path)
