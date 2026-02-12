# 🔧 Installing the DJ Mix Fixes (Development Branch)

## ⚠️ Important Notice

The DJ Mix detection, artist attribution, and metadata formatting fixes are currently on the **development branch** and **NOT yet in the main release**.

This is why `uv tool upgrade brucelee94` doesn't work yet - it only installs from the main branch.

## 🚀 How to Install the Fixes RIGHT NOW

You have **two options** to get the latest fixes immediately:

---

### Option 1: Install Directly from GitHub Branch (Recommended)

This is the fastest way to get the fixes:

```bash
# Uninstall the old version first
uv tool uninstall brucelee94

# Install from the development branch with the fixes
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/fix-dj-mix-metadata-issues
```

**Verify it worked:**
```bash
brucelee94 --version
```

---

### Option 2: Clone and Install Locally

If Option 1 doesn't work, install from a local clone:

```bash
# Clone the repository
git clone https://github.com/Vincent91-Reaper/Supersalmon.git
cd Supersalmon

# Checkout the branch with the fixes
git checkout copilot/fix-dj-mix-metadata-issues

# Uninstall old version
uv tool uninstall brucelee94

# Install from local directory
uv tool install .
```

**Verify it worked:**
```bash
brucelee94 --version
```

---

## ✅ Verify You Have the Fixes

After installing, you can verify the fixes are working:

### 1. Check for DJ Mix Label Fix

When you upload a DJ mix, the label should no longer show descriptions like "26 July 2025 20 songs, 59 minutes"

### 2. Check for Artist Parsing Fix

Artists with `&` in their names should now be correctly parsed:
- ✅ "Artist A & Artist B" → correctly split into two artists
- ❌ Old behavior: "Artist A &amp; Artist B" → mangled artist name

### 3. Check for Clean Output

No more debug print statements cluttering your console

---

## 🔄 Updating Later

Once these fixes are merged to the main branch, you can switch back to regular updates:

```bash
# Uninstall the dev branch version
uv tool uninstall brucelee94

# Install the regular version from main
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon

# Then future updates work normally
uv tool upgrade brucelee94
```

---

## ❓ Why Doesn't `uv tool upgrade` Work?

**Short answer:** The fixes haven't been merged to the main branch yet.

**What `uv tool upgrade brucelee94` does:**
- Checks the main branch for updates
- Doesn't see your dev branch changes
- Nothing to upgrade!

**Once the fixes are merged:**
- They'll be on the main branch
- `uv tool upgrade brucelee94` will work
- Everyone gets the fixes automatically

---

## 🆘 Troubleshooting

### "Command not found" after installing

Restart your terminal or run:
```bash
# Linux/macOS (bash)
source ~/.bashrc

# Linux/macOS (zsh)
source ~/.zshrc

# Windows: Close and reopen PowerShell
```

### Still getting errors?

Make sure you completely uninstalled the old version:
```bash
uv tool uninstall brucelee94
uv cache clean
```

Then try Option 1 or Option 2 again.

### Need to go back to stable?

```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon
```

---

## 📋 What's Fixed in This Branch?

1. **🎵 DJ Mix Label Fix**
   - Problem: DJ mixes showed "26 July 2025 20 songs, 59 minutes" as record label
   - Fixed: Now properly empty or shows correct label

2. **🎤 Artist Name Parsing**
   - Problem: "Artist A &amp; Artist B" wasn't parsed correctly
   - Fixed: All metadata sources now handle HTML entities properly

3. **🧹 Clean Output**
   - Problem: Debug messages cluttering console
   - Fixed: Removed all debug print statements

---

## 📞 Need Help?

If you still can't install the fixes, please:
1. Copy the exact error message you're getting
2. Open an issue at: https://github.com/Vincent91-Reaper/Supersalmon/issues
3. Include which option you tried (Option 1 or Option 2)

---

**TL;DR:** Run this command:
```bash
uv tool uninstall brucelee94 && uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/fix-dj-mix-metadata-issues
```
