/**
 * Re-export Ajax from the main application
 * This wrapper allows Layerfactory to use the application's Ajax utility
 */

// Import from the main application's wrapper/ajax
// Adjust the path based on your actual project structure
// import Ajax from 'Utils/ajax';

// Placeholder Ajax implementation - replace with actual import
const Ajax = {
    call: function(options) {
        return fetch(options.url, {
            method: options.type || 'GET',
            headers: options.headers || {},
            body: options.data ? JSON.stringify(options.data) : undefined,
            credentials: options.xhrFields?.withCredentials ? 'include' : 'same-origin'
        }).then(response => response.json());
    },
    
    deferred: function() {
        let resolve, reject;
        const promise = new Promise((res, rej) => {
            resolve = res;
            reject = rej;
        });
        
        return {
            promise: () => promise,
            resolve: resolve,
            reject: reject
        };
    },
    
    wait: function(promises, successCallback, errorCallback) {
        return Promise.all(promises)
            .then(results => successCallback(...results))
            .catch(error => errorCallback(error));
    }
};

export default Ajax;
