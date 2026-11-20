"""Reusable remote comparison service shared by CLI and API workers."""

from __future__ import annotations

from pathlib import Path

from ...diff_workflow import compare_outputs, parse_changed_lines
from ..capabilities import validate_diff_capabilities, validate_profile_capabilities
from .git import diff_against_remote


def compare_github_snapshots(
    *,
    base_source,
    head_source,
    output,
    profile="pr",
    policy="ratchet",
    summary="changed",
    gitleaks_path=None,
    base_file_manifest=None,
    head_file_manifest=None,
    analyzer=None,
):
    if analyzer is None:
        from ...cli import analyze_path as analyzer

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with base_source.materialize() as base_snapshot:
        with head_source.materialize() as head_snapshot:
            validate_profile_capabilities(base_snapshot, profile)
            validate_profile_capabilities(head_snapshot, profile)
            validate_diff_capabilities(base_snapshot)
            validate_diff_capabilities(head_snapshot)
            base_output = output / "base"
            head_output = output / "head"
            analyzer(
                base_snapshot.root,
                base_output,
                gitleaks_path,
                file_manifest=base_file_manifest,
                profile=profile,
                source_snapshot=base_snapshot,
            )
            analyzer(
                head_snapshot.root,
                head_output,
                gitleaks_path,
                file_manifest=head_file_manifest,
                profile=profile,
                source_snapshot=head_snapshot,
            )
            diff_text = diff_against_remote(
                base_tree=base_snapshot.root,
                head_repository=head_snapshot.repository,
                head_sha=head_snapshot.resolved_sha,
                host=base_source.target.host,
                token=base_source.client.token,
            )
            return compare_outputs(
                base_output,
                head_output,
                output,
                head_snapshot.root,
                policy_mode=policy,
                changed_lines=parse_changed_lines(diff_text),
                summary_mode=summary,
                diff_text=diff_text,
            )
