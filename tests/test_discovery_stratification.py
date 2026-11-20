import csv
import json

from scripts.stratify_discovery_evidence import classify_evidence, stratify


def test_evidence_classifier_prefers_explicit_topic_and_galaxy():
    assert classify_evidence({"discovery_query": "topic:ansible fork:true"}) == (
        "strong", "explicit-ansible-topic", "true"
    )
    assert classify_evidence({"discovery_sources": "ansible-galaxy"}) == (
        "strong", "ansible-galaxy-source", "true"
    )
    assert classify_evidence({
        "discovery_query": "ansible in:name,description,topics fork:true"
    }) == ("weak", "metadata-text-only", "false")


def test_stratification_streams_both_outputs_and_summary(tmp_path):
    source = tmp_path / "candidates.csv"
    source.write_text(
        "project,discovery_query,discovery_sources,metadata_eligible\n"
        "one/role,topic:ansible-role fork:true,github,true\n"
        'two/tool,"ansible in:name,description,topics fork:true",github,true\n',
        encoding="utf-8",
    )
    strong = tmp_path / "strong.csv"
    weak = tmp_path / "weak.csv"
    summary_path = tmp_path / "summary.json"
    summary = stratify(source, strong, weak, summary_path)
    assert summary["all_candidates"] == 2
    assert summary["strong_candidates"] == 1
    assert summary["weak_candidates"] == 1
    with strong.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["primary_enrichment_stratum"] == "true"
    assert json.loads(summary_path.read_text())["strong_metadata_eligible"] == 1
