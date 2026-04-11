"""
Shared helpers for the ClicheFactory MCP server.

Handles config resolution, client construction, schema parsing,
diagnostics, and error formatting.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from clichefactory import Client, Endpoint, factory
from clichefactory._config import (
    CLIConfig,
    config_file_path,
    load_config,
    resolve_api_key,
    resolve_base_url,
    resolve_model,
    resolve_model_api_key,
    resolve_ocr_api_key,
    resolve_ocr_model,
)
from clichefactory.errors import ClicheFactoryError, ConfigurationError, ErrorInfo


# ---------------------------------------------------------------------------
# Schema resolution
# ---------------------------------------------------------------------------

def resolve_schema(schema: str | dict[str, Any]) -> dict[str, Any]:
    """Accept a file path or an inline dict and return a parsed JSON schema."""
    if isinstance(schema, dict):
        return schema
    p = Path(schema)
    if not p.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema}")
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Client construction
# ---------------------------------------------------------------------------

def build_client(
    *,
    mode: str | None = None,
    model: str | None = None,
    model_api_key: str | None = None,
    ocr_model: str | None = None,
    ocr_api_key: str | None = None,
) -> Client:
    """Build a clichefactory Client using the same config cascade as the CLI.

    Resolution order (highest priority first):
        tool parameter → environment variable → ~/.clichefactory/config.toml → default
    """
    cfg = load_config()
    resolved_mode = mode or cfg.default_mode

    if resolved_mode == "service":
        api_key = resolve_api_key(cli_flag=None, cfg=cfg)
        if not api_key:
            raise ConfigurationError(
                ErrorInfo(
                    code="mcp.missing_api_key",
                    message="No ClicheFactory API key configured for service mode.",
                    hint=(
                        'Try mode="local" instead if an LLM key is configured. '
                        "Otherwise set CLICHEFACTORY_API_KEY in the MCP server environment, "
                        'or run "clichefactory configure" in a terminal.'
                    ),
                )
            )
        base_url = resolve_base_url(cli_flag=None, cfg=cfg)

        model_name = resolve_model(cli_flag=model, cfg=cfg)
        model_key = resolve_model_api_key(cli_flag=model_api_key, cfg=cfg)

        model_ep = None
        if model_name:
            model_ep = Endpoint(provider_model=model_name, api_key=model_key or None)

        return factory(
            api_key=api_key,
            base_url=base_url,
            mode="service",
            model=model_ep,
        )

    # --- local mode ---
    model_name = resolve_model(cli_flag=model, cfg=cfg)
    model_key = resolve_model_api_key(cli_flag=model_api_key, cfg=cfg)

    if not model_name:
        raise ConfigurationError(
            ErrorInfo(
                code="mcp.missing_model",
                message="No LLM model configured for local mode.",
                hint=(
                    'Try mode="service" instead if a ClicheFactory API key is configured. '
                    "Otherwise set LLM_MODEL_NAME and LLM_API_KEY in the MCP server environment, "
                    'or run "clichefactory configure --local" in a terminal.'
                ),
            )
        )

    model_ep = Endpoint(provider_model=model_name, api_key=model_key or None)

    ocr_name = resolve_ocr_model(cli_flag=ocr_model, cfg=cfg)
    ocr_key = resolve_ocr_api_key(
        cli_flag=ocr_api_key, cfg=cfg, model_api_key=model_key,
    )
    ocr_ep = None
    if ocr_name:
        ocr_ep = Endpoint(provider_model=ocr_name, api_key=ocr_key or None)

    return factory(
        mode="local",
        model=model_ep,
        ocr_model=ocr_ep,
    )


# ---------------------------------------------------------------------------
# Diagnostics (mirrors `clichefactory doctor`)
# ---------------------------------------------------------------------------

def _mask(s: str) -> str:
    if not s:
        return "(not set)"
    if len(s) <= 8:
        return "***"
    return s[:4] + "..." + s[-4:]


def run_doctor() -> str:
    """Run the same diagnostics as ``clichefactory doctor`` and return a text report."""
    lines: list[str] = []
    ok_count = warn_count = err_count = 0

    def ok(msg: str) -> None:
        nonlocal ok_count
        ok_count += 1
        lines.append(f"  [OK]   {msg}")

    def warn(msg: str) -> None:
        nonlocal warn_count
        warn_count += 1
        lines.append(f"  [WARN] {msg}")

    def err(msg: str) -> None:
        nonlocal err_count
        err_count += 1
        lines.append(f"  [ERR]  {msg}")

    lines.append("ClicheFactory Doctor")
    lines.append("")

    # --- Config ---
    lines.append("Configuration:")
    cfg_path = config_file_path()
    if cfg_path.is_file():
        cfg = load_config()
        ok(f"Config file: {cfg_path}")
        if cfg.default_mode == "service" and cfg.service.api_key:
            ok(f"Service API key configured ({_mask(cfg.service.api_key)})")
        elif cfg.default_mode == "service":
            warn("Service mode selected but no API key configured")
        if cfg.default_mode == "local" and cfg.local.model:
            ok(f"Local model: {cfg.local.model}")
        elif cfg.default_mode == "local":
            warn("Local mode selected but no model configured")
    else:
        warn('No config file found. Run "clichefactory configure" to set up.')

    lines.append("")

    # --- Python deps ---
    lines.append("Python dependencies:")

    for name, module in [("httpx", "httpx"), ("pydantic", "pydantic"), ("anyio", "anyio")]:
        try:
            __import__(module)
            ok(name)
        except ImportError:
            err(f"{name} (not installed)")

    local_deps = [
        ("pymupdf", "fitz"),
        ("docling", "docling"),
        ("Pillow", "PIL"),
        ("RapidOCR", "rapidocr"),
        ("pytesseract", "pytesseract"),
        ("openpyxl", "openpyxl"),
        ("python-docx", "docx"),
        ("pypdf", "pypdf"),
    ]
    for name, module in local_deps:
        try:
            __import__(module)
            ok(f"{name} (local)")
        except ImportError:
            warn(f"{name} not installed (needed for local mode)")

    lines.append("")

    # --- System binaries ---
    lines.append("System binaries:")
    for binary, purpose in [
        ("tesseract", "tesseract OCR engine"),
        ("pandoc", ".odt/.doc conversion"),
        ("soffice", "legacy .doc conversion"),
    ]:
        path = shutil.which(binary)
        if path:
            ok(f"{binary}: {path}")
        else:
            warn(f"{binary} not found on PATH (needed for {purpose})")

    lines.append("")

    # --- Summary ---
    total = ok_count + warn_count + err_count
    lines.append(f"Summary: {ok_count}/{total} checks passed, {warn_count} warnings, {err_count} errors")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Error formatting
# ---------------------------------------------------------------------------

def format_error(exc: Exception) -> str:
    """Turn an exception into an LLM-friendly error string."""
    if isinstance(exc, ClicheFactoryError):
        parts = [f"Error: {exc}"]
        hint = getattr(exc.info, "hint", None) if hasattr(exc, "info") else None
        if hint:
            parts.append(f"Hint: {hint}")
        return "\n".join(parts)

    if isinstance(exc, FileNotFoundError):
        return f"Error: {exc}"

    return f"Error ({type(exc).__name__}): {exc}"
