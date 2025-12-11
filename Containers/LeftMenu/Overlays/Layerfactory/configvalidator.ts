/**
 * Configuration validator for OneTool map data
 */

let errorMessages: string[] = [];

/**
 * Validates the map configuration
 * @param mapData - The map configuration data to validate
 * @returns boolean - true if valid, false otherwise
 */
export function isValidMapConfig(mapData: any): boolean {
    errorMessages = [];

    if (!mapData) {
        errorMessages.push('Map data is null or undefined');
        return false;
    }

    if (!Array.isArray(mapData)) {
        errorMessages.push('Map data must be an array');
        return false;
    }

    let isValid = true;

    mapData.forEach((category, index) => {
        if (!category.category) {
            errorMessages.push(`Category at index ${index} is missing 'category' property`);
            isValid = false;
        }

        if (!category.layers || !Array.isArray(category.layers)) {
            errorMessages.push(`Category '${category.category}' is missing 'layers' array`);
            isValid = false;
        } else {
            category.layers.forEach((layer: any, layerIndex: number) => {
                if (!layer.name) {
                    errorMessages.push(`Layer at index ${layerIndex} in category '${category.category}' is missing 'name' property`);
                    isValid = false;
                }

                if (!layer.src) {
                    errorMessages.push(`Layer '${layer.name}' in category '${category.category}' is missing 'src' property`);
                    isValid = false;
                }
            });
        }
    });

    return isValid;
}

/**
 * Gets all error messages from validation
 * @returns string[] - Array of error messages
 */
export function getErrorMsgs(): string[] {
    return errorMessages;
}

/**
 * Clears all error messages
 */
export function clearErrorMsgs(): void {
    errorMessages = [];
}
