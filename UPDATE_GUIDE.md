# 🔄 BruceLee94 Update Guide

This guide will help you update BruceLee94 to the latest version.

## Before You Update

1. **Check your current version:**
   ```bash
   brucelee94 --version
   ```

2. **Backup your configuration (optional but recommended):**
   ```bash
   # Linux/macOS
   cp ~/.config/brucelee94/config.toml ~/.config/brucelee94/config.toml.backup
   
   # Windows
   copy "%USERPROFILE%\.config\brucelee94\config.toml" "%USERPROFILE%\.config\brucelee94\config.toml.backup"
   ```

## How to Update

### Method 1: Standard Installation (Recommended)

If you installed BruceLee94 using `uv tool install`, updating is simple:

```bash
uv tool upgrade brucelee94
```

**Important:** Use `upgrade` not `update` with uv tools!

### Method 2: Manual/Development Installation

If you cloned the GitHub repository:

```bash
# Navigate to your Supersalmon directory
cd /path/to/Supersalmon

# Pull the latest changes
git pull origin main

# Update dependencies
uv sync

# If you want to use it as a tool, reinstall
uv tool install --force .
```

## After Updating

### 1. Verify the Update

Check that the new version is installed:

```bash
brucelee94 --version
```

You should see a version number higher than what you had before.

### 2. Test Your Configuration

Make sure your RED connection still works:

```bash
brucelee94 checkconf
```

### 3. Check System Dependencies

Verify all required tools are still installed:

```bash
brucelee94 health
```

### 4. Review New Features

Check the [CHANGELOG.md](CHANGELOG.md) to see what's new in this update.

## What's New in Recent Updates

### Latest Release (v0.9.7.4+)

**Bug Fixes:**
- ✅ **DJ Mix Label Fix** - DJ mixes no longer show descriptions like "26 July 2025 20 songs, 59 minutes" as the record label
- ✅ **Artist Name Parsing** - Artists with `&` in their names are now correctly parsed from all sources (Deezer, Qobuz, Tidal, Beatport, iTunes)
- ✅ **Clean Output** - Removed debug messages for better user experience

**What This Means for You:**
- Your DJ mix uploads will have cleaner metadata
- Artists like "Artist A & Artist B" will be properly recognized instead of being mangled
- Less clutter in the console output

## Troubleshooting

### Problem: "brucelee94: command not found" after update

**Solution:** Restart your terminal or reload your shell configuration:

```bash
# Linux/macOS (bash)
source ~/.bashrc

# Linux/macOS (zsh)
source ~/.zshrc

# Windows PowerShell
# Just close and reopen PowerShell
```

### Problem: Update command not working

**Solution:** Make sure you're using the right command:

```bash
# ✅ Correct
uv tool upgrade brucelee94

# ❌ Wrong
uv tool update brucelee94
```

### Problem: Getting errors after update

**Solution:** Try a clean reinstall:

```bash
# Uninstall
uv tool uninstall brucelee94

# Reinstall
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon

# Verify
brucelee94 --version
```

### Problem: New version not showing up

**Solution:** Force the update:

```bash
uv tool install --force git+https://github.com/Vincent91-Reaper/Supersalmon
```

### Problem: Configuration issues after update

**Solution:** Check for new configuration options:

```bash
# View the latest default config
cat ~/.config/brucelee94/config.default.toml

# Compare with your config
diff ~/.config/brucelee94/config.toml ~/.config/brucelee94/config.default.toml
```

## Getting Help

- **Documentation:** See [README.md](README.md) for full documentation
- **Issues:** Report bugs at https://github.com/Vincent91-Reaper/Supersalmon/issues
- **Changes:** View [CHANGELOG.md](CHANGELOG.md) for version history

## Stay Updated

To check for updates manually:

```bash
# Check current version
brucelee94 --version

# Check for available updates
uv tool upgrade --dry-run brucelee94
```

---

**Note:** BruceLee94 has an update notification feature built-in. When you run the tool, it will notify you if a newer version is available.
