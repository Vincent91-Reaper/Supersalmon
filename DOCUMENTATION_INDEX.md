# 📚 Documentation Index for BruceLee94

This repository contains comprehensive documentation to answer all your questions about installing, updating, and understanding the upload workflow.

## 🚀 Start Here

### Got Questions? Here's Where to Look:

| Question | Document to Read |
|----------|-----------------|
| How do I install the update? | [QUICK_ANSWER.md](QUICK_ANSWER.md) |
| When is label/catalog added? | [DEFERRED_METADATA_UPLOAD.md](DEFERRED_METADATA_UPLOAD.md) |
| Why upload label/catalog after? | [DEFERRED_METADATA_UPLOAD.md](DEFERRED_METADATA_UPLOAD.md) |
| Need detailed install guide? | [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md) |
| Want to understand the upload process? | [UPLOAD_WORKFLOW_EXPLAINED.md](UPLOAD_WORKFLOW_EXPLAINED.md) |
| Want a visual timeline? | [VISUAL_UPLOAD_TIMELINE.txt](VISUAL_UPLOAD_TIMELINE.txt) |
| General usage and features? | [README.md](README.md) |

## 📖 Available Documentation

### 1. [QUICK_ANSWER.md](QUICK_ANSWER.md)
**For:** Quick reference  
**Contains:**
- Installation command for this branch
- Quick FAQs
- TL;DR summary

**Best for:** Fast answers to common questions

---

### 2. [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md)
**For:** Installation and updates  
**Contains:**
- New installation instructions (Linux, Windows, macOS)
- Update commands for existing installations
- Branch-specific installation
- Troubleshooting guide
- Configuration setup steps

**Best for:** First-time users or updating existing installations

---

### 3. [DEFERRED_METADATA_UPLOAD.md](DEFERRED_METADATA_UPLOAD.md)
**For:** Understanding the new upload workflow  
**Contains:**
- Why label/catalog are added AFTER initial upload
- Benefits: 10-20% faster uploads
- How it works (two-phase process)
- Visual timeline comparison
- Technical details
- FAQ section

**Best for:** Understanding the deferred metadata upload feature

---

### 4. [UPLOAD_WORKFLOW_EXPLAINED.md](UPLOAD_WORKFLOW_EXPLAINED.md)
**For:** Understanding the complete upload process  
**Contains:**
- Detailed explanation of Phase 1 and Phase 2
- What gets uploaded when
- Code references
- Step-by-step workflow
- Common questions answered
- Verification instructions

**Best for:** Users who want to understand exactly what happens during upload

---

### 5. [VISUAL_UPLOAD_TIMELINE.txt](VISUAL_UPLOAD_TIMELINE.txt)
**For:** Visual learners  
**Contains:**
- ASCII art timeline
- Box diagrams showing what's included in each phase
- Key points summary
- Verification steps
- Common misconceptions corrected
- Code evidence

**Best for:** Quick visual understanding of the upload process

---

### 6. [README.md](README.md)
**For:** General information  
**Contains:**
- Features overview
- Basic installation (main branch)
- Usage instructions
- Common commands
- About BruceLee94

**Best for:** First-time visitors wanting general information

---

## 🎯 Quick Navigation by Topic

### Installation & Updates
1. Read: [QUICK_ANSWER.md](QUICK_ANSWER.md) for the command
2. Or read: [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md) for full guide

### Upload Process & Label/Catalog
1. Read: [QUICK_ANSWER.md](QUICK_ANSWER.md) for quick answer
2. Read: [VISUAL_UPLOAD_TIMELINE.txt](VISUAL_UPLOAD_TIMELINE.txt) for visual explanation
3. Read: [UPLOAD_WORKFLOW_EXPLAINED.md](UPLOAD_WORKFLOW_EXPLAINED.md) for complete details

### Folder Structure Optimization
1. Read: [FOLDER_STRUCTURE_OPTIMIZATION.md](FOLDER_STRUCTURE_OPTIMIZATION.md) for technical details
2. Read: [FOLDER_CHECK_FLOWCHART.txt](FOLDER_CHECK_FLOWCHART.txt) for decision tree
3. Read: [REQUIREMENTS_IMPLEMENTATION.md](REQUIREMENTS_IMPLEMENTATION.md) for implementation summary

### General Usage
1. Read: [README.md](README.md) for basic usage
2. Run: `brucelee94 --help` for command reference
3. Run: `brucelee94 up --help` for upload options

---

## ✅ Verified Answers to Common Questions

### Q: How do I install this version?
```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/remove-checking-for-dupe-feature-again
```

### Q: When are label and catalog number added?
**A:** They are included in the **initial torrent upload** (Phase 1), NOT added afterwards.

**Proof:** See code in `brucelee94/uploader/upload.py` lines 124-131

### Q: What IS added after upload?
**A:** Only these two things:
1. Cover image (uploaded to ptpimg, then added to group)
2. Album description with tracklist (new groups only)

### Q: How can I verify this myself?
**A:** 
1. Upload an album
2. Click the RED link immediately after "Successfully uploaded"
3. You'll see label and catalog are already there
4. Cover appears 3-5 seconds later

---

## 🔍 Finding Specific Information

### Code References
- **Upload data compilation:** `brucelee94/uploader/upload.py` lines 100-148
- **Upload process:** `brucelee94/uploader/__init__.py` lines 508-553
- **Folder structure check:** `brucelee94/tagger/folderstructure.py`

### Configuration
- **Config location:** `~/.config/brucelee94/config.toml`
- **Config guide:** See [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md) section "Configuration"

### Troubleshooting
- **Installation issues:** [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md) section "Troubleshooting"
- **Upload issues:** Check RED credentials with `brucelee94 checkconf`
- **System dependencies:** Check with `brucelee94 health`

---

## 📞 Support

If you can't find what you need in the documentation:
- Check the [Issues](https://github.com/Vincent91-Reaper/Supersalmon/issues) page
- Create a new issue with your question
- Include relevant logs and error messages

---

## 🎓 Learning Path

**For New Users:**
1. Read [README.md](README.md) to understand what BruceLee94 does
2. Follow [INSTALLATION_UPDATE_GUIDE.md](INSTALLATION_UPDATE_GUIDE.md) to install
3. Read [UPLOAD_WORKFLOW_EXPLAINED.md](UPLOAD_WORKFLOW_EXPLAINED.md) to understand the process
4. Try uploading a test album

**For Existing Users:**
1. Read [QUICK_ANSWER.md](QUICK_ANSWER.md) for update command
2. Review [VISUAL_UPLOAD_TIMELINE.txt](VISUAL_UPLOAD_TIMELINE.txt) to see what changed
3. Try the optimized version with a test upload

**For Developers:**
1. Read [FOLDER_STRUCTURE_OPTIMIZATION.md](FOLDER_STRUCTURE_OPTIMIZATION.md) for optimization details
2. Review code in `brucelee94/uploader/upload.py` and `brucelee94/uploader/__init__.py`
3. Check [REQUIREMENTS_IMPLEMENTATION.md](REQUIREMENTS_IMPLEMENTATION.md) for implementation notes

---

## 📝 Document Updates

All documentation is maintained in the repository and updated with code changes. Last updated: 2026-01-27

For the latest version, always refer to the documents in the repository rather than cached copies.
