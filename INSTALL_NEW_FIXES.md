# Installing the Latest Fixes

This guide explains how to install the latest BruceLee94 fixes from the `copilot/sub-pr-6-again` branch.

## What's Fixed in This Version

This branch includes important bug fixes:

1. **DJ Mix Record Label Fix** - Record label now correctly displays as empty for DJ Mix uploads instead of showing incorrect metadata (e.g., "26 July 2025 20 songs, 59 minutes")

2. **Universal Artist Splitting** - Artist separation with "&" and "," now works consistently across all sources (Deezer, Qobuz, Tidal, Beatport, Apple Music)

3. **Clean Output** - All debug messages have been removed for cleaner console output

## Installation Instructions

### For New Users

If you haven't installed BruceLee94 yet, follow the main [README.md](README.md) instructions first, but use this branch:

**Linux/macOS:**
```bash
# Install system dependencies first
sudo apt install sox flac ffmpeg mp3val curl unzip lame  # Linux
# OR
brew install sox flac ffmpeg mp3val curl unzip lame      # macOS

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BruceLee94 with the latest fixes
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

**Windows:**
```powershell
# Install system dependencies
winget install -e Gyan.FFmpeg ChrisBagwell.SoX Xiph.FLAC LAME.LAME ring0.MP3val.WF

# Fix sox Unicode filename issue
$soxDir = $((Get-Command sox).Source | Split-Path)
$zipPath = Join-Path -Path $soxDir -ChildPath "sox_windows_fix.zip"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/DevYukine/red_oxide/master/.github/dependency-fixes/sox_windows_fix.zip" -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $soxDir -Force
regedit "$soxDir\PreferExternalManifest.reg"
Remove-Item $zipPath

# Install uv package manager
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install BruceLee94 with the latest fixes
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

### For Existing Users (Updating)

If you already have BruceLee94 installed:

**All Platforms:**
```bash
# Uninstall current version
uv tool uninstall brucelee94

# Install version with latest fixes
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

### Verify Installation

After installation or update, verify it's working:
```bash
brucelee94 --help
brucelee94 checkconf  # Test RED connection
brucelee94 health     # Check system dependencies
```

## Initial Configuration (New Users Only)

If this is your first installation:

1. Run BruceLee94 to create default config:
   ```bash
   brucelee94
   ```

2. Copy the default config:
   ```bash
   # Linux/macOS
   cp ~/.config/brucelee94/config.default.toml ~/.config/brucelee94/config.toml
   
   # Windows
   copy %APPDATA%\brucelee94\config.default.toml %APPDATA%\brucelee94\config.toml
   ```

3. Edit the configuration file:
   ```bash
   # Linux/macOS
   nano ~/.config/brucelee94/config.toml
   
   # Windows
   notepad %APPDATA%\brucelee94\config.toml
   ```
   
   **Important settings to configure:**
   - Add your RED API key under `[tracker.red]`
   - Add your RED session cookie under `[tracker.red]`
   - Configure your download directory under `[directory]`

4. Initialize the database:
   ```bash
   brucelee94 migrate
   ```

5. Verify configuration:
   ```bash
   brucelee94 checkconf
   brucelee94 health
   ```

## Testing the Fixes

To verify the fixes are working:

### DJ Mix Label Fix
Upload a DJ Mix album from Apple Music/iTunes and verify that the record label field is empty instead of showing date/song count information.

### Artist Splitting Fix
Upload an album where artists are separated by commas or ampersands (e.g., "Artist A, Artist B & Artist C") from any source (Deezer, Qobuz, Tidal, Beatport) and verify they are properly split into individual artist tags.

### Clean Output
Run any upload and verify that no "DEBUG:" messages appear in the console output.

## Troubleshooting

**Issue: Command not found after installation**
```bash
# Ensure uv tools directory is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Issue: Installation fails**
```bash
# Update uv first
uv self update

# Retry installation
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

**Issue: Old version still running**
```bash
# Clear cached installations
uv tool uninstall brucelee94
rm -rf ~/.local/share/uv/tools/brucelee94  # Linux/macOS
# OR
rmdir /s %LOCALAPPDATA%\uv\tools\brucelee94  # Windows

# Reinstall
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

**Issue: Want to switch back to main branch**
```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
```

## Getting Help

- Check the main [README.md](README.md) for general usage instructions
- Review [UPLOAD_WORKFLOW_EXPLAINED.md](UPLOAD_WORKFLOW_EXPLAINED.md) for upload process details
- Report issues at: https://github.com/Vincent91-Reaper/Supersalmon/issues
