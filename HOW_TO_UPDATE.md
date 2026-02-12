# How to Install the New Update for BruceLee94

## TL;DR - Quick Update

If you already have BruceLee94 installed, just run:

```bash
uv tool upgrade brucelee94
```

Then verify it worked:

```bash
brucelee94 --version
```

That's it! 🎉

---

## Full Answer to "How Can I Install This New Update?"

### Step 1: Update BruceLee94

Open your terminal and run:

```bash
uv tool upgrade brucelee94
```

**Important Note:** It's `upgrade`, not `update`!

### Step 2: Verify the Update Worked

Check your version:

```bash
brucelee94 --version
```

You should see version **0.9.7.4** or higher.

### Step 3: Make Sure Everything Still Works

Test your RED connection:

```bash
brucelee94 checkconf
```

If this succeeds, you're all set! ✅

---

## What's New in This Update?

The latest update includes these important fixes:

### 1. 🎵 **DJ Mix Label Fix**
- **Problem:** DJ mix releases were showing descriptions like "26 July 2025 20 songs, 59 minutes" as the record label
- **Fixed:** Now shows proper labels or leaves it empty for DJ mixes

### 2. 🎤 **Artist Name Parsing Improvements**  
- **Problem:** Artists with `&` in their names (like "Artist A & Artist B") weren't being parsed correctly from metadata sources
- **Fixed:** All metadata sources (Deezer, Qobuz, Tidal, Beatport, iTunes) now correctly handle artist names with special characters

### 3. 🧹 **Cleaner Output**
- **Problem:** Debug messages were cluttering the console
- **Fixed:** Removed unnecessary debug output for a cleaner experience

---

## Troubleshooting

### "Command not found" after updating?

**Solution:** Restart your terminal, or run:

```bash
# Linux/macOS (bash)
source ~/.bashrc

# Linux/macOS (zsh)  
source ~/.zshrc

# Windows: Just close and reopen PowerShell
```

### Update didn't work?

**Solution:** Try forcing a reinstall:

```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
```

### Still having issues?

Check out the full guides:
- 📖 [UPDATE_GUIDE.md](UPDATE_GUIDE.md) - Comprehensive update instructions
- 📋 [CHANGELOG.md](CHANGELOG.md) - All changes and version history
- 📚 [README.md](README.md#-updating-brucelee94) - Full documentation

---

## Alternative Installation Methods

### If You Cloned the Repository Manually

```bash
cd /path/to/Supersalmon
git pull origin main
uv sync
```

### First Time Installing BruceLee94?

```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BruceLee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
```

---

## Need More Help?

- 🐛 **Report bugs:** https://github.com/Vincent91-Reaper/Supersalmon/issues
- 📖 **Full documentation:** [README.md](README.md)
- 📜 **Version history:** [CHANGELOG.md](CHANGELOG.md)
- 📚 **Detailed update guide:** [UPDATE_GUIDE.md](UPDATE_GUIDE.md)
