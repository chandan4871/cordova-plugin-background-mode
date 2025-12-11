/**
 * Re-export Layer from the main application
 * This wrapper allows Layerfactory entity layers to extend the application's Layer class
 */

// Import the base Layer class from your application
// The layer.js you provided appears to be from the main application
// Adjust this import path to match where your actual Layer class is located

// If your Layer class is in a different location, update this path
// For example, it might be at: 'Containers/LeftMenu/Overlays/Layer'
// or somewhere in a shared layers directory

// Placeholder - you need to point this to your actual Layer class location
export default class Layer {
    constructor(opts, token) {
        this.opts = opts || {};
        this.token = token;
        this.name = opts.name || 'Unnamed Layer';
    }

    // Add minimal methods that entity layers might use
    getToken() {
        return typeof this.token === 'function' ? this.token() : this.token;
    }

    setMap(mapWrapper) {
        this.map = mapWrapper;
    }

    getName() {
        return this.name;
    }

    // Placeholder methods - implement as needed
    getFilterbox() {
        return null;
    }

    getIdentifyDisplay() {
        return null;
    }

    refreshFilterbox() {
        // Implement refresh logic
    }

    highlightZoomCenterMap(geometry, zoom, center) {
        // Implement highlight/zoom logic
    }

    clearHighlights() {
        // Implement clear highlights logic
    }

    displayMessage(message) {
        console.log(message);
    }

    showErrorModal(message) {
        console.error(message);
    }
}
