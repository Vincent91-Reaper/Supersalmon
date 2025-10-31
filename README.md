[![Build and Publish Docker Image](https://github.com/smokin-salmon/smoked-salmon/actions/workflows/docker-image.yml/badge.svg)](https://github.com/smokin-salmon/smoked-salmon/actions/workflows/docker-image.yml) [![Linting](https://github.com/smokin-salmon/smoked-salmon/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/smokin-salmon/smoked-salmon/actions/workflows/lint.yml)

# 🐟 Supersalmon

A simplified music uploading tool for RED (Redacted). Based on smoked-salmon but with streamlined functionality focused on core uploading features.

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

This fork has removed the following features from smoked-salmon:
- ❌ Folder renaming
- ❌ File renaming  
- ❌ Multi-tracker support (OPS, DIC) - Only RED is supported
- ❌ Request filling
- ❌ Downconversion and transcoding
- ❌ Spectral image generation and uploading
- ❌ MQA detection

## 📥 Installation  

Manual installation instructions can be found on the [Wiki](https://github.com/smokin-salmon/smoked-salmon/wiki/Installation).

### 🔹  Install Supersalmon 
These steps use [`uv`](https://github.com/astral-sh/uv) for installing the *Supersalmon* package. [`pipx`](https://github.com/pypa/pipx) also works.
Installing with pip is not recommended because uv (and pipx) manage python versions and isolate the installation from the system python installation.

#### Linux
1. Install system packages:
    ```bash
    sudo apt install sox flac ffmpeg mp3val curl unzip lame
    ```

2. Install uv:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. Install Supersalmon package from github:
	```bash
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
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

3. Install uv:
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

4. Install Supersalmon package from github:
	```powershell
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
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

3. Install uv:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

4. Install Supersalmon package from github:
	```bash
	uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
	```

### 🔹  Initial Setup
1. Run salmon for the first time and follow the instructions to create a default configuration:
	```
	salmon-user@salmon:~$ salmon
	Could not find configuration path at /home/salmon-user/.config/smoked-salmon/config.toml.
	Do you want smoked-salmon to create a default config file at /home/salmon-user/.config/smoked-salmon/config.default.toml? [y/N]:
	```

2. Copy the default config to `~/.config/smoked-salmon/config.toml`.
	```
	cp ~/.config/smoked-salmon/config.default.toml ~/.config/smoked-salmon/config.toml
	```

3. Edit the `config.toml` file with your preferred text editor to add your RED API key and session cookie. Make sure to configure only RED tracker settings (OPS and DIC are not supported).

4. Use the `checkconf` command to verify that the connection to RED is working:

	```
	salmon checkconf
	```

5. Use the `health` command to verify that all necesasary command line dependencies are installed:

	```
	salmon health
	```

### 🐳 Docker Installation

A Docker image is generated per release.  
**Disclaimer**: I am not actively using the docker image myself, feedback is appreciated regarding that guide.

1. Pull the latest image:

   ```bash
   docker pull ghcr.io/smokin-salmon/smoked-salmon:latest
   ```

2. Copy the content of the file [`config.toml`](https://github.com/smokin-salmon/smoked-salmon/blob/master/data/config.default.toml) to a location on your host server.  
   Edit the `config.toml` file with your preferred text editor to add your API keys, session cookies and update your preferences (see the [Configuration Wiki](https://github.com/smokin-salmon/smoked-salmon/wiki/Configuration)).

3. Configure rclone if needed. The Docker Compose configuration expects an rclone configuration file. You can get the path to your rclone config file by running `rclone config file` on your host system.

---

### 🔁 Recommended Docker Operation Order

1. **Check Configuration** -> **Run Migration** -> **Run the Web UI**  
   Run the container with the `checkconf` command to verify that the connection to the trackers is working:

   ```bash
   docker run --rm -it --network=host \
   -v /path/to/your/music:/app/.music \
   -v /path/to/your/config.toml/directory:/root/.config/smoked-salmon/ \
   -v /path/to/your/smoked.db/directory:/root/.local/share/smoked-salmon/ \
   -v /path/to/your/generated/dottorrents:/app/.torrents \
   -v /get/this/from/"rclone config file":/root/.config/rclone/rclone.conf  # Optional: only if using rclone features \
   ghcr.io/smokin-salmon/smoked-salmon:latest checkconf
   ```

   If the configuration is valid, use the `migrate` command to initialize or upgrade the database schema:
   Once migration is complete, you may launch container in persistent mode with `web` command.

2. **Connect to the Running Container**  
   To manually execute operations inside the container(`web` command required), connect via SSH and run:

   ```bash
   docker exec -it smoked-salmon /bin/sh
   ```

   Then, inside the container, you can run the commands like this:

   ```bash
   .venv/bin/salmon up "/path/to/your/music" -s WEB
   ```

---

### ⚠️ Notes

- **Permission Issues**  
  The container currently **able to handle permissions** properly.  
  If your torrent client is not run as root, or if new uploads are inaccessible, you may need to:
  - Manually adjust file/folder ownership (`chown`) or permissions (`chmod`)
  - Ensure the container and torrent client users are compatible
  - Optionally run containers with matching `--user` flags or add `umask` logic
     ```bash
    user: "1001:100"
    environment:
      - PUID=1001
      - PGID=100
     ```

- **.torrent Directory Mapping**  
  Depending on how you've set the `DOTTORRENTS_DIR` in your `config.toml`, you may need to map an additional directory for `.torrent` file output. Add:

  ```bash
  -v /your/host/torrent/output:/app/.torrents
  ```

- **rclone Configuration**  
  If you're using rclone features, make sure to map your rclone configuration file. This is optional and only needed if you plan to use rclone functionality. You can find your rclone config file location by running `rclone config file` on your host system:

  ```bash
  -v /path/to/your/rclone.conf:/root/.config/rclone/rclone.conf
  ```

---

### 📦 Portainer Stack Alternative

If using Portainer or Docker Compose, here's an example stack for persistent usage:

```yaml
version: "3"
services:
  smoked-salmon:
    image: ghcr.io/smokin-salmon/smoked-salmon:latest
    container_name: smoked-salmon
    network_mode: host
    restart: unless-stopped
    volumes:
      - /path/to/your/music:/app/.music
      - /path/to/your/config.toml/directory:/root/.config/smoked-salmon/
      - /path/to/your/smoked.db/directory:/root/.local/share/smoked-salmon/
      - /path/to/your/generated/dottorrents:/app/.torrents
      - /get/this/from/"rclone config file":/root/.config/rclone/rclone.conf  # Optional: only if using rclone features
    command: web
```

## 🚀 Usage

### 🎨 Terminal Colors
smoked-salmon uses distinct terminal colors for different types of messages:

* Default – General information
* Red – Errors or critical failures
* Green – Success messages
* Yellow – Information headers
* Cyan – Section headers
* Magenta – User prompts

### 🔧 CLI Mode
smoked-salmon runs in CLI mode, except for spectral visualization, which launches a web server. Quick start usage instructions can be found on the [Wiki Usage page](https://github.com/smokin-salmon/smoked-salmon/wiki#usage).

The examples below show how to run smoked-salmon directly. If you're using Docker, you'll need to adjust them accordingly, but the underlying principles remain the same.

On the first run, you will need to create the database:
```bash
salmon migrate
```

To see the available commands, just type:
```bash
salmon
```

To test the connection to the trackers, run:
```bash
salmon checkconf
```

To check the status of salmon's command line and config dependencies, run:
```bash
salmon health
```

To start an upload (with the WEB source):
```bash
salmon up /data/path/to/album -s WEB
```

You can get help directly from the CLI by appending --help to any command. This is especially useful for the up command which has a lot of possible options.

## 🔄 Updating

For **normal installs**:
```bash
uv tool update salmon
```

For **manual installs**:
```bash
cd Supersalmon
git pull
uv sync
```

## 📞 Support
For bug reports and feature requests, use GitHub Issues at https://github.com/Vincent91-Reaper/Supersalmon

## 📝 Changes from smoked-salmon

Supersalmon is a streamlined fork of smoked-salmon with the following modifications:

### What's Different:
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
* Based on [smoked-salmon](https://github.com/smokin-salmon/smoked-salmon) - originally created by [ligh7s](https://github.com/ligh7s/smoked-salmon)
* Further development & maintenance of smoked-salmon by elghoto, xmoforf, miandru, redusys and others
* Supersalmon modifications by Vincent91-Reaper to create a simplified RED-only uploader
