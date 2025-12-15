# Update Guide: Fix Album Folder Format

This guide will help you update your existing Apple Music downloader to remove the "B" and "kHz" suffixes from folder names.

## What This Fix Does

**Before:** `[16B-44.1kHz]` or `[24B-48.0kHz]`  
**After:** `[16-44.1]` or `[24-48]`

## Option 1: Replace Your Installation (Recommended)

### Step 1: Backup Your Configuration
```bash
# Backup your config.yaml
cp ~/apple-music-downloader/config.yaml ~/config.yaml.backup
```

### Step 2: Remove Old Installation
```bash
# Navigate to parent directory
cd ~

# Remove old downloader (or rename it)
mv apple-music-downloader apple-music-downloader-old
```

### Step 3: Clone Fixed Version
```bash
# Clone this fixed repository
git clone https://github.com/Vincent91-Reaper/Supersalmon.git apple-music-downloader

# Navigate to the new directory
cd apple-music-downloader
```

### Step 4: Restore Your Configuration
```bash
# Copy your backup config back
cp ~/config.yaml.backup config.yaml
```

### Step 5: Build
```bash
# Build the application
go build -o apple-music-dl main.go
```

### Step 6: Verify
```bash
# Test the build
./apple-music-dl --help
```

Done! Your downloader is now updated.

---

## Option 2: Manual Patch (Quick Fix)

If you want to keep your existing installation, just patch the one file:

### Step 1: Open main.go
```bash
# Navigate to your downloader
cd ~/apple-music-downloader

# Open main.go in your editor
nano main.go
# or
vim main.go
# or
code main.go
```

### Step 2: Find and Replace

Search for this line (around line 2417):
```go
Quality = fmt.Sprintf("%sB-%.1fkHz", split[length-1], KHZ)
```

Replace it with these lines:
```go
// Format without decimal if it's a whole number
if KHZ == float64(int(KHZ)) {
    Quality = fmt.Sprintf("%s-%.0f", split[length-1], KHZ)
} else {
    Quality = fmt.Sprintf("%s-%.1f", split[length-1], KHZ)
}
```

### Step 3: Save and Rebuild
```bash
# Save the file (Ctrl+X then Y in nano, :wq in vim)

# Rebuild
go build -o apple-music-dl main.go
```

### Step 4: Verify
```bash
# Test the build
./apple-music-dl --help
```

Done! Your fix is applied.

---

## Option 3: Download Pre-Built Binary (Coming Soon)

Check the [Releases](https://github.com/Vincent91-Reaper/Supersalmon/releases) page for pre-built binaries.

---

## Verification

After updating, when you download an album, you should see folder names like:
- `Artist Name - Album Name (2024) [WEB FLAC] [24-48]` (not `[24B-48.0kHz]`)
- `Artist Name - Album Name (2024) [WEB FLAC] [16-44.1]` (not `[16B-44.1kHz]`)

---

## Troubleshooting

### Build fails with missing dependencies
```bash
# Make sure you have Go installed
go version

# Download dependencies
go mod download
```

### Permission denied when running
```bash
# Make the binary executable
chmod +x apple-music-dl
```

### Can't find your config.yaml location
```bash
# Search for it
find ~ -name "config.yaml" -path "*/apple-music-downloader/*" 2>/dev/null
```

---

## Notes

- **Wrapper:** No changes needed to the wrapper - it doesn't handle Quality formatting
- **Config:** Your `config.yaml` settings remain the same
- **Backwards Compatible:** This change only affects how folder names are displayed, not functionality

---

## Need Help?

Open an issue at: https://github.com/Vincent91-Reaper/Supersalmon/issues
