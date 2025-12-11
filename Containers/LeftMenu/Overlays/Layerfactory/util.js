/**
 * Re-export utility functions from the main application
 * This wrapper allows Layerfactory to use the application's utility functions
 */

// Import from the main application's utils
// Adjust the path based on your actual project structure
// For now, providing placeholder implementations

// Export ConfigStoreInt
export const ConfigStoreInt = {
    export: false,
    server: '',
    sr: 4326,
    environment: 'EXTRANET'
};

// Placeholder implementations - replace with actual imports from your application
export function appendUrlWithParams(url, params) {
    const queryString = Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
    return url + (url.includes('?') ? '&' : '?') + queryString;
}

export function generateCSVString(data) {
    // Implement CSV generation
    return '';
}

export function reversePolygonLatLng(geometry) {
    // Implement coordinate reversal
    return geometry;
}

export function getFeatureCenter(geometry) {
    // Implement center calculation
    return [0, 0];
}

export function isInt(value) {
    return Number.isInteger(Number(value));
}

export function logout() {
    // Implement logout
}

export function reproject(coords, from, to) {
    // Implement reprojection
    return coords;
}

export function buildToDeployServer(path) {
    return ConfigStoreInt.server + path;
}

export function sqmToSqkm(sqm, decimals = 2) {
    return (sqm / 1000000).toFixed(decimals);
}

export function polygonsToMultiPolygon(polygons) {
    return {
        type: 'MultiPolygon',
        coordinates: polygons
    };
}

export function convertSquareMetersToHa(sqm) {
    return (sqm / 10000).toFixed(2);
}

export function initDevEnv() {
    // Initialize development environment
}

export function arrayToList(array) {
    return array;
}

export function getGeospaceToken() {
    return '';
}
