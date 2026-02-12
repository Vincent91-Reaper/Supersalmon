# Changelog

All notable changes to BruceLee94 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **DJ Mix Label Parsing**: Fixed issue where DJ mix releases showed release descriptions (e.g., "26 July 2025 20 songs, 59 minutes") as record labels instead of leaving it empty. The `parse_copyright()` function now detects and rejects non-copyright strings containing "X songs, Y minutes" pattern.
- **Artist HTML Entity Handling**: Fixed artist name parsing across all metadata sources (Deezer, Qobuz, Tidal, Beatport, iTunes) to properly handle HTML entities like `&amp;`. Artists are now correctly split when their names contain `&` characters.
  - Before: "Artist A &amp; Artist B" → ["Artist A &amp", "Artist B"] ❌
  - After: "Artist A &amp; Artist B" → ["Artist A", "Artist B"] ✅
- **Debug Output**: Removed debug print statements (`print(i)` in search/deezer.py and `pprint(metadata)` in tagger/__init__.py) for cleaner output.

### Changed
- Optimized unescape operations in artist parsing to avoid redundant HTML entity decoding.
- Improved metadata scraping output format using structured `click.echo()` instead of `pprint()`.

## [0.9.7.4] - 2024-02-12

### Changed
- Limited metadata sources to only Qobuz, Deezer, iTunes, and Beatport for improved reliability.

## [0.9.7.3] - Previous Release

### Added
- Initial release of BruceLee94 as a simplified fork of smoked-salmon
- RED-only uploader with separate configuration directory
- Core features: metadata retrieval, file tagging, duplicate detection, upconvert checking

### Removed
- Folder and file renaming features
- Multi-tracker support (OPS, DIC)
- Request filling
- Downconversion and transcoding
- Spectral image generation and uploading
- MQA detection

---

## Upgrade Instructions

To get the latest updates:

**For standard installations:**
```bash
uv tool upgrade brucelee94
```

**For manual/development installations:**
```bash
cd Supersalmon
git pull origin main
uv sync
```

See the [README.md](README.md#-updating-brucelee94) for detailed update instructions.
