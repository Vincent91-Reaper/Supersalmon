# Label Passthrough Feature - Complete ✅

## What This Does

When brucelee94 detects a Various Artists compilation on a record label (like Ed Banger Records), it now **passes the actual record label name to RED** instead of "Self-Released".

---

## Your Request

> "For the special case that album artist matches record label, brucelee94 needs to pass the original record label to its upload manager for torrent page on RED, instead of self-released. For example, 'Ed Banger Records - ED REC Vol.X (2013)'. 'Ed Banger Records' is the record label, not the album main artist. Brucelee94 needs to pass 'Ed Banger Records' to its upload manager, not 'Self-Released'"

✅ **DONE!**

---

## What Changed

### Before
```
Upload to RED:
  Artist: Various Artists ✓
  Album: ED REC Vol.X ✓
  Label: Self-Released ✗ WRONG!
```

### After
```
Upload to RED:
  Artist: Various Artists ✓
  Album: ED REC Vol.X ✓
  Label: Ed Banger Records ✓ CORRECT!
```

---

## What You'll See

When you upload Ed Banger Records (or similar):

```
Detected record label as album artist: Ed Banger Records
This appears to be a various artists compilation.
Retagging album artist to 'Various Artists'...

Renamed folder:
  From: Ed Banger Records - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]
  To:   Various Artists - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]

Label updated for upload: Ed Banger Records  ← NEW!

Album will be treated as Various Artists compilation.
```

---

## How to Test

**1. Update brucelee94:**
```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

**2. Upload Ed Banger Records:**
```
Album: Ed Banger Records - ED REC Vol.X
URL: https://www.qobuz.com/us-en/album/ed-rec-volx-mr-oizo-krazy-baldhead-breakbot-busy-p-mr-flash-justice-cassius-boston-bun/5060281613875
```

**3. Check console output:**
- Should see: "Label updated for upload: Ed Banger Records"

**4. Check RED torrent page:**
- Label should show: "Ed Banger Records"
- NOT "Self-Released"

---

## Summary

✅ **Problem:** Label albums uploaded with "Self-Released"
✅ **Solution:** Now uploads with actual label name
✅ **Result:** Correct label attribution on RED

**Your requirement is fully implemented and ready to use!**

---

## More Details

See **LABEL_PASSTHROUGH.md** for complete technical documentation.
