# Model Profiles

Phase 1 keeps model choice operator-controlled through environment variables.

## Recommended Profiles

| Profile | Recommended target | Context | Use |
|---|---|---:|---|
| development | Gemma 4 E2B Q4 or nearest installed small Gemma Q4 tag | 4096 | Daily development and quick smoke checks |
| validation | Gemma 4 E4B Q4 or nearest installed medium Gemma Q4 tag | 4096 | Functional validation |
| evaluation | Gemma 4 12B Q4 or nearest installed 12B Q4 tag | 8192 | Manual quality evaluation on the reference machine |

Exact Ollama tags can differ by registry and quantization. Set the installed tag explicitly:

```bash
AI_ASSISTANT_PROVIDER=ollama
AI_ASSISTANT_MODEL=<installed-ollama-tag>
AI_ASSISTANT_CONTEXT_LIMIT=4096
AI_ASSISTANT_REQUEST_TIMEOUT=180
```

Use `AI_ASSISTANT_CONTEXT_LIMIT=8192` only for evaluation runs where memory pressure is acceptable.

## Smoke

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q
```

Real Ollama validation stays separate:

```bash
AI_ASSISTANT_MODEL=<installed-ollama-tag> \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```
