# Quick Answer: Detection Logic

## Your Question

> It has 2 conditions correct?
> 1. The artist name is the same as the record label
> 2. The artist name contains certain keywords such as "Records", "Productions", etc.

## Answer

**NO - Only condition #1 is used.**

**Condition #2 (keywords) is NOT checked.**

---

## Current Detection Logic

### ✅ What IS Checked

1. **Album artist matches label** (exact or 60%+ overlap)
2. **Album has 3+ track artists**
3. **No track artist matches album artist**

### ❌ What is NOT Checked

- Keywords like "Records", "Music", "Productions", "Entertainment"
- **No keyword pattern matching at all**

---

## Why?

**Keywords were tried but removed because:**
- Not reliable (many false positives/negatives)
- Doesn't work for all labels (XL, Warp, Ninja Tune, etc.)
- Label comparison is more accurate

**Current approach:**
- Compares album artist to actual record label from metadata
- Based on real data, not keyword guessing
- Works for all label names

---

## Examples

### Ed Banger Records
- Detected by: **Label comparison** ("Ed Banger Records" matches "Ed Banger Records")
- NOT by: Keywords (not checked)

### XL Recordings
- Detected by: **Label comparison** ("XL Recordings" matches "XL Recordings")
- NOT by: Keywords (not checked)

---

## Full Details

See **DETECTION_LOGIC_CLARIFICATION.md** for complete explanation with examples and code references.

---

## Summary

**Detection uses label comparison ONLY, not keywords.**

This is more reliable and accurate than keyword-based detection.
