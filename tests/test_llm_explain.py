import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.error

import pytest

from ansibleguard.report import llm_explain
from ansibleguard.symbol_index import VariableDefinition


# ---------------------------------------------------------------------------
# _read_source_context
# ---------------------------------------------------------------------------

def test_read_source_context_centers_on_flagged_line(tmp_path):
    f = tmp_path / "tasks.yml"
    f.write_text("\n".join(f"line{i}" for i in range(1, 21)), encoding="utf-8")
    ctx = llm_explain._read_source_context(tmp_path, "tasks.yml", 10, before=2, after=2)
    lines = ctx.splitlines()
    assert len(lines) == 5
    assert "line8" in lines[0]
    assert "line12" in lines[-1]


def test_read_source_context_missing_file_returns_empty_string(tmp_path):
    assert llm_explain._read_source_context(tmp_path, "does_not_exist.yml", 1) == ""


def test_read_source_context_rejects_stale_line_instead_of_substituting_other_source(tmp_path):
    f = tmp_path / "tasks.yml"
    f.write_text("only_line", encoding="utf-8")
    # A valid file does not make a stale finding's anchor valid.
    ctx = llm_explain._read_source_context(tmp_path, "tasks.yml", 999, before=2, after=2)
    assert ctx == ""


@pytest.mark.parametrize("line", [0, -1, None, True, 1.5, "1.0", "-1", "not-a-line"])
def test_invalid_anchor_never_becomes_line_one(tmp_path, line):
    (tmp_path / "tasks.yml").write_text("a: b\n")
    assert llm_explain._read_source_context(tmp_path, "tasks.yml", line) == ""


def test_source_context_cannot_read_parent_absolute_or_external_symlink(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    external = tmp_path / "private.yml"
    external.write_text("private: must-not-enter-prompt\n")
    (root / "link.yml").symlink_to(external)
    for file in ("../private.yml", str(external), "link.yml", ".git/config", None):
        assert llm_explain._read_source_context(root, file, 1) == ""


@pytest.mark.parametrize("raw", [b"invalid: \xff", b"binary: \0value", b"a" * (llm_explain.MAX_SOURCE_BYTES + 1)])
def test_unusable_or_oversize_source_is_not_sent(tmp_path, raw):
    (tmp_path / "tasks.yml").write_bytes(raw)
    assert llm_explain._read_source_context(tmp_path, "tasks.yml", 1) == ""


# ---------------------------------------------------------------------------
# _variable_name_from_occurrence
# ---------------------------------------------------------------------------

def test_variable_name_from_occurrence_parses_semantic_subject():
    occurrence = {"semantic_subject": "variable:my_var|extra_stuff"}
    assert llm_explain._variable_name_from_occurrence(occurrence) == "my_var"


def test_variable_name_from_occurrence_no_extra_suffix():
    occurrence = {"semantic_subject": "variable:my_var"}
    assert llm_explain._variable_name_from_occurrence(occurrence) == "my_var"


def test_variable_name_from_occurrence_non_variable_subject_returns_none():
    assert llm_explain._variable_name_from_occurrence({"semantic_subject": "task:foo"}) is None


def test_variable_name_from_occurrence_missing_subject_returns_none():
    assert llm_explain._variable_name_from_occurrence({}) is None


# ---------------------------------------------------------------------------
# _locate_definition_line
# ---------------------------------------------------------------------------

def test_locate_definition_line_finds_key_within_window(tmp_path):
    f = tmp_path / "main.yml"
    f.write_text(
        "- name: unrelated task\n"
        "  block:\n"
        "    - name: set fact\n"
        "      set_fact:\n"
        "        my_var: 1\n",
        encoding="utf-8",
    )
    # reported_line=1 (the enclosing block's line), actual key is on line 5
    located = llm_explain._locate_definition_line(tmp_path, "main.yml", 1, "my_var")
    assert located == 5


def test_locate_definition_line_falls_back_when_not_found(tmp_path):
    f = tmp_path / "main.yml"
    f.write_text("- name: no matching key here\n  debug: msg=hi\n", encoding="utf-8")
    located = llm_explain._locate_definition_line(tmp_path, "main.yml", 1, "my_var")
    assert located == 1


def test_locate_definition_line_missing_file_falls_back(tmp_path):
    located = llm_explain._locate_definition_line(tmp_path, "missing.yml", 7, "my_var")
    assert located == 7


# ---------------------------------------------------------------------------
# _cross_file_variable_context
# ---------------------------------------------------------------------------

def _fake_graph(definitions):
    class _Graph:
        def possible_definitions_of(self, name):
            return definitions
    return _Graph()


def test_cross_file_variable_context_empty_for_non_variable_occurrence(monkeypatch):
    assert llm_explain._cross_file_variable_context("/repo", {"semantic_subject": "task:x"}) == ""


def test_cross_file_variable_context_empty_when_graph_build_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda repo_root: None)
    occurrence = {"semantic_subject": "variable:my_var", "file": "a.yml", "line": 5}
    assert llm_explain._cross_file_variable_context(tmp_path, occurrence) == ""


def test_cross_file_variable_context_skips_the_flagged_site_itself(monkeypatch, tmp_path):
    defn = VariableDefinition(name="my_var", kind="set_fact", file="a.yml", line=5)
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda repo_root: _fake_graph([defn]))
    occurrence = {"semantic_subject": "variable:my_var", "file": "a.yml", "line": 5}
    assert llm_explain._cross_file_variable_context(tmp_path, occurrence) == ""


def test_cross_file_variable_context_includes_other_definitions(monkeypatch, tmp_path):
    (tmp_path / "other.yml").write_text("my_var: 42\n", encoding="utf-8")
    defn = VariableDefinition(name="my_var", kind="set_fact", file="other.yml", line=1, scope="role")
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda repo_root: _fake_graph([defn]))
    monkeypatch.setattr(llm_explain, "_locate_definition_line", lambda *a, **k: 1)
    occurrence = {"semantic_subject": "variable:my_var", "file": "flagged.yml", "line": 10}
    result = llm_explain._cross_file_variable_context(tmp_path, occurrence)
    assert "other.yml:1" in result
    assert "my_var" in result
    assert "verify yourself" in result


def test_cross_file_variable_context_caps_at_three(monkeypatch, tmp_path):
    defs = [
        VariableDefinition(name="my_var", kind="set_fact", file=f"f{i}.yml", line=1)
        for i in range(5)
    ]
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda repo_root: _fake_graph(defs))
    monkeypatch.setattr(llm_explain, "_locate_definition_line", lambda *a, **k: 1)
    monkeypatch.setattr(llm_explain, "_read_source_context", lambda *a, **k: "snippet")
    occurrence = {"semantic_subject": "variable:my_var", "file": "flagged.yml", "line": 10}
    result = llm_explain._cross_file_variable_context(tmp_path, occurrence)
    assert sum(result.count(f"f{i}.yml") for i in range(5)) == 3


def test_cross_file_variable_context_definitions_lookup_raises_is_not_fatal(monkeypatch, tmp_path):
    class _BrokenGraph:
        def possible_definitions_of(self, name):
            raise RuntimeError("boom")
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda repo_root: _BrokenGraph())
    occurrence = {"semantic_subject": "variable:my_var", "file": "a.yml", "line": 5}
    assert llm_explain._cross_file_variable_context(tmp_path, occurrence) == ""


# ---------------------------------------------------------------------------
# _build_user_prompt
# ---------------------------------------------------------------------------

def test_build_user_prompt_includes_fields():
    occurrence = {
        "concept_id": "ansibleguard/unguarded-variable",
        "message": "variable used without guard",
        "finding_category": "variable-reasoning",
        "file": "tasks/main.yml",
        "line": 12,
    }
    prompt = llm_explain._build_user_prompt(occurrence, "   10 | some code", "")
    assert "ansibleguard/unguarded-variable" in prompt
    assert "variable used without guard" in prompt
    assert "tasks/main.yml" in prompt
    assert "12" in prompt
    assert "some code" in prompt


def test_build_user_prompt_falls_back_when_no_source_context():
    occurrence = {"file": "x.yml", "line": 1}
    prompt = llm_explain._build_user_prompt(occurrence, "", "")
    assert "(no source context available)" in prompt


def test_build_user_prompt_appends_cross_file_context():
    occurrence = {"file": "x.yml", "line": 1}
    prompt = llm_explain._build_user_prompt(occurrence, "main context", "\n\nEXTRA BLOCK")
    assert "main context" in prompt
    assert "EXTRA BLOCK" in prompt


# ---------------------------------------------------------------------------
# _call_ollama
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self, limit=-1):
        return self._payload if limit < 0 else self._payload[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_call_ollama_sends_num_ctx_in_options(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse({"message": {"content": "{}"}})

    monkeypatch.setattr(llm_explain, "_open_local", fake_urlopen)
    llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30, num_ctx=4096)
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["format"] == llm_explain._request_generation_schema()
    assert captured["payload"]["options"]["num_predict"] == llm_explain.DEFAULT_NUM_PREDICT


def test_generation_grammar_omits_only_string_maxima_and_runtime_schema_keeps_them():
    def without_maxima(value):
        if isinstance(value, dict):
            return {key: without_maxima(child) for key, child in value.items() if key != "maxLength"}
        if isinstance(value, list):
            return [without_maxima(child) for child in value]
        return value
    assert llm_explain.GENERATION_SCHEMA == without_maxima(llm_explain.RESPONSE_SCHEMA)
    assert llm_explain.RESPONSE_SCHEMA["properties"]["summary"]["maxLength"] == llm_explain.MAX_FIELD_CHARS


def test_call_ollama_default_num_ctx_is_8192(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse({"message": {"content": "{}"}})

    monkeypatch.setattr(llm_explain, "_open_local", fake_urlopen)
    llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30)
    assert captured["payload"]["options"]["num_ctx"] == llm_explain.DEFAULT_NUM_CTX == 8192


def test_call_ollama_returns_content_on_success(monkeypatch):
    monkeypatch.setattr(
        llm_explain, "_open_local",
        lambda req, timeout: _FakeResponse({"message": {"content": "hello"}}),
    )
    text, duration, error = llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30)
    assert text == "hello"
    assert error is None
    assert duration >= 0


def test_call_ollama_connection_error(monkeypatch):
    def fake_urlopen(req, timeout):
        raise urllib.error.URLError("refused")
    monkeypatch.setattr(llm_explain, "_open_local", fake_urlopen)
    text, duration, error = llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30)
    assert text is None
    assert "connection error" in error


def test_call_ollama_timeout(monkeypatch):
    def fake_urlopen(req, timeout):
        raise TimeoutError()
    monkeypatch.setattr(llm_explain, "_open_local", fake_urlopen)
    text, duration, error = llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30)
    assert text is None
    assert error == "timeout"


def test_call_ollama_unexpected_error_is_not_fatal(monkeypatch):
    def fake_urlopen(req, timeout):
        raise ValueError("weird")
    monkeypatch.setattr(llm_explain, "_open_local", fake_urlopen)
    text, duration, error = llm_explain._call_ollama("http://127.0.0.1:11434", "model", "sys", "user", 30)
    assert text is None
    assert "unexpected error" in error


@pytest.mark.parametrize("host", [
    "https://example.com", "http://192.168.1.2:11434", "http://0.0.0.0:11434",
    "http://localhost.evil", "http://127.0.0.1@evil.example", "http://user@127.0.0.1",
    "file:///tmp/model", "http://127.0.0.1/api", "http://127.0.0.1?target=remote",
    "http://127.0.0.1#fragment", "http://127.0.0.1:99999", "http://127.0.0.1\n",
])
def test_nonlocal_or_ambiguous_endpoints_never_open_a_connection(monkeypatch, host):
    def forbidden(*a, **k):
        pytest.fail("disallowed host opened a connection")
    monkeypatch.setattr(llm_explain, "_open_local", forbidden)
    text, _, error = llm_explain._call_ollama(host, "model", "sys", "source", 30)
    assert text is None and "local loopback" in error


@pytest.mark.parametrize("host,expected", [
    ("http://localhost:11434/", "http://127.0.0.1:11434/api/chat"),
    ("http://127.0.0.2:11434", "http://127.0.0.2:11434/api/chat"),
    ("http://[::1]:11434", "http://[::1]:11434/api/chat"),
])
def test_local_urls_have_explicit_loopback_destination(host, expected):
    assert llm_explain._local_chat_url(host) == expected


@pytest.fixture
def local_ollama_stub():
    state = {"calls": [], "redirect": False}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            state["calls"].append(self.path)
            if state["redirect"]:
                self.send_response(307)
                self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/forbidden")
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"message":{"content":"local response"},"done":true}')

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_local_transport_ignores_environment_proxy(local_ollama_stub, monkeypatch):
    host, state = local_ollama_stub
    for key in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(key, "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    monkeypatch.setenv("no_proxy", "")
    text, _, error = llm_explain._call_ollama(host, "model", "sys", "source", 2)
    assert error is None and text == "local response" and state["calls"] == ["/api/chat"]


def test_local_transport_refuses_redirects(local_ollama_stub):
    host, state = local_ollama_stub
    state["redirect"] = True
    text, _, error = llm_explain._call_ollama(host, "model", "sys", "source", 2)
    assert text is None and "redirects are disabled" in error
    assert state["calls"] == ["/api/chat"]


@pytest.mark.parametrize("body", [[], {"message": []}, {"message": {"content": 12}},
                                   {"message": {"content": "{}"}, "done": False},
                                   {"message": {"content": "{}"}, "done_reason": "length"}])
def test_bad_or_incomplete_ollama_envelopes_are_errors(monkeypatch, body):
    monkeypatch.setattr(llm_explain, "_open_local", lambda *a, **k: _FakeResponse(body))
    text, _, error = llm_explain._call_ollama(llm_explain.DEFAULT_HOST, "model", "sys", "source", 30)
    assert text is None and error


def test_oversize_envelope_is_bounded(monkeypatch):
    monkeypatch.setattr(llm_explain, "_open_local", lambda *a, **k: _FakeResponse({"huge": "a" * llm_explain.MAX_ENVELOPE_BYTES}))
    text, _, error = llm_explain._call_ollama(llm_explain.DEFAULT_HOST, "model", "sys", "source", 30)
    assert text is None and "byte limit" in error


def test_oversize_prompt_never_opens_a_connection(monkeypatch):
    monkeypatch.setattr(llm_explain, "_open_local", lambda *a, **k: pytest.fail("oversize prompt sent"))
    text, _, error = llm_explain._call_ollama(llm_explain.DEFAULT_HOST, "model", "sys", "a" * llm_explain.MAX_PROMPT_BYTES, 30)
    assert text is None and "prompt exceeds" in error


# ---------------------------------------------------------------------------
# _validate
# ---------------------------------------------------------------------------

def _full_response(**overrides):
    base = {k: "x" for k in llm_explain.REQUIRED_KEYS}
    base["confidence"] = "high"
    base.update(assessment="supported", actionability="actionable", evidence=[{"file": "a.yml", "line": 1}], missing_evidence=[])
    base.update(overrides)
    return base


def test_validate_accepts_well_formed_response():
    parsed, warnings = llm_explain._validate(json.dumps(_full_response()))
    assert warnings == []
    assert parsed["confidence"] == "high"


def test_validate_none_raw_text():
    parsed, warnings = llm_explain._validate(None)
    assert parsed is None
    assert warnings == ["no response body"]


def test_validate_malformed_json():
    parsed, warnings = llm_explain._validate("{not valid json")
    assert parsed is None
    assert "malformed JSON" in warnings[0]


def test_validate_not_a_dict():
    parsed, warnings = llm_explain._validate(json.dumps([1, 2, 3]))
    assert parsed is None
    assert "not a JSON object" in warnings[0]


def test_validate_missing_keys():
    response = _full_response()
    del response["confidence"]
    parsed, warnings = llm_explain._validate(json.dumps(response))
    assert parsed is None
    assert "missing keys" in warnings[0]
    assert "confidence" in warnings[0]


@pytest.mark.parametrize("key,value", [
    ("recommended_fix", {}), ("summary", []), ("reasoning", None),
    ("confidence", True), ("confidence", "certain"), ("confidence", "HIGH"),
    ("limitations", 4), ("fixed_code_snippet", []), ("reasoning", "  "),
    ("summary", "a" * (llm_explain.MAX_FIELD_CHARS + 1)),
])
def test_validate_rejects_invalid_field_types_enums_blanks_and_limits(key, value):
    parsed, warnings = llm_explain._validate(json.dumps(_full_response(**{key: value})))
    assert parsed is None and warnings


@pytest.mark.parametrize("raw", [
    '{"confidence":"high","confidence":"low"}', '{"value":NaN}', '{"value":Infinity}',
    '"' + "a" * llm_explain.MAX_RESPONSE_BYTES + '"', 7,
])
def test_validate_rejects_ambiguous_nonstandard_or_oversize_json(raw):
    parsed, warnings = llm_explain._validate(raw)
    assert parsed is None and warnings


def test_validate_rejects_unknown_fields():
    parsed, warnings = llm_explain._validate(json.dumps(_full_response(extra="invented field")))
    assert parsed is None and "unexpected" in warnings[0]


@pytest.mark.parametrize("limitations", [None, "", "  "])
def test_validate_requires_limitations_for_lower_confidence(limitations):
    parsed, warnings = llm_explain._validate(json.dumps(_full_response(confidence="low", limitations=limitations)))
    assert parsed is None and "limitations required" in warnings[0]


def test_validate_allows_explicitly_nullable_fields():
    parsed, warnings = llm_explain._validate(json.dumps(_full_response(fixed_code_snippet=None, limitations=None)))
    assert not warnings and parsed["fixed_code_snippet"] is None


# ---------------------------------------------------------------------------
# explain_occurrence
# ---------------------------------------------------------------------------

def test_explain_occurrence_success(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_explain, "_read_source_context", lambda *a, **k: "    1 | ctx")
    monkeypatch.setattr(llm_explain, "_cross_file_variable_context", lambda *a, **k: "")
    monkeypatch.setattr(
        llm_explain, "_call_ollama",
        lambda *a, **k: (json.dumps(_full_response(confidence="medium")), 1.23, None),
    )
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "ok"
    assert result["llm_confidence"] == "medium"
    assert result["llm_duration_seconds"] == 1.2
    assert result["llm_disclaimer"] == llm_explain.LLM_DISCLAIMER


def test_explain_occurrence_connection_error_degrades_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_explain, "_read_source_context", lambda *a, **k: "ctx")
    monkeypatch.setattr(llm_explain, "_cross_file_variable_context", lambda *a, **k: "")
    monkeypatch.setattr(
        llm_explain, "_call_ollama", lambda *a, **k: (None, 0.5, "connection error: refused")
    )
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "error"
    assert "connection error" in result["llm_error"]
    assert result["llm_duration_seconds"] == 0.5


def test_explain_occurrence_unparseable_response_is_an_error(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_explain, "_read_source_context", lambda *a, **k: "ctx")
    monkeypatch.setattr(llm_explain, "_cross_file_variable_context", lambda *a, **k: "")
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: ("not json", 0.5, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "error"
    assert "malformed JSON" in result["llm_error"]


# ---------------------------------------------------------------------------
# enrich_occurrences_with_explanations
# ---------------------------------------------------------------------------

def test_enrich_updates_occurrences_in_place_and_reports_stats(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ansibleguard.report.findings.is_optional_finding", lambda item: False
    )
    monkeypatch.setattr(
        llm_explain, "explain_occurrence",
        lambda occurrence, repo_root, **kw: {"llm_status": "ok", "llm_explanation": "x"},
    )
    occurrences = [{"file": "a.yml"}, {"file": "b.yml"}]
    stats = llm_explain.enrich_occurrences_with_explanations(occurrences, tmp_path)
    assert stats == {"attempted": 2, "ok": 2, "error": 0}
    assert occurrences[0]["llm_explanation"] == "x"
    assert occurrences[1]["llm_status"] == "ok"


def test_enrich_respects_max_items(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ansibleguard.report.findings.is_optional_finding", lambda item: False
    )
    calls = []
    monkeypatch.setattr(
        llm_explain, "explain_occurrence",
        lambda occurrence, repo_root, **kw: calls.append(occurrence) or {"llm_status": "ok"},
    )
    occurrences = [{"file": f"{i}.yml"} for i in range(5)]
    stats = llm_explain.enrich_occurrences_with_explanations(occurrences, tmp_path, max_items=2)
    assert stats["attempted"] == 2
    assert len(calls) == 2
    # items beyond max_items are left untouched
    assert "llm_status" not in occurrences[2]


def test_enrich_filters_optional_findings_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ansibleguard.report.findings.is_optional_finding",
        lambda item: item.get("optional", False),
    )
    monkeypatch.setattr(
        llm_explain, "explain_occurrence",
        lambda occurrence, repo_root, **kw: {"llm_status": "ok"},
    )
    occurrences = [{"file": "a.yml", "optional": True}, {"file": "b.yml", "optional": False}]
    stats = llm_explain.enrich_occurrences_with_explanations(occurrences, tmp_path)
    assert stats["attempted"] == 1
    assert "llm_status" not in occurrences[0]
    assert occurrences[1]["llm_status"] == "ok"


def test_enrich_counts_errors_separately_from_ok(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ansibleguard.report.findings.is_optional_finding", lambda item: False
    )
    results = iter([{"llm_status": "ok"}, {"llm_status": "error", "llm_error": "boom"}])
    monkeypatch.setattr(
        llm_explain, "explain_occurrence",
        lambda occurrence, repo_root, **kw: next(results),
    )
    occurrences = [{"file": "a.yml"}, {"file": "b.yml"}]
    stats = llm_explain.enrich_occurrences_with_explanations(occurrences, tmp_path)
    assert stats == {"attempted": 2, "ok": 1, "error": 1}


def test_no_model_or_symbol_lookup_without_valid_source(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: pytest.fail("model called without source"))
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda *a, **k: pytest.fail("graph built without source"))
    (tmp_path / "tasks.yml").write_text("a: b\n")
    result = llm_explain.explain_occurrence({"file": "tasks.yml", "line": 999}, tmp_path)
    assert result["llm_status"] == "insufficient-context"


def test_direct_graph_reads_rebuild_after_source_changes(monkeypatch, tmp_path):
    from ansibleguard import symbol_index
    calls = []

    def build(root):
        value = (root / "vars.yml").read_text()
        calls.append(value)
        return value

    monkeypatch.setattr(symbol_index, "build_repository_symbol_index", build)
    (tmp_path / "vars.yml").write_text("old")
    assert llm_explain._symbol_graph_for(tmp_path) == "old"
    (tmp_path / "vars.yml").write_text("new")
    assert llm_explain._symbol_graph_for(tmp_path) == "new"
    assert calls == ["old", "new"] and llm_explain._SYMBOL_GRAPH_CACHE.get() is None


def test_graph_reuse_is_limited_to_one_enrichment_operation(monkeypatch, tmp_path):
    from ansibleguard import symbol_index
    calls = []
    monkeypatch.setattr(symbol_index, "build_repository_symbol_index", lambda root: calls.append(root) or object())

    def explain(occurrence, root, **kwargs):
        first = llm_explain._symbol_graph_for(root)
        assert llm_explain._symbol_graph_for(root) is first
        return {"llm_status": "ok"}

    monkeypatch.setattr(llm_explain, "explain_occurrence", explain)
    for _ in range(2):
        llm_explain.enrich_occurrences_with_explanations([{}, {}], tmp_path, actionable_only=False)
        assert llm_explain._SYMBOL_GRAPH_CACHE.get() is None
    assert calls == [tmp_path, tmp_path]


def test_graph_cache_is_discarded_if_enrichment_raises(monkeypatch, tmp_path):
    def failure(*args, **kwargs):
        assert llm_explain._SYMBOL_GRAPH_CACHE.get() == {}
        raise RuntimeError("fixture")
    monkeypatch.setattr(llm_explain, "explain_occurrence", failure)
    with pytest.raises(RuntimeError, match="fixture"):
        llm_explain.enrich_occurrences_with_explanations([{}], tmp_path, actionable_only=False)
    assert llm_explain._SYMBOL_GRAPH_CACHE.get() is None


def _assessment_response(assessment, **overrides):
    values = {"assessment": assessment}
    if assessment != "supported":
        values.update(recommended_fix=None, fixed_code_snippet=None, actionability="not-assessed")
    if assessment == "insufficient-evidence":
        values.update(confidence="low", evidence=[], missing_evidence=["role reachability"], limitations="not supplied")
    values.update(overrides)
    return _full_response(**values)


@pytest.mark.parametrize("assessment", llm_explain.ASSESSMENTS)
def test_neutral_contract_accepts_all_explicit_outcomes(assessment):
    result, warnings = llm_explain._validate(json.dumps(_assessment_response(assessment)))
    assert not warnings and result["assessment"] == assessment


def test_legacy_answer_is_not_silently_promoted_to_the_new_contract():
    old = _full_response()
    for key in ("assessment", "evidence", "missing_evidence"):
        del old[key]
    result, warnings = llm_explain._validate(json.dumps(old))
    assert result is None and "missing keys" in warnings[0]


@pytest.mark.parametrize("assessment", ["unsupported", "insufficient-evidence"])
@pytest.mark.parametrize("fix_field", ["recommended_fix", "fixed_code_snippet"])
def test_unproven_or_contradicted_findings_cannot_carry_a_fix(assessment, fix_field):
    result, warnings = llm_explain._validate(json.dumps(_assessment_response(assessment, **{fix_field: "edit anyway"})))
    assert result is None and "must not propose fixes" in warnings[0]


@pytest.mark.parametrize("overrides", [{"missing_evidence": []}, {"confidence": "high"}])
def test_insufficiency_requires_missing_dependency_and_low_confidence(overrides):
    result, warnings = llm_explain._validate(json.dumps(_assessment_response("insufficient-evidence", **overrides)))
    assert result is None and warnings


@pytest.mark.parametrize("field,value", [
    ("assessment", "true-positive"), ("evidence", []), ("evidence", {}),
    ("evidence", [{"file": "a.yml", "line": True, "quote": "ctx"}]),
    ("evidence", [{"file": "a.yml", "line": 0, "quote": "ctx"}]),
    ("evidence", [{"file": "a.yml", "line": 1, "quote": "ctx", "extra": True}]),
    ("evidence", [{"file": "a.yml", "line": 1, "quote": "ctx"}] * (llm_explain.MAX_CITATIONS + 1)),
    ("missing_evidence", [None]), ("missing_evidence", [""]), ("missing_evidence", "unknown"),
])
def test_neutral_fields_have_independent_runtime_validation(field, value):
    result, warnings = llm_explain._validate(json.dumps(_full_response(**{field: value})))
    assert result is None and warnings


@pytest.mark.parametrize("citation", [
    {"file": "a.yml", "line": 2},
    {"file": "other.yml", "line": 1},
])
def test_citations_must_match_lines_actually_supplied_to_the_model(tmp_path, monkeypatch, citation):
    (tmp_path / "a.yml").write_text("ctx\n")
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: (
        json.dumps(_full_response(evidence=[citation])), 0.1, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "error" and "citation does not match" in result["llm_error"]


def test_cannot_cite_real_repository_lines_omitted_from_the_prompt(tmp_path, monkeypatch):
    (tmp_path / "a.yml").write_text("ctx\n" * 20)
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: (
        json.dumps(_full_response(evidence=[{"file": "a.yml", "line": 20}])), 0.1, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "error"


def test_cross_file_citations_match_only_retrieved_candidate_definitions(tmp_path, monkeypatch):
    (tmp_path / "a.yml").write_text("ctx\n")
    (tmp_path / "defaults.yml").write_text("my_var: value\n")
    definition = VariableDefinition(name="my_var", file="defaults.yml", line=1, kind="role_default", scope="role:web")
    monkeypatch.setattr(llm_explain, "_symbol_graph_for", lambda root: _fake_graph([definition]))
    citation = {"file": "defaults.yml", "line": 1}
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: (json.dumps(_full_response(evidence=[citation])), 0.1, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1, "semantic_subject": "variable:my_var"}, tmp_path)
    assert result["llm_status"] == "ok" and result["llm_evidence"] == [{**citation, "quote": "my_var: value"}]
    assert result["llm_citations_checked"] and result["llm_response_schema_version"] == 3


def test_model_insufficiency_retains_explicit_missing_evidence_without_fix(tmp_path, monkeypatch):
    (tmp_path / "a.yml").write_text("ctx\n")
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: (
        json.dumps(_assessment_response("insufficient-evidence")), 0.1, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "ok" and result["llm_assessment"] == "insufficient-evidence"
    assert result["llm_missing_evidence"] == ["role reachability"]
    assert result["llm_suggested_fix"] is None and result["llm_fixed_code_snippet"] is None


def test_repeated_enrichment_failure_discards_previous_success_fields(tmp_path, monkeypatch):
    old = {"llm_status": "ok", "llm_suggested_fix": "old edit", "llm_assessment": "supported"}
    monkeypatch.setattr(llm_explain, "explain_occurrence", lambda *a, **k: {"llm_status": "error", "llm_error": "new failure"})
    llm_explain.enrich_occurrences_with_explanations([old], tmp_path, actionable_only=False)
    assert old == {"llm_status": "error", "llm_error": "new failure"}


@pytest.mark.parametrize("actionability", ["not-actionable", "context-dependent", "not-assessed"])
def test_supported_condition_can_have_no_actionable_change(actionability):
    raw = _full_response(actionability=actionability, recommended_fix=None, fixed_code_snippet=None)
    result, warnings = llm_explain._validate(json.dumps(raw))
    assert not warnings and result["assessment"] == "supported"
    raw["recommended_fix"] = "speculative edit"
    assert llm_explain._validate(json.dumps(raw))[0] is None


def test_backend_attaches_original_quote_without_asking_model_to_copy_indentation(tmp_path, monkeypatch):
    (tmp_path / "a.yml").write_text("    exact: source\n")
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: (json.dumps(_full_response()), 0.1, None))
    result = llm_explain.explain_occurrence({"file": "a.yml", "line": 1}, tmp_path)
    assert result["llm_status"] == "ok"
    assert result["llm_evidence"] == [{"file": "a.yml", "line": 1, "quote": "    exact: source"}]


def test_conflicting_or_blank_context_cannot_certify_a_citation():
    catalog = {}
    llm_explain._catalog_snippet(catalog, "a.yml", "    1 | first\n    2 |    ")
    llm_explain._catalog_snippet(catalog, "a.yml", "    1 | changed")
    for line in (1, 2):
        assert not llm_explain._check_citations({"evidence": [{"file": "a.yml", "line": line}]}, catalog)


def test_v2_defect_field_contract_is_not_promoted_into_neutral_v3():
    raw = _full_response()
    raw["what_is_wrong"] = raw.pop("summary")
    assert llm_explain._validate(json.dumps(raw))[0] is None


@pytest.mark.parametrize("assessment", ["supported", "unsupported"])
def test_decisive_assessment_cannot_declare_required_decision_evidence_missing(assessment):
    raw = _assessment_response(assessment, missing_evidence=["inventory and extra-vars definitions"])
    result, warnings = llm_explain._validate(json.dumps(raw))
    assert result is None and "missing required decision evidence" in warnings[0]
