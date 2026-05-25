# Debugging Record Label Detection Issue

## For the User: Start Here! 👇

The record label detection isn't working for your Ed Banger Records album from Qobuz. We've added debug output to find out why.

**Please read: [USER_INSTRUCTIONS.md](USER_INSTRUCTIONS.md)**

This document has simple steps for you to:
1. Update brucelee94
2. Run the upload
3. Look for debug messages
4. Share the output with us

That's it! The debug output will tell us exactly what's wrong, and we can fix it.

## Quick Summary

### What's Wrong

You uploaded an album from Qobuz, but:
- No detection message appeared
- No retagging happened
- Folder wasn't renamed
- Upload went through with "Ed Banger Records" instead of "Various Artists"

### What We Did

Added purple/magenta **[DEBUG]** messages to show:
- Album artist extraction
- Label extraction
- Track artists found
- Detection function call
- Detection result
- Why skipped (if applicable)

### What You Need to Do

1. **Update:**
   ```bash
   uv tool uninstall brucelee94
   uv tool install git+https://github.com/Vincent91-Reaper/Supersalmon@copilot/sub-pr-6-again
   ```

2. **Run the upload again** with the same album

3. **Look for [DEBUG] messages** in purple/magenta

4. **Share the complete console output** (all [DEBUG] messages are important!)

### What Happens Next

Based on your debug output, we'll:
1. Identify the exact issue
2. Implement a fix
3. You test again
4. It works!

## Documentation

- **[USER_INSTRUCTIONS.md](USER_INSTRUCTIONS.md)** - Simple steps (read this!)
- **[DEBUG_TESTING.md](DEBUG_TESTING.md)** - Detailed guide
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Original testing guide

## Questions?

Just share the complete console output (with [DEBUG] messages) and we'll take it from there!

Thank you for helping us fix this! 🙏
