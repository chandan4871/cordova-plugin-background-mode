# LayerFactory Integration - Quick Checklist

## ✅ Complete These Tasks in Order

### Phase 1: Fix Import Errors (Required to run)

- [ ] **Step 1**: Find your actual `Ajax` utility file location
  - Look in: `src/Utils/`, `src/wrapper/`, or similar
  - Update `ajax.js` line 3 with correct import path

- [ ] **Step 2**: Find your actual utility functions file
  - Look in: `src/Utils/helpers.js`, `src/functions/util.js`, or similar
  - Update `util.js` with correct import path

- [ ] **Step 3**: Find your actual Layer base class
  - Look for your Layer.js file (you provided the code earlier)
  - Update `layer.js` with correct import path or copy the class

- [ ] **Step 4**: Find your URL constants file
  - Look in: `src/Constants/urlconstants.js` or similar
  - Update `urlconstants.js` with correct import path

- [ ] **Step 5**: Find your aggregation constants file
  - Look in: `src/Constants/aggregationconstants.js` or similar
  - Update `aggregationconstants.js` with correct import path

### Phase 2: Configure Data

- [ ] **Step 6**: Update `onetool.js` with your actual layer configurations
  - Add your layer categories
  - Add layer definitions (name, src, layers, etc.)
  - Refer to your existing layer data

### Phase 3: Test

- [ ] **Step 7**: Run `npm start` and check browser console
  - [ ] No import errors
  - [ ] `window.LayerFactory` is defined
  - [ ] No ePlanner 404 errors

- [ ] **Step 8**: Test in application
  - [ ] Navigate to Overlays menu
  - [ ] Layers display correctly
  - [ ] Can select/deselect layers
  - [ ] Filters work (if applicable)

### Phase 4: Implement Entity Layers (Optional but recommended)

- [ ] **Step 9**: Implement `parkscorelayer.js`
  - Use `mp19landuselayer.js` as template

- [ ] **Step 10**: Implement `salessitelayer.js`
  - Use `mp19landuselayer.js` as template

- [ ] **Step 11**: Implement `rentalofstatelandlayer.js`
  - Use `mp19landuselayer.js` as template

- [ ] **Step 12**: Implement `retaildensitylayer.js`
  - Use `mp19landuselayer.js` as template

### Phase 5: Cleanup

- [ ] **Step 13**: Remove old ePlanner integration code
  - [ ] Remove external script loading code
  - [ ] Remove `window.$eplannerLoaded` checks
  - [ ] Remove ePlanner URL references

- [ ] **Step 14**: Final testing
  - [ ] All layers work
  - [ ] All filters work
  - [ ] No errors in console
  - [ ] Performance is good

## 🎯 Priority Order

**Must Do Now (Blocks application)**:
- Steps 1-5 (Fix imports)

**Should Do Soon (App works but layers won't load)**:
- Step 6 (Configure onetool.js)

**Can Do Later (Optional features)**:
- Steps 9-12 (Implement entity layers)

**Do Last (Cleanup)**:
- Steps 13-14 (Remove old code)

## 📝 Quick Reference

### Files to Edit (Priority Order) - All at Root Level!:
1. `ajax.js` - Line 8
2. `util.js` - Line 7
3. `layer.js` - Line 10
4. `urlconstants.js` - Line 6
5. `aggregationconstants.js` - Line 7
6. `onetool.js` - Replace entire OneToolMapData array

**Everything is in one folder - super easy to find!** 🎉

### Where to Find Your Files:
```
Your Project Root/
├── src/
│   ├── Utils/ or wrapper/
│   │   └── ajax.js (Step 1)
│   │   └── helpers.js (Step 2)
│   ├── Constants/
│   │   └── urlconstants.js (Step 4)
│   │   └── aggregationconstants.js (Step 5)
│   └── [somewhere]/
│       └── Layer.js (Step 3)
```

### Webpack Aliases (Common):
- `Utils/` → `src/Utils/`
- `Constants/` → `src/Constants/`
- `Components/` → `src/Components/`
- `Containers/` → `src/Containers/`

If these don't work, check your `webpack.config.js` for actual aliases.

## ⚡ Fastest Path to Working Application

1. Find all 5 actual file locations (Steps 1-5)
2. Update all 5 import paths in wrapper/functions/constants files
3. Add ONE layer to `onetool.js` for testing
4. Run `npm start`
5. Test in browser
6. If it works, add more layers; if not, check console errors

## 🆘 Emergency Fallback

If you can't find the actual files:
1. The placeholder implementations might actually work for basic testing
2. Focus on getting `onetool.js` configured with your layers
3. You can implement entity layers later
4. The app should at least start without errors

---

**Start Here**: Open `SETUP_GUIDE.md` for detailed instructions on each step!

**Got Errors?**: Check browser console → Google the error → Update the import path → Restart server
