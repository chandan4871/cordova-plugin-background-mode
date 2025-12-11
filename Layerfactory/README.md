# LayerFactory Integration

This directory contains the integrated LayerFactory code that was previously loaded from the external ePlanner application.

## Structure

```
Layerfactory/
├── layerfactory.js          # Main LayerFactory class
├── WebApi.ts                # Web API utilities
├── export-styles.css        # Styles for LayerFactory components
├── functions/               # Utility functions
│   ├── util.js/ts          # Utility functions
│   ├── layer.js            # Base Layer class
│   └── configvalidator.ts  # Config validation
├── entities/               # Layer entity classes
│   ├── mp19landuselayer.js
│   ├── parkscorelayer.js
│   ├── salessitelayer.js
│   ├── rentalofstatelandlayer.js
│   └── retaildensitylayer.js
└── wrapper/               # Wrapper utilities
    └── ajax.js/ts         # Ajax wrapper
```

## Integration

### Before (External ePlanner)
Previously, the application loaded LayerFactory from:
- JS: `https://eplanner.gov.sg/Scripts/js-built/layerfactory.js`
- CSS: `https://eplanner.gov.sg/Content/js/js-built/export-cssmin.css`

The code checked for `window.$eplannerLoaded` flag before using LayerFactory.

### After (Local Integration)
Now, the application imports LayerFactory directly:

```javascript
import 'Layerfactory/layerfactory';
import 'Layerfactory/export-styles.css';
```

The `layerfactory.js` file automatically exposes `LayerFactory` to the global `window` object, making it available as `window.LayerFactory`.

## Usage

1. **Import LayerFactory**: The import is done at the top of the component file.

2. **Access LayerFactory**: Use `window.LayerFactory` to access the singleton instance.

3. **Setup Development Environment**:
   ```javascript
   window.LayerFactory.setupDevelopmentEnvs(arcGISServerHost, spatialReference, environment);
   ```

4. **Get Layers**:
   ```javascript
   const categories = window.LayerFactory.getLayers(mapWrapper, layerWrapper, messenger, token);
   ```

## Required Dependencies

Ensure these dependencies are installed:
- `@mui/material`
- `@mui/styles`
- `@emotion/react`
- `@emotion/cache`
- `esri-leaflet`
- `esri-loader`
- `leaflet`
- `react`

## Configuration

The LayerFactory needs:
1. **OneToolMapData**: Map configuration data (imported from `../onetool`)
2. **ArcGIS Token**: User authentication token for ArcGIS services
3. **Server Configuration**: ArcGIS server host and spatial reference

## Build Configuration

Make sure your webpack/build configuration can resolve the `Layerfactory` path. You may need to add an alias:

```javascript
// webpack.config.js
resolve: {
  alias: {
    'Layerfactory': path.resolve(__dirname, 'Layerfactory'),
    // ... other aliases
  }
}
```

## Notes

- The LayerFactory wraps MUI components with style prefixes (`epl-exportjss`) to avoid conflicts with OneTool components
- All layer entities extend the base `Layer` class from `functions/layer.js`
- Web API calls are centralized in `WebApi.ts`
