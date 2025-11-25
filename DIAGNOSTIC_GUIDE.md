# 🔍 Diagnostic Guide - ChartJSON Issue

## **The Problem**

You're still getting:
```json
{
  "labels": ["Unknown Layer (ID:1) - "],
  "data": [["", "", "Unknown Layer (ID:1)"]]
}
```

This means:
1. ❌ Layer matching is failing → "Unknown Layer (ID:1)"
2. ❌ No dependencies found → Only 1 empty item
3. ❌ Empty dates → ""

---

## **What I Added - Debug Logging**

I've added extensive DEBUG logging to the script to identify the problem. The new version will log:

### **In `process_infratagging_summary`:**
```
DEBUG: Available layer IDs: [1, 2, 3, 4, ...]
DEBUG: Sample layer names: ['Substations', 'Roads', 'Water', ...]
DEBUG: Layer NOT matched - LayerID=1, LayerName='', FeatureID=2022_SS_1
WARNING: X features had unmatched layers
```

This will tell us:
- ✅ What layer IDs are available
- ✅ What layer names are available  
- ❌ Which features failed to match layers

---

### **In `get_schedule_data_island_wide`:**
```
DEBUG: Processing feature: Layer='Unknown Layer (ID:1)', FeatureId='2022_SS_1'
DEBUG: Found 0 matching dependencies
```

This will tell us:
- ✅ What layer name is being searched
- ❌ Why no dependencies are found

---

## **🚀 Run with Debug Logging**

```bash
python infratagging_complete.py
```

---

## **📋 What to Send Me**

Please send me the log output showing:

1. **Layer matching section:**
```
DEBUG: Available layer IDs: [...]
DEBUG: Sample layer names: [...]
DEBUG: Layer NOT matched - LayerID=X, LayerName='...', FeatureID=...
```

2. **Dependency search section:**
```
DEBUG: Processing feature: Layer='...', FeatureId='...'
DEBUG: Found X matching dependencies
```

3. **Any WARNING messages**

---

## **🔎 What I'm Looking For**

### **Scenario 1: Layer Matching Fails**

If you see:
```
DEBUG: Layer NOT matched - LayerID=1, LayerName='', FeatureID=2022_SS_1
```

**Diagnosis:** The `SOURCELAYER` field is empty or doesn't match any layer name in `INFRATAGGING_LAYERS_VW`.

**Questions:**
1. What does this query return?
```sql
SELECT TOP 5 
    SOURCE_LAYERID, 
    SOURCE_FEATUREID,
    -- SOURCELAYER column might be missing or empty?
FROM ONETOOLAPP.INFRATAGGING_MAPPING
```

2. Does `INFRATAGGING_MAPPING` have a `SOURCELAYER` column?
3. Or do we need to JOIN to get layer names?

---

### **Scenario 2: Layer Matches, But No Dependencies**

If you see:
```
DEBUG: Processing feature: Layer='Substations', FeatureId='2022_SS_1'
DEBUG: Found 0 matching dependencies
```

**Diagnosis:** The feature exists in the layer, but has no outgoing dependencies in the mapping table.

**Questions:**
1. Does this query find dependencies?
```sql
SELECT *
FROM ONETOOLAPP.INFRATAGGING_MAPPING
WHERE SOURCE_FEATUREID = '2022_SS_1'
```

2. Are feature IDs in the mapping table formatted differently? (e.g., with/without prefix)

---

### **Scenario 3: Table Structure Issues**

**Questions I need answered:**

1. **What columns exist in `INFRATAGGING_MAPPING`?**
```sql
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'INFRATAGGING_MAPPING'
ORDER BY ORDINAL_POSITION
```

2. **Does it have a SOURCELAYER column, or just SOURCE_LAYERID?**

3. **Sample data:**
```sql
SELECT TOP 3 * 
FROM ONETOOLAPP.INFRATAGGING_MAPPING
```

4. **Sample layers:**
```sql
SELECT TOP 5 LAYER_ID, LAYER_NAME 
FROM ONETOOLAPP.INFRATAGGING_LAYERS_VW
```

---

## **💡 Possible Issues**

### **Issue 1: Missing SOURCELAYER Column**

If `INFRATAGGING_MAPPING` doesn't have a `SOURCELAYER` column, we need to:

```python
# Instead of reading it directly from mapping
src_layer = layer_dict.get(source_layer_id, {})
result['SOURCELAYER'] = src_layer.get('LAYER_NAME', '')
```

This is actually what I'm doing in `get_dependency_links_all` (lines 170-186), but maybe the layer_id doesn't match?

---

### **Issue 2: Layer ID Mismatch**

Maybe the `SOURCE_LAYERID` in the mapping table doesn't match the `LAYER_ID` in the layers table?

**Check:**
```sql
-- Are there orphaned mappings?
SELECT DISTINCT m.SOURCE_LAYERID
FROM ONETOOLAPP.INFRATAGGING_MAPPING m
WHERE NOT EXISTS (
    SELECT 1 
    FROM ONETOOLAPP.INFRATAGGING_LAYERS_VW l 
    WHERE l.LAYER_ID = m.SOURCE_LAYERID
)
```

---

### **Issue 3: Different Supporting View**

For "Supporting" type, I'm using `INFRATAGGING_MAPPING_SUPP_VW`.

**Questions:**
1. Does this view exist?
2. Does it have the same columns as `INFRATAGGING_MAPPING`?

---

## **🎯 Next Steps**

1. **Run the script** - Get the debug log output
2. **Send me the DEBUG lines** - Especially layer matching and dependency search
3. **Run the SQL queries** - Send me the results
4. **I'll identify the exact issue** - And fix the code accordingly

---

## **Quick Diagnostic Queries**

Run these and send me the results:

```sql
-- 1. Check mapping table structure
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'INFRATAGGING_MAPPING'
ORDER BY ORDINAL_POSITION;

-- 2. Sample mapping data
SELECT TOP 3 * 
FROM ONETOOLAPP.INFRATAGGING_MAPPING;

-- 3. Sample layers
SELECT TOP 5 LAYER_ID, LAYER_NAME 
FROM ONETOOLAPP.INFRATAGGING_LAYERS_VW;

-- 4. Check if SOURCE_LAYERID matches LAYER_ID
SELECT 
    COUNT(*) as Total_Mappings,
    COUNT(DISTINCT m.SOURCE_LAYERID) as Unique_Source_Layers,
    SUM(CASE WHEN l.LAYER_ID IS NULL THEN 1 ELSE 0 END) as Unmatched_Layers
FROM ONETOOLAPP.INFRATAGGING_MAPPING m
LEFT JOIN ONETOOLAPP.INFRATAGGING_LAYERS_VW l 
    ON l.LAYER_ID = m.SOURCE_LAYERID;

-- 5. Sample staging data
SELECT TOP 3 * 
FROM ONETOOLAPP.INFRA_CONS_STAGINGYR_VW;
```

---

🔍 **With this debug info, I can pinpoint the exact issue and fix it!**
