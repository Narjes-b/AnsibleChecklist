# Local LLM selection for explainable Ansible issue analysis

## Hardware and environment (measured, not assumed)

Confirmed via `nvidia-smi` on this machine (both native Windows and WSL2 report the
same GPU, as expected for WSL2's GPU passthrough):

```
name, memory.total [MiB]
NVIDIA GeForce RTX 5060 Laptop GPU, 8151 MiB
```

- **VRAM: ~8 GB** — this is the *binding* constraint. The brief mentioned "8-12 GB,"
  but the actual card is at the low end (8 GB), so every size estimate below assumes
  8 GB, not 12.
- **RAM: 32 GB** (per brief) — generous; relevant mainly for CPU-offloaded layers if
  a model doesn't fully fit in VRAM.
- **OS: Windows + WSL2.** Ollama runs natively on Windows and also inside WSL2 with
  GPU passthrough; `ollama` was not yet installed in the WSL2 environment this
  session (`which ollama` → not found). Native Windows Ollama is the simpler install
  path and avoids WSL2 GPU-passthrough quirks entirely, so that's the recommended
  deployment target — see [Setup](#setup).

## Candidates compared

| Model | Params | Quant (GGUF) | Approx. VRAM footprint | Code/explanation signal | Fit on this GPU |
| --- | --- | --- | --- | --- | --- |
| **Qwen2.5-Coder-7B-Instruct** | 7B | Q4_K_M | ~4.7 GB weights + ~1-2 GB KV cache/runtime | Strongest reported code-reasoning score in its size class: CRUXEval Input-CoT 56.5 / Output-CoT 56.0 (full-precision base model, Seed-Coder paper table), HumanEval ~88.4% (secondary source, treat as a rough figure); trained explicitly for generation, repair, explanation, and completion | **Comfortable fit**, several GB of headroom for context |
| Qwen2.5-Coder-14B-Instruct | 14B | Q4_K_M | ~8.5 GB weights alone + ~2.9 GB KV cache + ~1.2 GB runtime overhead (community VRAM-fit estimator) | Presumably stronger reasoning than the 7B (same family, larger), but no 8GB-specific benchmark found | **Does not comfortably fit** 8 GB once context/KV-cache is added; would need partial CPU offload or a very short context window — a stretch option, not the default |
| DeepSeek-Coder-6.7B-Instruct | 6.7B | Q4_K_M | ~4 GB | CRUXEval clearly behind Qwen2.5-Coder-7B (39.0/41.0 vs 56.5/56.0, Seed-Coder table); best known for fill-in-the-middle/autocomplete, not explanation | Fits easily, but weaker reasoning — not chosen |
| Llama-3.1-8B-Instruct | 8B | Q4_K_M | ~4.9 GB | General-purpose instruction model; HumanEval ~72.6% in one secondary source, no code-specific reasoning benchmark found; not trained specifically for code | Fits, but weaker on code-specific tasks than a code-specialized model of similar size |
| CodeLlama-7B-Instruct | 7B | Q4_K_M | ~4 GB | Older generation; generally ranked below Qwen2.5-Coder in current guides; reasonable at explaining code but outranked by it | Fits, but superseded |
| Phi-4-mini (3.8B) | 3.8B | Q4 | ~2-2.5 GB | Smallest footprint, most headroom for context; lower absolute reasoning ceiling | Viable fallback if 7B proves too slow on this GPU, not the primary pick |

Sources for the numbers above: Seed-Coder paper's CRUXEval comparison table (arXiv
2506.03524), an Ollama model-size cheat sheet, and several 2026 "best local
LLM for N GB VRAM" guides cross-checked against each other (these guides disagree on
details in places, e.g. one incorrectly lists a 14B model as fitting 8GB — flagged
and discounted here). No vendor benchmark specifically targets Ansible/YAML/Jinja2
reasoning; none was found for any candidate. That capability is evaluated directly
in this project's own [evaluation suite](#evaluation) instead of taken on faith from
a generic coding benchmark.

## Recommendation

**Qwen2.5-Coder-7B-Instruct, Q4_K_M quantization, served via Ollama.**

Rationale:
- Best measured code-reasoning signal of any model that comfortably fits this GPU's
  actual 8 GB VRAM (not the 14B's precarious fit).
- Code-specialized training (generation, repair, explanation, completion) matches
  the task — explaining *why* Ansible/YAML/Jinja2 code is wrong, not just classifying
  it.
- Small enough to leave real headroom for the context this task needs: the detected
  issue, surrounding YAML, and relevant task/variable context all have to fit in the
  prompt alongside the model weights and KV cache.
- Reproducible and fully offline after the initial `ollama pull` — no API keys, no
  network calls at inference time, consistent with the "privacy / offline" and
  "licensing / reproducibility" requirements.

**Alternative worth testing later, not chosen now:** a newer "Qwen 3.5 9B" /
"Qwen3-9B"-class model was mentioned in several 2026 guides as fitting 8GB at Q4 and
beating Qwen2.5-Coder-7B on some benchmarks. It's listed here as a documented
alternative rather than the recommendation because (a) the guides citing it are
lower-confidence SEO-style sources with inconsistent details elsewhere, and (b)
unlike Qwen2.5-Coder, no peer-reviewed or vendor benchmark table was found for it
in this research pass. If a second iteration is wanted, pulling it alongside
Qwen2.5-Coder-7B and running both through this project's evaluation suite (see
below) would settle it with actual evidence instead of guide-reading.

**Stretch option:** Qwen2.5-Coder-14B-Instruct, if explanation quality from the 7B
proves insufficient in practice. Expect to need a reduced context window and/or
partial CPU offload (32 GB system RAM makes this viable, just slower). Re-evaluate
only after running the 7B through the evaluation suite below and finding concrete,
specific shortfalls — not preemptively.

## Inference engine: Ollama (over raw llama.cpp)

| | Ollama | llama.cpp (direct) |
| --- | --- | --- |
| Setup complexity | Single installer, `ollama pull <model>`, done | Manual build, manual GGUF download/management |
| API | REST API on localhost, JSON in/out, `format: "json"` for schema-constrained output | Also has a server mode with an OpenAI-compatible API, but more manual configuration |
| Model management | Built-in (list/pull/rm, named tags per quantization) | Manual file management |
| Reproducibility | Model name + tag is sufficient to pin a version | Need to track the exact GGUF file/commit |
| Integration effort for this project | Low — one HTTP client, no new build toolchain | Higher — would add a C++ build dependency to a Python project for no capability this task needs |

Ollama is the right choice here: this project doesn't need anything llama.cpp
exposes that Ollama doesn't (no custom sampling research, no embedding-specific
tuning), and Ollama's model management and JSON-constrained output directly serve
the "structured, consistent outputs" and "reproducible execution with documented
model/config versions" requirements. Fallback to raw llama.cpp is cheap later if a
real llama.cpp-specific need shows up — the interface in this project's integration
code (`local-llm/scripts/explain.py`) only talks to a REST endpoint, so swapping the
backend doesn't require rewriting the pipeline (see the modularity note in
[`INTEGRATION.md`](INTEGRATION.md)).

## Setup

```bash
# Windows (recommended) — download the installer from https://ollama.com/download
# or, inside WSL2:
curl -fsSL https://ollama.com/install.sh | sh

ollama pull qwen2.5-coder:7b     # ~4.7 GB download, Q4_K_M by default
ollama serve                     # starts the local REST API on 127.0.0.1:11434 (if not already running as a service)
ollama run qwen2.5-coder:7b "explain this Ansible task: ..."   # smoke test
```

**Update: this was verified end-to-end in a later session.** `qwen2.5-coder:7b`
(Q4_K_M) was pulled via native Windows Ollama and run live against
`scripts/explain.py` for all 12 cases in `eval/eval_cases.csv`. Real results,
including two pipeline bugs found and fixed along the way (a field-name
mismatch that silently dropped all source context, and Ollama's 4096-token
default context window truncating larger prompts) and a significant model
calibration finding, are in [`eval/EVAL_RESULTS.md`](eval/EVAL_RESULTS.md).
See also [`INTEGRATION.md`](INTEGRATION.md)'s "what remains incomplete"
section, kept up to date rather than left as a one-time snapshot.
