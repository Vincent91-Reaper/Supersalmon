# User Instructions: Debug Record Label Detection Issue

## Summary

The record label detection isn't working for your Ed Banger Records album from Qobuz. We've added debug output to find out why. Please follow these steps:

## Step 1: Update brucelee94

Run these commands:

```bash
uv tool uninstall brucelee94
uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
```

## Step 2: Run the Upload Again

Upload the same Ed Banger Records album:

```bash
bl94 up "/path/to/Ed Banger Records - ED REC Vol.X (2013) [WEB FLAC] [24-44.1]" -su "https://www.qobuz.com/us-en/album/ed-rec-volx-mr-oizo-krazy-baldhead-breakbot-busy-p-mr-flash-justice-cassius-boston-bun/5060281613875"
```

## Step 3: Look for Debug Messages

After "Retagging files...", you should see **purple/magenta [DEBUG] messages** like:

```
Retagging files...
Retagged X file(s) with correct artist tags from scraped metadata.

[DEBUG] Starting record label detection...
[DEBUG] Album artist from tags: Ed Banger Records
[DEBUG] Label from metadata: None
[DEBUG] Final extracted label: Ed Banger Records
[DEBUG] Track artists found: 10 - ['Mr Oizo', 'Breakbot', ...]
[DEBUG] Calling detection function...
[DEBUG] Detection result: True
```

## Step 4: Share the Output

Please share the **complete console output** including:
- All the [DEBUG] messages (they're important!)
- The full output from start to finish
- Any error messages

You can copy and paste it in your response, or take a screenshot.

## What the Debug Messages Will Tell Us

The debug messages will show us:
- ✓ Whether album artist is being extracted from tags
- ✓ Whether label is being extracted from metadata
- ✓ How many track artists are found
- ✓ Whether detection function gets called
- ✓ What the detection function returns
- ✓ Why it's skipped (if applicable)

Based on this, we can identify the exact issue and fix it!

## Common Scenarios

### If you see no [DEBUG] messages at all
- The detection code isn't being reached
- There might be an earlier error
- Share the complete output

### If you see "No album artist found in tags"
- Tags aren't set at that point in the code
- We need to check why

### If you see "Label from metadata: None" and "Final extracted label: None"
- Label isn't being extracted
- We need to fix the extraction logic

### If you see "Detection skipped - artists: 2"
- Not enough track artists found
- We need to fix track artist collection

### If you see "Detection result: False"
- Detection function says they don't match
- We need to check the comparison logic

## Next Steps

Once you share the debug output:
1. We'll identify the exact issue
2. We'll implement a fix
3. You can test again
4. It should work!

## Need Help?

If you have any questions or issues:
- Share the complete console output
- Let us know what you see
- We'll help diagnose from there

Thank you for helping us debug this! 🙏
