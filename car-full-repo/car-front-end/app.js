// App entry point - hash-based routing for frontend navigation

// Load containers (these are ES6 modules, so they execute immediately)
import './src/containers/home-page/index.js';
import './src/containers/db-schema-page/index.js';
import './src/containers/query-page/index.js';
import './src/containers/results-page/index.js';
import './src/containers/payment-page/index.js';

// Hash-based routing
function route() {
    const hash = window.location.hash || '#/';
    
    // Normalize hash (remove trailing slash except for root)
    const normalizedHash = hash === '#' || hash === '' ? '#/' : hash;
    
    console.log('[Router] Current hash:', normalizedHash);
    console.log('[Router] renderHomePage available:', typeof window.renderHomePage);
    console.log('[Router] renderDbSchemaPage available:', typeof window.renderDbSchemaPage);
    console.log('[Router] renderQueryPage available:', typeof window.renderQueryPage);
    
    if (normalizedHash === '#/db-schema') {
        console.log('[Router] Routing to DB Schema page');
        if (window.renderDbSchemaPage) {
            window.renderDbSchemaPage();
        } else {
            console.error('[Router] renderDbSchemaPage not available! Retrying...');
            setTimeout(() => {
                if (window.renderDbSchemaPage) {
                    window.renderDbSchemaPage();
                } else {
                    console.error('[Router] renderDbSchemaPage still not available after retry');
                }
            }, 100);
        }
    } else if (normalizedHash === '#/query') {
        console.log('[Router] Routing to Query page');
        if (window.renderQueryPage) {
            window.renderQueryPage();
        } else {
            console.error('[Router] renderQueryPage not available! Retrying...');
            setTimeout(() => {
                if (window.renderQueryPage) {
                    window.renderQueryPage();
                } else {
                    console.error('[Router] renderQueryPage still not available after retry');
                }
            }, 100);
        }
    } else if (normalizedHash === '#/results') {
        console.log('[Router] Routing to Results page');
        if (window.renderResultsPage) {
            window.renderResultsPage();
        } else {
            console.error('[Router] renderResultsPage not available! Retrying...');
            setTimeout(() => {
                if (window.renderResultsPage) {
                    window.renderResultsPage();
                } else {
                    console.error('[Router] renderResultsPage still not available after retry');
                }
            }, 100);
        }
    } else if (normalizedHash === '#/payment') {
        console.log('[Router] Routing to Payment page');
        if (window.renderPaymentPage) {
            window.renderPaymentPage();
        } else {
            console.error('[Router] renderPaymentPage not available! Retrying...');
            setTimeout(() => {
                if (window.renderPaymentPage) {
                    window.renderPaymentPage();
                } else {
                    console.error('[Router] renderPaymentPage still not available after retry');
                }
            }, 100);
        }
    } else {
        console.log('[Router] Routing to Home page');
        if (window.renderHomePage) {
            window.renderHomePage();
        } else {
            console.error('[Router] renderHomePage not available! Retrying...');
            setTimeout(() => {
                if (window.renderHomePage) {
                    window.renderHomePage();
                } else {
                    console.error('[Router] renderHomePage still not available after retry');
                }
            }, 100);
        }
    }
}

// Handle hash changes
window.addEventListener('hashchange', route);

// Initialize on DOM ready
// Use a small delay to ensure modules have loaded and exposed their functions
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure ES6 modules have executed
    setTimeout(() => {
        route();
    }, 50);
});