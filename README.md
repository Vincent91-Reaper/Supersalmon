# 🥋 BruceLee94

A simplified music uploading tool for RED (Redacted). Completely separate from smoked-salmon with its own configuration and data directories.

## 🚀 Quick Start

### New Installation
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BruceLee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
```

### Updating to Latest Version
```bash
# Update BruceLee94 to the latest version
uv tool upgrade brucelee94

# Verify the update
brucelee94 --version
```

See [detailed installation instructions](#-installation) and [update guide](#-updating-brucelee94) below.

## 🌟 Features  

- **RED Upload** – Upload music to RED (Redacted) tracker
- **Upconvert Detection** – Checks 24-bit flac files for potential upconverts
- **Duplicate Upload Detection** – Prevents redundant uploads  
- **Metadata Retrieval** – Fetches metadata from:
  - Bandcamp, Beatport, Deezer, Discogs, iTunes, JunoDownload, MusicBrainz, Qobuz, Tidal
- **File Management** –  
  - Retags files with updated metadata
  - Checks file integrity and sanitizes if needed
  - Original folder and file names are preserved
- **Description generation** – Edition description generation (tracklist, sources, available streaming platforms, encoding details...)
- **Update Notifications** – Informs users when a new version is available

## ⚠️ Removed Features

These features have been removed from the original smoked-salmon:
- ❌ Folder renaming
- ❌ File renaming  
- ❌ Multi-tracker support (OPS, DIC) - Only RED is supported
- ❌ Request filling
- ❌ Downconversion and transcoding
- ❌ Spectral image generation and uploading
- ❌ MQA detection

## 📥 Installation  

BruceLee94 requires Python 3.11 or later. Follow the steps below for your operating system.

### 🔹 Install BruceLee94

These steps use [`uv`](https://github.com/astral-sh/uv) for installing the *BruceLee94* package. [`pipx`](https://github.com/pypa/pipx) also works.
Installing with pip is not recommended because uv (and pipx) manage python versions and isolate the installation from the system python installation.

#### Linux
1. Install system packages (required for audio processing):
    ```bash
    sudo apt install sox flac ffmpeg mp3val curl unzip lame
    ```

2. Install uv (Python package manager):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. Install BruceLee94 package from GitHub:
	```bash
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
	```

4. Verify installation:
    ```bash
    brucelee94 --help
    ```

#### Windows
1. Install required system packages using winget:
    ```powershell
    winget install -e Gyan.FFmpeg ChrisBagwell.SoX Xiph.FLAC LAME.LAME ring0.MP3val.WF
    ```

2. Fix sox Unicode filename handling issue on Windows:
    ```powershell
    $soxDir = $((Get-Command sox).Source | Split-Path)
    $zipPath = Join-Path -Path $soxDir -ChildPath "sox_windows_fix.zip"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/DevYukine/red_oxide/master/.github/dependency-fixes/sox_windows_fix.zip" -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $soxDir -Force
    regedit "$soxDir\PreferExternalManifest.reg"
    Remove-Item $zipPath
    ```

3. Install uv (Python package manager):
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

4. Install BruceLee94 package from GitHub:
	```powershell
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
	```

5. Verify installation:
    ```powershell
    brucelee94 --help
    ```

#### macOS
1. Install Homebrew (if you haven't already):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. Install system packages using Homebrew:
    ```bash
    brew install sox flac ffmpeg mp3val curl unzip lame
    ```

3. Install uv (Python package manager):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

4. Install BruceLee94 package from GitHub:
	```bash
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
	```

5. Verify installation:
    ```bash
    brucelee94 --help
    ```

### 🔹 Initial Setup and Configuration

1. Run BruceLee94 for the first time to create a default configuration:
	```bash
	brucelee94
	```
	
	You'll see:
	```
	Could not find configuration path at /home/user/.config/brucelee94/config.toml.
	Do you want BruceLee94 to create a default config file at /home/user/.config/brucelee94/config.default.toml? [y/N]:
	```
	
	Type `y` and press Enter.

2. Copy the default config to the active configuration file:
	```bash
	cp ~/.config/brucelee94/config.default.toml ~/.config/brucelee94/config.toml
	```

3. Edit the configuration file with your preferred text editor:
	```bash
	# Linux/macOS
	nano ~/.config/brucelee94/config.toml
	
	# Or use vim, emacs, etc.
	vim ~/.config/brucelee94/config.toml
	```
	
	**Important settings to configure:**
	- Add your RED API key under `[tracker.red]`
	- Add your RED session cookie under `[tracker.red]`
	- Configure your download directory under `[directory]`
	- Adjust other preferences as needed

4. Verify your RED connection is working:
	```bash
	brucelee94 checkconf
	```
	
	This should successfully connect to RED and confirm your credentials are valid.

5. Check that all command-line dependencies are installed:
	```bash
	brucelee94 health
	```
	
	This will verify that sox, flac, ffmpeg, and other required tools are available.

## 🚀 Usage

## 🚀 Usage

### 🎨 Terminal Colors
BruceLee94 uses distinct terminal colors for different types of messages:

* Default – General information
* Red – Errors or critical failures
* Green – Success messages
* Yellow – Information headers
* Cyan – Section headers
* Magenta – User prompts

### 🔧 Basic Commands

#### Initialize the database
On the first run, you need to create the database:
```bash
brucelee94 migrate
```

#### View available commands
To see all available commands:
```bash
brucelee94 --help
```

#### Test RED connection
To verify your RED credentials are working:
```bash
brucelee94 checkconf
```

#### Check system dependencies
To verify all required command-line tools are installed:
```bash
brucelee94 health
```

#### Upload an album
To upload an album to RED (specify the source with `-s`):
```bash
brucelee94 up /path/to/album/folder -s WEB
```

Common source options:
- `WEB` - Web download
- `CD` - CD rip
- `Vinyl` - Vinyl rip
- `SACD` - SACD rip
- `Blu-ray` - Blu-ray rip

#### Get help for a specific command
To see all options for a command (e.g., the upload command):
```bash
brucelee94 up --help
```

### 📋 Common Upload Workflow

1. **Prepare your music folder** - Ensure your album is in a single folder with FLAC files
2. **Run the upload command**:
   ```bash
   brucelee94 up /path/to/album -s WEB
   ```
3. **Review metadata** - The tool will fetch metadata and ask you to review it
4. **Confirm upload** - After reviewing, confirm to upload to RED
5. **Done!** - The torrent will be created and uploaded

### 🎯 Additional Options

- `--group-id <ID>` or `-g <ID>` - Upload to an existing group
- `--compress` or `-c` - Recompress FLACs before uploading
- `--scene` - Mark as a scene release
- `--source-url <URL>` or `-su <URL>` - Add a source URL to the description
- `-yyy` - Automatically accept all prompts (use with caution)

## 🔄 Updating BruceLee94

### 📦 For Standard Installations (Installed with `uv tool install`)

If you installed BruceLee94 using the recommended `uv tool install` method, updating is simple:

```bash
uv tool upgrade brucelee94
```

**Note:** Use `upgrade` (not `update`) with uv tools.

After upgrading, verify the new version:
```bash
brucelee94 --version
```

### 🛠️ For Development/Manual Installations

If you cloned the repository and installed manually:

1. Navigate to your Supersalmon directory:
   ```bash
   cd /path/to/Supersalmon
   ```

2. Pull the latest changes:
   ```bash
   git pull origin main
   ```

3. Sync dependencies:
   ```bash
   uv sync
   ```

4. Verify the installation:
   ```bash
   python run.py --version
   ```

### ✅ Verifying the Update

After updating, you can verify everything is working:

1. Check the version:
   ```bash
   brucelee94 --version
   ```

2. Test your configuration:
   ```bash
   brucelee94 checkconf
   ```

3. Check system dependencies:
   ```bash
   brucelee94 health
   ```

### 🆕 What's New in Recent Updates

**Latest Updates (v0.9.7.4+):**
- ✅ **Fixed DJ Mix Label Parsing** - DJ mix releases no longer show release descriptions (e.g., "26 July 2025 20 songs, 59 minutes") as record labels
- ✅ **Universal Artist HTML Entity Handling** - Artists with HTML entities like `&amp;` in their names are now parsed correctly across all metadata sources (Deezer, Qobuz, Tidal, Beatport, iTunes)
- ✅ **Cleaner Debug Output** - Removed debug print statements for a cleaner user experience

### 🔧 Troubleshooting Updates

**Issue: "Command not found" after update**
- Solution: Restart your terminal or run `source ~/.bashrc` (Linux/macOS) or restart PowerShell (Windows)

**Issue: Update doesn't seem to apply**
- Solution: Try uninstalling and reinstalling:
  ```bash
  uv tool uninstall brucelee94
  uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
  ```

**Issue: Configuration errors after update**
- Solution: Check if new configuration options were added. Compare your `config.toml` with `config.default.toml`:
  ```bash
  # View the default config
  cat ~/.config/brucelee94/config.default.toml
  ```

## 📞 Support
For bug reports and feature requests, use GitHub Issues at https://github.com/Vincent91-Reaper/Supersalmon

## 📝 About BruceLee94

BruceLee94 is a streamlined fork of the original smoked-salmon tool with the following modifications:

**Important:** BruceLee94 uses its own separate configuration directory (`~/.config/brucelee94/`) and will not interfere with any existing smoked-salmon installation.

### What's Different:
- **Renamed Tool**: Changed from "salmon" to "brucelee94" command
- **Simplified Upload Process**: File and folder names are preserved in their original state - no automatic renaming
- **RED-Only**: Focused exclusively on uploading to RED (Redacted), removing complexity of multi-tracker support
- **Streamlined Workflow**: Removed spectral generation, MQA detection, request filling, and downconversion features
- **Core Functionality**: Retains essential features like metadata retrieval, file tagging, duplicate detection, and upconvert checking

### Removed Features:
1. Folder renaming (original folder names are kept)
2. File renaming (original file names are kept)
3. Multi-tracker support (OPS and DIC removed)
4. Request filling
5. Downconversion and transcoding
6. Spectral image generation and uploading
7. MQA detection

## 🎩 Credits
* Based on the original [smoked-salmon](https://github.com/smokin-salmon/smoked-salmon) - created by [ligh7s](https://github.com/ligh7s/smoked-salmon)
* Further development & maintenance of the original smoked-salmon by elghoto, xmoforf, miandru, redusys and others
* BruceLee94 modifications by Vincent91-Reaper - renamed from Supersalmon and configured as a simplified RED-only uploader with separate config directories
