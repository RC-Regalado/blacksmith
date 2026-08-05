# Ollama Local Runbook

This guide targets the current reference host: 64 GB DDR3 RAM, NVIDIA GTX 1060
6 GB VRAM and Intel E5-1620v2.

## Server

Start Ollama in the foreground for local development:

```bash
OLLAMA_HOST=127.0.0.1:11434 \
OLLAMA_NUM_PARALLEL=1 \
OLLAMA_MAX_LOADED_MODELS=1 \
OLLAMA_KEEP_ALIVE=30m \
OLLAMA_LOAD_TIMEOUT=10m \
OLLAMA_CONTEXT_LENGTH=2048 \
OLLAMA_NO_CLOUD=1 \
CUDA_VISIBLE_DEVICES=0 \
ollama serve
```

For a systemd service, use the same values as service environment:

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_LOAD_TIMEOUT=10m"
Environment="OLLAMA_CONTEXT_LENGTH=2048"
Environment="OLLAMA_NO_CLOUD=1"
Environment="CUDA_VISIBLE_DEVICES=0"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
ollama ps
```

These settings favor reliability over throughput:

- one parallel request avoids GPU contention;
- one loaded model avoids VRAM pressure;
- 2048 context keeps the GTX 1060 usable;
- 30 minute keep-alive avoids repeated cold starts without pinning the model forever;
- 10 minute load timeout tolerates first-load stalls.

## Blacksmith Model

Build the project tool profile from the repository root:

```bash
ollama pull qwen3.5:4b
ollama create blacksmith-tools -f Modelfile
```

Current `Modelfile` baseline:

```text
FROM qwen3.5:4b
PARAMETER num_ctx 2048
PARAMETER temperature 0.2
SYSTEM You are a local assistant. Use tools only when the user asks to inspect files.
```

If VRAM pressure is still too high, prefer a smaller Q4 2B-3B instruct model and
keep the same `num_ctx 2048` and `temperature 0.2` profile.

## Blacksmith CLI

Run Blacksmith with tools enabled:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_BASE_URL=http://127.0.0.1:11434 \
AI_ASSISTANT_REQUEST_TIMEOUT=240 \
AI_ASSISTANT_CONTEXT_LIMIT=2048 \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_TIMEOUT=5 \
AI_ASSISTANT_MAX_READ_BYTES=8192 \
AI_ASSISTANT_MAX_DIRECTORY_ENTRIES=200 \
AI_ASSISTANT_MAX_DIRECTORY_DEPTH=0 \
python main.py
```

Manual tool checks:

```text
list files
```

```text
read README.md
```

Deterministic direct tool-call checks:

```json
{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}
```

```json
{"tool_call":{"name":"read_file","arguments":{"path":"README.md","max_bytes":1200}}}
```

## Troubleshooting

- First response times can exceed one minute on cold model load. Keep
  `AI_ASSISTANT_REQUEST_TIMEOUT=240` for manual validation.
- If `ollama ps` shows full GPU use while idle, lower `OLLAMA_KEEP_ALIVE` or run
  `ollama stop blacksmith-tools`.
- If answers hallucinate instead of using tools, paste the deterministic JSON
  tool call to separate model quality from tool execution.
- Do not expose `OLLAMA_HOST` outside loopback for this local-first setup.
