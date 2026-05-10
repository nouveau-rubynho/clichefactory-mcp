# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
(pre-1.0: minor for additive features, patch for bugfix / dependency
bump / docs).

## [0.1.4] — 2026-05-10

### Changed

- Bumped `clichefactory` floor to `>=0.5.1` to pick up the SDK's
  Docling-adapter page-marker fix. The SDK now emits canonical
  `<!-- cf:page N -->` markers from `to_markdown()`, so
  `PageChunker(pages_per_chunk=N)` actually splits multi-page
  documents on page boundaries instead of falling back to
  `TokenChunker` and producing a single chunk for any multi-page
  document under the token cap. The MCP server's local-mode
  `extract` and `to_markdown` tools route through this code path,
  so fresh installs of the MCP server now pick up the fix
  transparently. No public MCP tool surface changed.

## [0.1.3] — 2026-05-10

### Changed

- Bumped `clichefactory` floor to `>=0.5.0` to track the SDK's latest
  minor. No public MCP tool surface changed — this is purely a
  dependency-floor bump. See the SDK's CHANGELOG for SDK-side details.

## [0.1.2] — 2026-05-10

### Changed

- Bumped `clichefactory` floor to `>=0.4.2` to pick up the SDK's new
  default service base URL. Service-mode MCP installs now talk to
  `https://api.clichefactory.com` out of the box — `CLICHEFACTORY_API_KEY`
  is the only env var most users need. `CLICHEFACTORY_API_URL` remains
  available as the override for local development and
  self-hosted instances.

### Documentation

- Dropped the redundant `"CLICHEFACTORY_API_URL": "https://api.clichefactory.com"`
  from the Cursor and OpenClaw service-mode example snippets — it was
  always equivalent to the SDK default since the floor is now `>=0.4.2`.
- Tightened the env-vars table description for `CLICHEFACTORY_API_URL`
  to make it explicit that it overrides the default rather than enables
  it.

## [0.1.1] — 2026-05-09

### Changed

- Bumped `clichefactory` floor to `>=0.4.0` to pick up the SDK's
  fast-mode MIME degradation. `mode="fast"` extract calls on EML,
  DOCX, XLSX, CSV, ODT and DOC inputs now succeed transparently
  instead of raising the vendor's `400 INVALID_ARGUMENT: Unsupported
  MIME type` (the SDK pre-flights `AIClient.supports_bytes(mime)`
  and parses unsupported types to markdown locally before a single
  `extract(text, schema)` call). PDFs and common image MIMEs keep
  the multimodal raw-bytes path unchanged. No public MCP tool
  surface changed.

## [0.1.0] — 2026-05-05

### Added

- Initial public release. MCP server exposing `extract`,
  `to_markdown` and `doctor` tools backed by the `clichefactory`
  SDK in either local (BYOK) or service (ClicheFactory cloud) mode.
