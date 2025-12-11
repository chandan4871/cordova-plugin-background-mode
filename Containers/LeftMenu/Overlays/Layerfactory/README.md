# LayerFactory Integration

> 📋 **Quick Navigation:** See **[INDEX.md](./INDEX.md)** or **[FILE_LAYOUT.md](./FILE_LAYOUT.md)** for visual horizontal file layout!

This directory contains the integrated LayerFactory code that was previously loaded from the external ePlanner application.

## ✅ Completed Files (Flat Structure - Easy to Find!)

### 📂 Files Arranged by Category (All in One Folder!)

#### 🎯 **Core Files** (Row 1)
`layerfactory.js` | `WebApi.ts` | `onetool.js` | `export-css.css`

#### 🔧 **Helper Files** (Row 2)  
`ajax.js` | `util.js` | `layer.js` | `configvalidator.ts`

#### 📊 **Constants** (Row 3)
`urlconstants.js` | `aggregationconstants.js` | `chartconstants.js`

#### 🗺️ **Entity Layers** (Row 4)
`mp19landuselayer.js` | `parkscorelayer.js` | `salessitelayer.js` | `rentalofstatelandlayer.js` | `retaildensitylayer.js`

#### 📖 **Documentation** (Row 5)
`README.md` | `SETUP_GUIDE.md` | `QUICK_CHECKLIST.md` | `INTEGRATION_SUMMARY.md` | `FILES_AT_A_GLANCE.md`

---

### 📋 Quick Status Table

| **Core Files** | **Status** | **Helper Files** | **Status** | **Constants** | **Status** |
|----------------|------------|------------------|------------|---------------|------------|
| layerfactory.js | ✅ Done | ajax.js | 🔧 Update | urlconstants.js | 🔧 Update |
| WebApi.ts | ✅ Done | util.js | 🔧 Update | aggregationconstants.js | 🔧 Update |
| onetool.js | 🔧 Update | layer.js | 🔧 Update | chartconstants.js | ✅ Done |
| export-css.css | ✅ Done | configvalidator.ts | ✅ Done | | |

| **Entity Layers** | **Status** |
|-------------------|------------|
| mp19landuselayer.js | ✅ Fully Implemented |
| parkscorelayer.js | 📝 Stub - Needs Implementation |
| salessitelayer.js | 📝 Stub - Needs Implementation |
| rentalofstatelandlayer.js | 📝 Stub - Needs Implementation |
| retaildensitylayer.js | 📝 Stub - Needs Implementation |

**All 20 files are at the same level - no nested folders! Easy to find! 🎉**

## Integration

### Before (External ePlanner)
Previously, the application loaded LayerFactory from:
- JS: `https://eplanner.gov.sg/Scripts/js-built/layerfactory.js`
- CSS: `https://eplanner.gov.sg/Content/js/js-built/export-cssmin.css`

The code checked for `window.$eplannerLoaded` flag before using LayerFactory.

### After (Local Integration)
Now, the application imports LayerFactory directly in `Overlays.js`:

```javascript
import 'Containers/LeftMenu/Overlays/Layerfactory/layerfactory';
import 'Containers/LeftMenu/Overlays/Layerfactory/export-css';
```

The `layerfactory.js` file automatically exposes `LayerFactory` to the global `window` object, making it available as `window.LayerFactory`.

## Usage

The `Overlays.js` component now:

1. **Imports LayerFactory**: Direct import at the top of the component file
2. **Checks Availability**: Verifies `window.LayerFactory` is available
3. **Setup Development Environment**:
   ```javascript
   window.LayerFactory.setupDevelopmentEnvs(arcGISServerHost, spatialReference, environment);
   ```
4. **Get Layers**:
   ```javascript
   const categories = window.LayerFactory.getLayers(mapWrapper, layerWrapper, messenger, token);
   ```

## Required Dependencies

Ensure these dependencies are installed in `package.json`:

```json
{
  "dependencies": {
    "@mui/material": "^5.x.x",
    "@mui/styles": "^5.x.x",
    "@emotion/react": "^11.x.x",
    "@emotion/cache": "^11.x.x",
    "esri-leaflet": "^3.x.x",
    "esri-loader": "^3.x.x",
    "leaflet": "^1.x.x",
    "react": "^18.x.x",
    "react-dom": "^18.x.x"
  }
}
```

## 🔧 Files That Need Integration

All files have been created, but several need to be integrated with your existing application code:

### 1. Core Files
- `WebApi.ts` - Already provided by you (place in this directory)
- `onetool.js` - OneToolMapData configuration

### 2. Function Files
- `functions/util.js` or `util.ts` - Utility functions including:
  - `ConfigStoreInt`
  - `arrayToList`
  - `reversePolygonLatLng`
  - `sqmToSqkm`
  - `getFeatureCenter`
  - `polygonsToMultiPolygon`
  - `convertSquareMetersToHa`
  - `buildToDeployServer`
  - `initDevEnv`
  - `reproject`
  - `appendUrlWithParams`
  - `getGeospaceToken`

- `functions/layer.js` - Base Layer class that all entities extend

- `functions/configvalidator.ts` - Configuration validation:
  - `isValidMapConfig`
  - `getErrorMsgs`
  - `clearErrorMsgs`

### 3. Wrapper Files
- `wrapper/ajax.js` or `ajax.ts` - Ajax utility wrapper with methods like:
  - `Ajax.call()`
  - `Ajax.deferred()`
  - `Ajax.wait()`

### 4. Entity Layer Files
- `entities/parkscorelayer.js`
- `entities/salessitelayer.js`
- `entities/rentalofstatelandlayer.js`
- `entities/retaildensitylayer.js`

## Import Path Convention

The project uses webpack aliases with capital letters:
- `Components/...` for component imports
- `Constants/...` for constant imports
- `Store/...` for Redux store imports
- `Utils/...` for utility imports
- `Containers/...` for container imports

Within the Layerfactory folder, use relative paths:
- `./WebApi` for WebApi
- `./functions/util` for utility functions
- `./entities/mp19landuselayer` for entity layers
- `../functions/layer` for layer base class (from entities)

## MUI Style Prefix

The LayerFactory wraps MUI components with the prefix `epl-exportjss` to avoid conflicts with OneTool components. This is configured in `layerfactory.js`:

```javascript
const EPL_CSS_PREFIX = 'epl-exportjss';
```

All MUI components rendered by LayerFactory will have class names starting with this prefix.

## Testing

After adding all required files:

1. Start your development server
2. Navigate to the Overlays menu
3. Check browser console for:
   - `LayerFactory available: true`
   - No import errors
   - No 404 errors for ePlanner URLs
4. Test layer selection and filtering functionality

## Troubleshooting

### Issue: "Cannot find module 'Containers/LeftMenu/Overlays/Layerfactory/...'"
**Solution**: Ensure webpack is configured to resolve the `Containers` alias, or use relative paths.

### Issue: "LayerFactory is not defined"
**Solution**: Check that `layerfactory.js` is properly imported and all its dependencies are available.

### Issue: Import errors in entity layers
**Solution**: Verify all entity layer files exist and have correct import paths (use webpack aliases for external imports, relative paths for internal imports).
