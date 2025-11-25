# 🚀 Quick Reference Guide

## **3 Critical Functions - FIXED!**

---

### **1. GetSpaces** ✅

**What it does:** Formats chart labels with layer name, arrow, and indentation

**Format:** `"LayerName - Description ↵    "`

**Example:**
```python
# Input:
{
    'SourceLayer': 'Road',
    'Name': 'Main Street Reconstruction',
    'RelationId': 2
}

# Output:
"Road - Main Street Reconstr  ↵         "
#  ^30 chars max               ^arrow    ^8 spaces (RelId=2 × 4)
```

**Key Points:**
- ✅ Combines `SourceLayer + " - " + Name`
- ✅ Truncates to 30 characters
- ✅ Adds arrow symbol ` ↵ ` (U+21B5)
- ✅ Adds 4 spaces per RelationId level

---

### **2. CheckIssuesForDepending** ✅

**What it does:** Checks if children finish AFTER their parents (❌ BAD for Depending)

**Algorithm:**
1. Iterate **BACKWARDS** (last → first)
2. Find parent (RelationId = current - 1)
3. Check: `child.endDate > parent.endDate`? → **ISSUE!**
4. Mark BOTH child AND parent as having issues
5. Issues propagate **UP** the tree

**Example:**
```
Road (2023-2025)          [RelId=1]
  └─ Water (2024-2026)    [RelId=2]  ← 2026 > 2025 → ISSUE!
      └─ Electric (2027)  [RelId=3]  ← 2027 > 2026 → ISSUE!

Result:
- Electric: hasIssue = true (ends after Water)
- Water: hasIssue = true (ends after Road + child has issue)
- Road: hasIssue = true (child has issue)

All marked RED! 🔴
```

**Why Backwards?**
- To catch issues at the leaf nodes first
- Then propagate UP to root

---

### **3. CheckIssuesForSupporting** ✅

**What it does:** Checks if children finish BEFORE their parents (❌ BAD for Supporting)

**Algorithm:**
1. Iterate **FORWARD** (first → last)
2. Find child (RelationId = current + 1)
3. Check: `child.endDate < parent.endDate`? → **ISSUE!**
4. Mark BOTH parent AND child as having issues
5. Issues propagate **DOWN** the tree

**Example:**
```
Road (2023-2027)          [RelId=1]
  └─ Water (2024-2025)    [RelId=2]  ← 2025 < 2027 → ISSUE!
      └─ Electric (2026)  [RelId=3]  ← 2026 < 2027 → ISSUE!

Result:
- Road: hasIssue = true (Water ends before Road)
- Water: hasIssue = true (Electric ends before Road + parent has issue)
- Electric: hasIssue = true (ends before Water)

All marked RED! 🔴
```

**Why Forward?**
- To catch issues at the root first
- Then propagate DOWN to leaves

---

## **Quick Logic Reference**

### **Depending (Parent → Child)**
| Condition | Status | Color | Logic |
|-----------|--------|-------|-------|
| Child ends AFTER parent | ❌ Issue | 🔴 Red | `child.end > parent.end` |
| Child ends BEFORE/ON parent | ✅ OK | 🟢 Green | `child.end <= parent.end` |

**Why?** Dependencies should finish before or with their dependents.

---

### **Supporting (Child → Parent)**
| Condition | Status | Color | Logic |
|-----------|--------|-------|-------|
| Child ends BEFORE parent | ❌ Issue | 🔴 Red | `child.end < parent.end` |
| Child ends AFTER/ON parent | ✅ OK | 🟢 Green | `child.end >= parent.end` |

**Why?** Supporting infrastructure should finish after or with what they support.

---

## **Chart Label Examples**

### **RelationId Hierarchy:**

```
Road - Main St Project  ↵          [RelId=0, 0 spaces]
Road - Intersection Upgrade  ↵     [RelId=1, 4 spaces]
Water - Main Line Replace  ↵         [RelId=2, 8 spaces]
Electric - Grid Moderniza  ↵             [RelId=3, 12 spaces]
Fiber - Cable Installation  ↵                 [RelId=4, 16 spaces]
```

**Formula:** `spaces = RelationId × 4`

---

## **Testing Checklist**

Run: `python infratagging_complete.py`

Verify:
- [ ] Chart labels have format: `"Layer - Name ↵    "`
- [ ] Labels are truncated to 30 chars
- [ ] Arrow symbol (↵) is present
- [ ] Indentation: 4 spaces per RelationId
- [ ] Issues are detected correctly:
  - [ ] Depending: child ending after parent = RED
  - [ ] Supporting: child ending before parent = RED
- [ ] Issues propagate correctly:
  - [ ] Depending: issues go UP
  - [ ] Supporting: issues go DOWN
- [ ] Both parent and child marked when issue found
- [ ] ChartHeight varies (not always 100)
- [ ] ChartJSON contains full Chart.js config

---

## **Common Issues**

### ❌ **Labels look like:** `Road Project`
**Problem:** Old `GetSpaces` implementation  
**Solution:** Use updated version with layer name + arrow

---

### ❌ **No issues detected even when dates wrong**
**Problem:** Old `CheckIssues` functions just checking any()  
**Solution:** Use updated versions with parent/child comparison

---

### ❌ **Issues not propagating**
**Problem:** Not marking both parent and child  
**Solution:** Ensure `schedule_data[i]` and `schedule_data[parent_index]` both set to True

---

### ❌ **Wrong iteration direction**
**Problem:** Depending iterates forward, Supporting iterates backward  
**Solution:**
- Depending: `range(len() - 1, 0, -1)` ← Backwards
- Supporting: `range(len() - 1)` ← Forward

---

## **Database Output**

### **INFRATAGGING_SUMMARY_CACHE Table**

| Column | Example Value |
|--------|---------------|
| LAYER_ID | 7373 |
| FEATURE_ID | `2022_KL_3` |
| CHARTJSON | `{"type":"horizontalBar","data":{...}}` |
| CHARTHEIGHT | 250 (varies!) |

**ChartJSON Sample:**
```json
{
  "type": "horizontalBar",
  "data": {
    "labels": [
      "Road - Main St Project  ↵ ",
      "Water - Line Replacement  ↵     "
    ],
    "datasets": [{
      "backgroundColor": ["rgba(255,0,0,0.5)", "rgba(0,128,0,0.5)"],
      "data": [["2023", "2025", "Road"], ["2024", "2026", "Water"]]
    }]
  }
}
```

---

## **Summary**

| Function | Purpose | Direction | Issue Logic |
|----------|---------|-----------|-------------|
| **GetSpaces** | Format labels | N/A | N/A |
| **CheckIssuesForDepending** | Detect issues | ⬅️ Backward | child.end > parent.end |
| **CheckIssuesForSupporting** | Detect issues | ➡️ Forward | child.end < parent.end |

---

🎉 **All functions now match the .NET implementation EXACTLY!**

Download and test:
```bash
python infratagging_complete.py
```
