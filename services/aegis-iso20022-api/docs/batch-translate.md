# Batch translate API

The translator service can convert multiple MT messages in a single request by uploading a batch file. Batch mode reuses the existing prevalidation and MT→MX mapping logic but keeps the entire workflow in memory—no files are written to disk and no database is involved.

## Supported inputs

- `.dat` / `.txt` files that contain a single batch in the following format:
  - A header line (prefixed with `HDR|`) containing key/value pairs such as `BatchID`, `Sender`, `MsgCount`, etc.
  - One or more MT blocks separated by a line that only contains `$`.
  - A trailer line (prefixed with `TRL|`) summarising totals.
- `.zip` archives that contain one or more `.dat`/`.txt` files matching the structure above. Nested directories are allowed; non-batch files are ignored.

The parser is resilient to blank lines and both Unix/Windows newlines.

## Endpoint

```
POST /translate/batch
```

| Parameter | Location | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `file` | form-data | file | required | Batch file to process (`.dat`, `.txt`, or `.zip`). |
| `prevalidate` | query | bool | `true` | Run MT prevalidation before translation. If disabled, messages skip the `PRESENCE` checks. |
| `max_workers` | query | int | `4` | Maximum number of messages processed concurrently per batch file. |
| `responseFileFormat` | query | str (`zip` &#124; `json`) | `zip` | `zip` streams a downloadable archive (default). Use `json` to get the previous JSON structure. |

**Response**

```jsonc
{
  "batches": [
    {
      "source": "MTBatch_20251030.dat",
      "header": { "BatchID": "...", "Sender": "...", ... },
      "trailer": { "TotalMessages": "3", "Valid": "3", ... },
      "summary": { "total": 3, "succeeded": 3, "failed": 0 },
      "results": [
        {
          "index": 1,
          "status": "ok",
          "mt_type": "MT101",
          "mx_type": "pain.001.001.12",
          "validation": { "ok": true, "errors": [] },
          "xml": "<?xml version='1.0' ...>",
          "metrics": { "latency_ms": 45.12 },
          "audit": {
            "source_mt": "MT101",
            "target_mx": "pain.001.001.12",
            "...": "..."
          }
        },
        {
          "index": 3,
          "status": "error",
          "error": { "status_code": 422, "detail": { ... } }
        }
      ]
    }
  ],
  "summary": {
    "total_batches": 1,
    "total_messages": 3,
    "succeeded": 2,
    "failed": 1,
    "processed_at": "2025-10-30T10:15:27.123456+00:00"
  }
}
```

Each message is processed in-memory; XML output is embedded directly in the response. When a message fails (for example, prevalidation rejects it), the response captures the HTTP error code and detail JSON returned by the standard `/translate` handler.

## XSD validation backends

The translator validates generated MX documents using pluggable schema backends:

- **Default (`auto`)** – uses the Python `xmlschema` package when available to enforce XSD 1.1 schemas, and falls back to the built-in lxml validator otherwise.
- **`xmlschema11`** – explicitly require the `xmlschema` backend; the service returns an error if the dependency is missing.
- **`lxml`** – force the original libxml2/lxml validator (XSD 1.0 only).
- **`remote`** – delegate validation to an external service (for example, the `aegis-xsd-validator` sidecar). Requires `XSD_VALIDATOR_ENDPOINT` and optional `XSD_VALIDATOR_ENGINE`.

Set the environment variable `XSD_VALIDATOR_BACKEND` to choose the backend at runtime:

```bash
export XSD_VALIDATOR_BACKEND=xmlschema11   # prefer XSD 1.1 support
```

When a schema cannot be located (or a backend fails to parse it), validation is skipped and the response contains a warning entry in `validation.errors` so tenants can decide whether to treat the result as acceptable.

## ZIP payload layout

The default `zip` response streams an archive with the following structure:

- `summary.json` – same structure shown above, plus a `processed_at` ISO 8601 timestamp.
- `<batch-id>/record-<###>_<mx>.xml` – generated MX documents for successful records.
- `<batch-id>/record-<###>_error.json` – details for records that failed prevalidation or translation.

## Sample batch

An example batch is available at `batch-mode-samples/MTBatch_20251030.dat`. It contains:

- `HDR` / `TRL` metadata,
- Three MT records (MT101, MT103, MT196),
- `$` separators between records.

The automated tests (`tests/test_batch_translate_api.py`) load this file to assert the batch endpoint behaviour. Use it as a template for constructing custom batches.
