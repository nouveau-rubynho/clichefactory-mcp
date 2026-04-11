---
name: clichefactory
description: Extract structured data from documents (PDF, images, DOCX, XLSX, CSV, EML) into validated JSON using ClicheFactory
metadata: {"openclaw": {"requires": {"bins": ["uvx"]}, "primaryEnv": "LLM_API_KEY", "install": [{"id": "uv", "kind": "uv", "package": "clichefactory-mcp", "bins": ["clichefactory-mcp"], "label": "Install ClicheFactory MCP server (uv)"}]}}
---

# ClicheFactory — Structured Document Extraction

ClicheFactory extracts structured, Pydantic-validated data from documents. Give it a file and a JSON schema — it returns clean JSON.

This skill requires the `clichefactory` MCP server. Register it once:

```bash
openclaw mcp set clichefactory '{"command":"uvx","args":["clichefactory-mcp"],"env":{"LLM_MODEL_NAME":"gemini/gemini-3-flash-preview","LLM_API_KEY":"YOUR_KEY"}}'
```

Or for ClicheFactory cloud (service mode):

```bash
openclaw mcp set clichefactory '{"command":"uvx","args":["clichefactory-mcp"],"env":{"CLICHEFACTORY_API_KEY":"cliche-your-key"}}'
```

Verify with `openclaw mcp list`.

## MCP Tools

### extract

Primary tool. Takes a document file path and a JSON schema, returns structured JSON matching the schema.

**Parameters:**
- `file` — absolute path to the document
- `schema` — JSON schema (inline object or path to a `.json` file)
- `mode` — `"local"` (BYOK) or `"service"` (ClicheFactory cloud)
- `extraction_mode` — omit for default OCR+LLM, or `"fast"` for multimodal LLM without OCR
- `model` — LLM override, e.g. `"openai/gpt-4o"`

### to_markdown

Converts a document to readable markdown. Use this to inspect contents before building a schema, or when extract fails and you need to understand the document structure.

**Parameters:**
- `file` — absolute path to the document
- `mode` — `"local"` or `"service"`

### doctor

Checks configuration, Python dependencies, and system binaries. Call this when extraction fails to diagnose the issue.

## Workflow

1. If the user provides a document without a schema, call `to_markdown` first to see the content.
2. Build a JSON schema from what you see (or from the user's description of what they need).
3. Call `extract` with the file and schema.
4. If extraction returns validation errors, inspect them — the schema may need adjustment (wrong types, missing fields, etc.).
5. If extraction fails entirely, try switching `mode` (local ↔ service), then call `doctor` to check the setup.

## Supported File Types

PDF, PNG, JPG, JPEG, WebP, GIF, BMP, DOCX, DOC, ODT, XLSX, CSV, EML, TXT, MD.

## Schema Tips

Schemas follow standard JSON Schema. Example for an invoice:

```json
{
  "type": "object",
  "properties": {
    "invoice_number": {"type": "string"},
    "date": {"type": "string", "description": "Invoice date in YYYY-MM-DD format"},
    "vendor": {"type": "string"},
    "line_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "number"},
          "unit_price": {"type": "number"},
          "total": {"type": "number"}
        }
      }
    },
    "total_amount": {"type": "number"}
  }
}
```

Use `description` fields in the schema to guide extraction — the LLM reads them.

## More Information

- SDK and CLI: [clichefactory on PyPI](https://pypi.org/project/clichefactory/)
- MCP server: [clichefactory-mcp on PyPI](https://pypi.org/project/clichefactory-mcp/)
- Website: [clichefactory.com](https://clichefactory.com)
