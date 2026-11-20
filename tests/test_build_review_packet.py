from scripts.build_review_packet import build_review_packet, write_packet


def test_review_packet_includes_context_and_rule_contract(tmp_path):
    source = tmp_path / "project" / "vars.yml"
    source.parent.mkdir()
    source.write_text("name: demo\npassword: literal\n", encoding="utf-8")
    rows = [{
        "project": "project", "path": "vars.yml", "line": "2",
        "rule_id": "plaintext-sensitive-variable",
    }]

    packet = build_review_packet(rows, tmp_path)

    assert packet[0]["source_available"] == "true"
    assert "2: password: literal" in packet[0]["source_context"]
    assert packet[0]["rule_taxonomy"] == "RISK"


def test_review_packet_writer_emits_csv_and_metadata(tmp_path):
    output = tmp_path / "packet.csv"
    metadata = tmp_path / "metadata.json"
    write_packet([{"project": "x", "source_context": ""}], output, metadata)

    assert output.is_file()
    assert '"rows": 1' in metadata.read_text(encoding="utf-8")
