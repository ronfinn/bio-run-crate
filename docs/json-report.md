# JSON validation report

**Status:** implemented, in `src/bio_run_crate/reporting/json_report.py`.

## 1. Purpose

The JSON report renders one run's validation findings in a shape a machine can
parse: a CI job deciding whether to fail a pipeline, an audit tool recording what
was checked, a script summarising many runs at once. The terminal output of
`validate` is for a person reading it now; this report is for a program reading
it later, possibly a version or two later.

Two properties follow from that audience, and both are contracts rather than
conveniences:

- **A stable, versioned schema**, so a consumer can be written against a known
  document shape and can detect if that shape ever changes (§2, §3).
- **Deterministic serialization**, so two reports for the same result are
  byte-identical and a report can be diffed, hashed, or committed (§5).

The report is produced by a pure function of an already-parsed manifest and the
`ValidationResult` the validation engine produced for it. It never re-reads the
manifest, re-runs validation, mutates its inputs, reads the clock, or touches the
network — see `docs/architecture.md` §3.5.

## 2. Schema version

The top-level `schema_version` field identifies the version of **this document
format**. It is:

- **not** the package version (`bio-run-crate version`);
- **not** the manifest's `manifest_version`.

The current value is `"1"`. It changes only when the document shape changes in a
way that could break a consumer — for example if a field were removed or
renamed, or its type changed. Adding the field would not otherwise be
distinguishable from any other JSON, so consumers should read it before anything
else and refuse a version they do not understand.

## 3. Schema

A report is a single JSON object with exactly four keys, in this order:

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Version of the report format. Currently `"1"`. See §2. |
| `run_id` | string | The `run_id` of the validated run, copied from the manifest. Identifies which run the report is about. |
| `summary` | object | Count of findings per severity. Always all three keys. See §4. |
| `findings` | array | Every finding, in canonical order. Empty when the manifest produced none. See §3.2. |

### 3.1 `summary`

| Field | Type | Description |
|---|---|---|
| `ERROR` | integer ≥ 0 | Number of ERROR findings. |
| `WARNING` | integer ≥ 0 | Number of WARNING findings. |
| `INFO` | integer ≥ 0 | Number of INFO findings. |

### 3.2 `findings[]`

Each element is an object with exactly four keys, in this order:

| Field | Type | Description |
|---|---|---|
| `rule_id` | string | The stable identifier of the rule that produced the finding, `<NAMESPACE>-<NNN>` (e.g. `CORE-001`). See `docs/data-model.md` §A.8.1. |
| `severity` | string | One of `ERROR`, `WARNING`, `INFO` — the plain severity name, never a number or an object. |
| `message` | string | Human-readable explanation. Wording may change between versions; `rule_id` is the stable handle, not the message. |
| `location` | object | Where in the manifest the finding applies. |

`location` is an object with a single `path` key, holding a textual pointer into
the parsed manifest using dotted field names and bracketed list indices — for
example `outputs[1].checksum`. A finding about the manifest as a whole uses `$`.
This is the same structured shape the internal `Location` model uses; the report
deliberately does not invent a second, incompatible representation.

## 4. Severity summary semantics

`summary` counts findings, not rules: one rule that fires three times
contributes three. All three severities are always present, including those with
a count of zero, so a consumer can read `summary.ERROR` unconditionally rather
than treating a missing key as zero.

`summary` is derived from `findings` and is always consistent with it: the sum of
the three counts equals the length of `findings`. It exists so that a consumer
that only needs a verdict does not have to walk the array.

Severity carries the same meaning as everywhere else in the tool: `ERROR` means
the manifest is not acceptable, `WARNING` means it is acceptable but
questionable, `INFO` is an observation requiring no action. Only `ERROR` affects
the exit code (§8).

## 5. Determinism

Semantically identical reports serialise to byte-identical text. Every degree of
freedom in the output is pinned down deliberately:

- **Object key order** is the field declaration order shown in §3, at the top
  level and in nested objects alike. Keys are *not* sorted alphabetically: the
  declared order groups related fields more readably and is equally stable.
- **Finding order** is the canonical order imposed by `ValidationResult` on every
  construction path: by severity (ERROR, then WARNING, then INFO), then by
  location path, rule ID, and message. The order rules happened to run in, and
  the order a caller happened to supply findings in, cannot show through.
- **Formatting** is two-space indentation, with no trailing whitespace on any
  line.
- **Line endings**: the document ends with exactly one newline, so it behaves as
  a well-formed text file under `diff` and in version control.
- **No styling**: the report is written directly to stdout rather than through
  the Rich console used for terminal output, so no ANSI escape or wrapping can
  ever appear in it.

Nothing volatile is included — no timestamp, no hostname, no run duration, no
absolute paths beyond what the manifest itself declares. A field is present only
because a consumer needs it now.

## 6. CLI invocation

The report is reachable through the existing `validate` command, via a format
option:

```
# Human-readable terminal output (the default)
uv run bio-run-crate validate examples/synthetic/valid-run.yaml
uv run bio-run-crate validate examples/synthetic/valid-run.yaml --format text

# JSON report on stdout
uv run bio-run-crate validate examples/synthetic/valid-run.yaml --format json
uv run bio-run-crate validate examples/synthetic/valid-run.yaml -f json
```

`--format` is an enumeration rather than a `--json` boolean flag because further
formats are expected — Markdown is issue #8 — and adding a member is a smaller
change for users than adding a second mutually exclusive switch. An unrecognised
value is rejected by the CLI with a usage error listing the valid choices.

The format chooses only how a result is *presented*. The rule engine runs exactly
once either way, over the same manifest, producing the same findings.

## 7. stdout and stderr

| Mode | stdout | stderr |
|---|---|---|
| `--format text` (default) | One-line verdict and per-run summary. | Findings table; schema-error table on a structural failure. |
| `--format json` | Exactly one JSON report, and nothing else. | Nothing, except on a structural failure (§9). |

In JSON mode the findings table and the human summary are both suppressed, so
stdout holds a single parseable document. `bio-run-crate validate run.yaml
--format json > report.json` therefore yields a valid report file.

## 8. Exit codes

The format option does not change the exit code. `validate` behaves identically
in both modes (see `docs/architecture.md` §3.1):

| Code | Meaning | JSON report on stdout? |
|---|---|---|
| `0` | The manifest parsed and produced no ERROR findings. | Yes |
| `1` | The manifest parsed and produced at least one ERROR finding. | Yes |
| `2` | The manifest never reached the rule engine. | No — see §9 |

A WARNING-only result therefore emits a full report and exits `0`. Consumers
should read the report rather than infer detail from the exit code: `0` and `1`
both mean "validation ran, here are the results".

## 9. Structural failures produce no report

A manifest that is missing, unreadable, not valid YAML, has a non-mapping top
level, or fails the `RunManifest` schema never reaches the rule engine. There is
no `RunManifest` and no `ValidationResult`, and therefore nothing this report
could describe. In that case `validate --format json`:

- writes **no** JSON to stdout;
- keeps its existing human-readable diagnostics on stderr;
- exits `2`, exactly as in text mode.

This is the same boundary the tool draws everywhere else: structural failures are
Pydantic's errors and are deliberately not dressed up as `CORE-*` findings, since
they are not rule findings (`docs/architecture.md` §3.1–3.2). A machine-readable
representation of *parsing and schema* failures would be a second, differently
shaped document with its own version; if it is ever wanted, it should be designed
as such rather than smuggled into this one.

## 10. Example

Validating [`examples/synthetic/valid-run.yaml`](../examples/synthetic/valid-run.yaml),
which is schema-valid but leaves `output-002` without a checksum:

```
$ uv run bio-run-crate validate examples/synthetic/valid-run.yaml --format json
```

```json
{
  "schema_version": "1",
  "run_id": "run-001",
  "summary": {
    "ERROR": 0,
    "WARNING": 1,
    "INFO": 0
  },
  "findings": [
    {
      "rule_id": "CORE-003",
      "severity": "WARNING",
      "message": "Output 'output-002' has no checksum; a checksum is recommended for outputs so the artifact can be verified.",
      "location": {
        "path": "outputs[1].checksum"
      }
    }
  ]
}
```

Exit code `0`: a WARNING does not make a manifest invalid.

A clean run produces the same document with an empty `findings` array and an
all-zero summary:

```json
{
  "schema_version": "1",
  "run_id": "run-001",
  "summary": {
    "ERROR": 0,
    "WARNING": 0,
    "INFO": 0
  },
  "findings": []
}
```

All values above are synthetic, as is every example in this repository.

## 11. Not covered here

The **Markdown report** is a separate output format and a separate piece of work
(issue #8). It is not implemented, and nothing in this document applies to it.
Writing a report to a file rather than to stdout is likewise not implemented;
shell redirection covers the case today.
