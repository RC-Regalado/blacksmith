# FINDING-TOOL-PARSE-001

Severity: HIGH

## Summary

`ToolCallInterpreter` could propagate `json.JSONDecodeError` when assistant
text contained a balanced brace-delimited candidate that was not valid JSON.

## Impact

- A valid model turn could crash during tool-call interpretation.
- No tool would execute.
- The interaction could end as `outcome=error`.
- Arbitrary assistant prose containing balanced braces could reach the fallback
  JSON parser.

## Required Invariant

For every assistant string `S`, `ToolCallInterpreter.interpret(S)` must return a
controlled domain result or controlled domain error. It must not leak JSON
parser exceptions.

## Reproduction

Input:

```text
not json before {not valid json}
```

Reproduction command:

```bash
venv/bin/python -m pytest -q tests/test_tools.py::test_interpreter_does_not_leak_json_decode_error_for_invalid_brace_candidate
```

Before remediation this failed with:

```text
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

## Remediation

The fallback brace-candidate parse now catches `json.JSONDecodeError` and
returns `None`, which preserves the controlled "no tool call" result for
assistant text that is not valid tool-call JSON.

Invalid structured `tool_call` payloads still raise the existing controlled
`InvalidToolCallError`.

## Validation

Post-remediation validation:

```bash
venv/bin/python -m pytest -q tests/test_tools.py::test_interpreter_does_not_leak_json_decode_error_for_invalid_brace_candidate
venv/bin/python -m pytest -q tests/test_tools.py
```
