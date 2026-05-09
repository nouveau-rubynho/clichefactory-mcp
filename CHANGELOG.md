# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
(pre-1.0: minor for additive features, patch for bugfix / dependency
bump / docs).

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
