# v0.0.5 benchmark corpus

`v005-corpus.example.json` is the fast source-tree smoke corpus. The permanent
shape corpus is generated deterministically so the 44k-line pathological file
does not bloat Git history:

```bash
python scripts/build_v005_benchmark_corpus.py /tmp/ansibleguard-v005-corpus
python scripts/benchmark_v005.py \
  --manifest /tmp/ansibleguard-v005-corpus/manifest.json \
  --json /tmp/ansibleguard-v005-baseline.json
```

The generated manifest records all size parameters. It includes:

- a small role;
- a medium multi-role project;
- a repository with many small YAML files;
- a variable-heavy repository;
- a 4,000-task, at-least-44,000-line pathological task file.

Baselines are intentionally hardware/profile specific. Store the baseline with
the controlled CI or research environment, then enforce it with
the same manifest:

```bash
python scripts/benchmark_v005.py \
  --manifest /tmp/ansibleguard-v005-corpus/manifest.json \
  --baseline /tmp/ansibleguard-v005-baseline.json \
  --max-slowdown 1.25
```

For an end-to-end internal-engine stress run:

```bash
python -m ansibleguard.cli \
  /tmp/ansibleguard-v005-corpus/pathological-large-task-file \
  --profile developer-fast --fail-on never \
  --output /tmp/ansibleguard-v005-pathological-output
```

Never compare timings produced by different hardware or semantic/provider
environments as if they were one gate.
