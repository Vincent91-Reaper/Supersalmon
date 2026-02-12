# Retagging Feature - Quick Reference

## Summary

**New Rule**: Only retag if main artist is **missing** from file tags.

If main artist is present (even with featured artists), **DON'T retag**.

---

## Visual Examples

### ✅ Scenario 1: Main Artist Present with Featured Artist
```
┌─────────────────────────────────────────┐
│ File Tag:  "Artist A, Artist B"         │
│ Metadata:  "Artist A"                   │
│                                         │
│ Decision:  ✓ NO RETAG                  │
│ Reason:    Main artist "Artist A" is    │
│            already present in file      │
└─────────────────────────────────────────┘
```

**Result**: File keeps both "Artist A" and "Artist B"

---

### ❌ Scenario 2: Main Artist Missing
```
┌─────────────────────────────────────────┐
│ File Tag:  "Artist B"                   │
│ Metadata:  "Artist A"                   │
│                                         │
│ Decision:  ✗ RETAG                     │
│ Reason:    Main artist "Artist A" is    │
│            missing from file            │
└─────────────────────────────────────────┘
```

**Result**: File is retagged to "Artist A"

---

### ✅ Scenario 3: Multiple Main Artists with Featured
```
┌─────────────────────────────────────────┐
│ File Tag:  "Artist A & Artist B         │
│             feat. Artist C"             │
│ Metadata:  "Artist A & Artist B"        │
│                                         │
│ Decision:  ✓ NO RETAG                  │
│ Reason:    Both main artists present    │
└─────────────────────────────────────────┘
```

**Result**: File keeps all three artists

---

### ❌ Scenario 4: One Main Artist Missing
```
┌─────────────────────────────────────────┐
│ File Tag:  "Artist A, Artist C"         │
│ Metadata:  "Artist A & Artist B"        │
│                                         │
│ Decision:  ✗ RETAG                     │
│ Reason:    "Artist B" is missing        │
└─────────────────────────────────────────┘
```

**Result**: File is retagged to "Artist A & Artist B"

---

### ✅ Scenario 5: Exact Match
```
┌─────────────────────────────────────────┐
│ File Tag:  "Artist A"                   │
│ Metadata:  "Artist A"                   │
│                                         │
│ Decision:  ✓ NO RETAG                  │
│ Reason:    Exact match                  │
└─────────────────────────────────────────┘
```

**Result**: No change needed

---

### ❌ Scenario 6: Empty/Missing Artist
```
┌─────────────────────────────────────────┐
│ File Tag:  "" (empty)                   │
│ Metadata:  "Artist A"                   │
│                                         │
│ Decision:  ✗ RETAG                     │
│ Reason:    No artist tagged             │
└─────────────────────────────────────────┘
```

**Result**: File is tagged with "Artist A"

---

## Key Points

1. **Main Artist Present** → Keep file as-is (preserves featured artists)
2. **Main Artist Missing** → Retag with correct main artist
3. **Case Insensitive** → "ARTIST A" matches "artist a"
4. **Separator Agnostic** → Handles `&`, `,`, `;`, `feat.`, `ft.`

---

## Benefits

✓ Preserves manually added featured artists  
✓ Reduces unnecessary file modifications  
✓ Only fixes genuinely incorrect tags  
✓ Maintains user customizations  

---

## See Also

- **RETAGGING_FEATURE.md** - Full documentation
- **test_retagging.py** - Test suite with all scenarios
