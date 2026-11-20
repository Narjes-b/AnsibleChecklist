# Setup, usage, and troubleshooting

## What actually worked (native Windows Ollama)

In the end, the simplest reliable path on this machine was the **native
Windows Ollama install**, not WSL2 — `ollama.exe` from
https://ollama.com/download, then:

```powershell
ollama pull qwen2.5-coder:7b     # ~4.68 GB download, Q4_K_M by default
# ollama serve runs automatically as a background service on install;
# if not: ollama serve
ollama run qwen2.5-coder:7b "explain this Ansible task: ..."   # smoke test
```

`explain.py`'s default `--host http://127.0.0.1:11434` reaches this directly
from Windows Python — no WSL networking involved. **If a WSL2 Ollama install
is also running on the same machine**, check which one actually owns port
11434 first (`Get-Process ollama` on Windows, and separately inside WSL) —
both bind to `127.0.0.1:11434` on their own side, and whichever you query
depends on where you run `curl`/the client from, not on which one you meant
to use. This caused a real, confusing failure in this project: `explain.py`
(Windows Python) kept getting `model not found` 404s from an empty **native**
Ollama instance while a fully-pulled model sat unreachable inside WSL, because
nothing had pulled the model on the native side yet.

## WSL2 path (attempted first; kept here because the failure modes are real and recur)

The sudo-free standalone tarball method below works and was used successfully
at one point, but hit enough WSL-specific friction that native Windows ended
up being the practical choice. Keep this section if you need WSL specifically
(e.g. to also run `ansible-lint`, which needs the POSIX `grp` module and does
not work on native Windows Python at all).

```bash
# Find the current release's actual Linux asset name first — it has changed
# format before (.tgz -> .tar.zst), so don't hardcode a filename from memory:
curl -s https://api.github.com/repos/ollama/ollama/releases/latest \
  | grep -o '"browser_download_url": *"[^"]*linux-amd64\.[^"]*"' | head -1

mkdir -p ~/ollama_local && cd ~/ollama_local
curl -L -o ollama.tar.zst <url from the command above>

# If `zstd` isn't installed (common on a minimal WSL image) and you can't
# apt-get it without sudo, tar --zstd will fail with "Cannot exec: zstd:
# Permission denied" or "No such file". Decompress with Python instead,
# inside a venv so pip doesn't need --break-system-packages / sudo:
python3 -m venv .extract_venv && .extract_venv/bin/pip install --quiet zstandard
.extract_venv/bin/python3 - <<'PY'
import zstandard, tarfile
with open("ollama.tar.zst", "rb") as f:
    with zstandard.ZstdDecompressor().stream_reader(f) as reader:
        with tarfile.open(fileobj=reader, mode="r|") as tar:
            tar.extractall(path=".")
PY
# (or `tar --zstd -xf ollama.tar.zst` directly if zstd is actually available)

# Run directly, no install step, no PATH changes required:
./bin/ollama serve &
./bin/ollama pull qwen2.5-coder:7b
```

### Troubleshooting: WSL2's VM can silently lose downloaded data

In this project, a ~1.6GB partially-downloaded model blob (tracked and
confirmed growing correctly across several hourly checks) **disappeared
entirely** — the blobs directory came back empty — after the WSL2 VM was
shut down overnight with no process keeping it alive (`uptime` on the next
session showed "up 1 min", i.e. a fresh VM boot). This looks like a WSL2
vhdx-level issue, not an Ollama bug. If a long download needs to survive
across a WSL session gap, keep a process running in a detached tmux session
(`tmux new-session -d -s <name> "<command>"` — WSL2's VM tears down shortly
after the last invoking process exits) and verify real on-disk byte progress
periodically rather than trusting that a resume will pick up where it left
off after an extended gap.

### Troubleshooting: an upstream network actively resetting large downloads

A university network connection was observed actively resetting a large
binary download at inconsistent byte thresholds (143KB-507KB) on every
attempt, while a small 19KB control file downloaded instantly and reliably —
this pattern (small files fine, large files reset, not just slow) indicates
active interference (firewall/DPI), not generic slowness or a flaky link.
`curl --retry N` is not sufficient here, since it gives up once its retry
budget is exhausted against a connection that keeps resetting mid-transfer.
A simple outer retry loop that treats each `curl -C -` invocation as
disposable and relaunches it indefinitely worked:

```bash
#!/usr/bin/env bash
cd ~/ollama_local
URL="<release asset url>"; OUT="ollama.tar.zst"
while true; do
  curl -L -C - --connect-timeout 20 --speed-limit 500 --speed-time 45 -o "$OUT" "$URL"
  [ $? -eq 0 ] && break
  sleep 3
done
```

If this is still too slow, switching to a different network (and, per above,
verifying real byte progress rather than trusting percentage displays, which
can look like it "regressed" when parallel download chunks restart
individually) is more effective than tuning retry parameters further.

### Troubleshooting: `sudo` hangs

If `ollama`'s official installer (or anything else needing `sudo`) hangs with no
output, it is very likely sitting at an invisible password prompt. Check with:

```bash
ps aux | grep sudo   # a long-lived `sudo <something>` with no CPU time = waiting on input
sudo -n true         # returns instantly with "a password is required" if that's the issue,
                      # vs. hanging for ~1-2 minutes if it's a DNS/hostname-resolution issue instead
```

If it's the password case, kill the hung process and use the sudo-free tarball
method above instead of trying to supply a password non-interactively.

### Troubleshooting: the model loads but every explanation looks ungrounded or wrong

Check two things before suspecting the model itself:
1. **Is `--num-ctx` large enough for your prompts?** Ollama's server defaults
   to a 4096-token context window regardless of what a model's `/api/tags`
   entry advertises as its max. A prompt that exceeds the active window is
   silently truncated — this produced a schema-breaking, completely
   off-topic response in this project's own eval run before `--num-ctx 8192`
   (now `explain.py`'s default) was set explicitly. See
   `eval/EVAL_RESULTS.md` for the full writeup.
2. **Is the source-context field actually populated in your input CSV?**
   `explain.py`/`prompt_template.py` read `source_context`, falling back to
   `original_code_or_issue` (the column name used by this project's own
   comparison CSVs). If you feed a CSV with neither column, or an empty one,
   the model will still respond confidently — it just won't be grounded in
   anything, and may say so ("the file is empty") or may confabulate
   plausible-sounding specifics instead. Don't assume a specific-sounding
   answer means real grounding; check the `context_supplied_to_model` field
   in the audit record.

## Running the explanation pipeline

```bash
cd local-llm/scripts

# Smoke test on a handful of issues first:
python explain.py --input ../../annotation-comparison/consolidated-comparison.csv \
  --id-col issue_id --limit 3

# Full run over the evaluation set:
cd ..
python eval/run_eval.py

# Build the Task 3 side-by-side comparison once eval has run:
python build_task3_comparison.py
```

Configuration knobs (`explain.py --help` for the full list):
- `--model` — defaults to `qwen2.5-coder:7b`; pass any other pulled Ollama tag to
  compare models without touching code.
- `--host` — defaults to `http://127.0.0.1:11434`; point at a different host if
  Ollama runs elsewhere (e.g. native Windows Ollama reachable from WSL2 at the
  Windows host's IP).
- `--temperature` — defaults to 0.1 (low, for grounded/repeatable explanations).
- `--skip-existing` — resume a partially-completed run without re-calling the
  model for issues that already have an audit record.

## What each deliverable file is

| File | Task | Contents |
| --- | --- | --- |
| `MODEL_SELECTION.md` | 2.2 | Model/engine research, comparison table, recommendation, sources |
| `PROMPT_DESIGN.md` | 2.3 | Explanation schema and the exact prompt text |
| `scripts/explain.py` | 2.4 | The integration: issue in, audited explanation out |
| `outputs/*.json` | 2.5 | One full audit record per explained issue |
| `eval/eval_cases.csv` | 2.6 | 12 hand-picked issues covering the required case types |
| `eval/EVAL_RESULTS.md` | 2.6 | Actual results and failure cases, not just the harness |
| `task3-comparison.csv` | 3 | Side-by-side: existing agent vs. local model, rubric columns for scoring |
| `INTEGRATION.md` | — | How this fits the existing project; what's reused vs. new; what's incomplete |

## Known limitations (stated here, not buried)

- See `INTEGRATION.md`'s "What remains incomplete" section for the authoritative,
  up-to-date list — it's kept next to the design docs so it doesn't drift out of
  sync with what was actually run.
