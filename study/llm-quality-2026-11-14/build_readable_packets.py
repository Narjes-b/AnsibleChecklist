"""Add readable source listings to reviewer packets without model/gold leakage."""
import csv
import io
import json
from pathlib import Path
import re
import zipfile


def fenced(text):
    fence = "~" * max(4, 1 + max((len(x) for x in re.findall(r"~+", text)), default=0))
    return fence + "\n" + text + "\n" + fence


def main():
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / "manifest.json").read_text())
    cases = [c for p in ("explanation", "repair") for c in manifest["panels"][p]]
    for reviewer in ("A", "B"):
        before = package / f"reviewer-{reviewer}-source-packet.zip"
        target = package / f"reviewer-{reviewer}-source-readable.zip"
        with zipfile.ZipFile(before) as source, zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as dest:
            for name in source.namelist():
                dest.writestr(name, source.read(name))
            index = ["# Independent source review", "", "Start with REVIEWERS.md, then fill your own source-reviewer CSV.",
                     "These listings contain no model outputs, engineering expectations, or prefilled judgments.",
                     "Original JSON source packets remain alongside these readable renderings.", ""]
            for case in cases:
                case_id = case["case_id"]
                packet = json.loads(source.read(f"source-review/{case_id}.json"))
                lines = [f"# {case_id}", "", f"Rule: {packet['occurrence']['rule_id']}", "",
                         f"Finding: {packet['occurrence']['message']}", "",
                         f"Anchor: {packet['occurrence']['file']}:{packet['occurrence']['line']}", ""]
                if packet.get("intent"):
                    lines += ["## Supplied deployment intent", "", packet["intent"], ""]
                for name, text in packet["files"].items():
                    numbered = "\n".join(f"{i + 1}: {line}" for i, line in enumerate(text.splitlines()))
                    lines += ["## Source: " + name, "", fenced(numbered), ""]
                lines += ["## Additional supplied snippets", ""]
                for snippet in packet["snippets"]:
                    lines += [str(snippet.get("file", "source")), "", fenced(snippet["text"]), ""]
                lines += ["## Recorded missing context", "", fenced(json.dumps(packet["missing"], indent=2)), "",
                          "Judge the condition independently. Missing evidence is not proof that a runtime definition or safeguard is absent.", ""]
                dest.writestr(f"readable/{case_id}.md", "\n".join(lines))
                index.append(f"- [{case_id}](readable/{case_id}.md)")
            dest.writestr("START_HERE.md", "\n".join(index) + "\n")
    print("Two readable packets created; 60 source listings and blank independent form per reviewer.")


if __name__ == "__main__":
    main()
