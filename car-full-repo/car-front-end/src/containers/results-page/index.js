// Results Page - Displays query results with paywall
const API_BASE_URL = 'http://localhost:5000';

// Results to display (first 2 visible, rest blurred)
const FREE_RESULTS_COUNT = 2;

// Create and render the results page
function renderResultsPage() {
    const appDiv = document.getElementById('app');
    
    // Get results from sessionStorage (passed from query page)
    const resultsData = sessionStorage.getItem('queryResults');
    
    if (!resultsData) {
        // No results data found, redirect to query page
        window.location.hash = '#/query';
        return;
    }
    
    let data;
    try {
        data = JSON.parse(resultsData);
    } catch (e) {
        console.error('Failed to parse results data:', e);
        window.location.hash = '#/query';
        return;
    }
    
    const queryText = data.query || 'Your query';
    const results = data.results || [];
    const resultCount = data.result_count || results.length;
    
    // Check if payment has been completed
    const paymentCompleted = sessionStorage.getItem('paymentCompleted') === 'true';
    
    // Split results into free (visible) and premium (blurred)
    // If payment completed, show all results; otherwise show first 2 free
    const freeResults = paymentCompleted ? results : results.slice(0, FREE_RESULTS_COUNT);
    const premiumResults = paymentCompleted ? [] : results.slice(FREE_RESULTS_COUNT);
    
    appDiv.innerHTML = `
        <div class="container">
            <header class="cds-header">
                <h1>Search Results</h1>
                <p>Found ${resultCount} vehicle${resultCount !== 1 ? 's' : ''} matching your query</p>
                <nav class="cds-nav">
                    <a href="#/" class="cds-button cds-button--secondary">Back to Home</a>
                    <a href="#/query" class="cds-button cds-button--secondary">New Query</a>
                </nav>
            </header>
            <main class="cds-content">
                <div class="cds-results-card">
                    <div class="results-header">
                        <h2>Query: "${escapeHtml(queryText)}"</h2>
                        <p class="results-count">
                            ${paymentCompleted 
                                ? `Showing all ${resultCount} result${resultCount !== 1 ? 's' : ''} (Unlocked)`
                                : `Showing ${freeResults.length} of ${resultCount} results`
                            }
                        </p>
                    </div>
                    
                    <div class="results-container">
                        <!-- Free Results (Fully Visible) -->
                        ${freeResults.map((vehicle, idx) => renderVehicleCard(vehicle, idx, false)).join('')}
                        
                        <!-- Premium Results (Blurred) -->
                        ${premiumResults.map((vehicle, idx) => renderVehicleCard(vehicle, idx + FREE_RESULTS_COUNT, true)).join('')}
                    </div>
                    
                    ${premiumResults.length > 0 ? `
                        <div class="paywall-blur-overlay" onclick="navigateToPayment()">
                            <div class="paywall-content">
                                <h3>🔒 Unlock ${premiumResults.length} More Result${premiumResults.length !== 1 ? 's' : ''}</h3>
                                <p>Get full access to all ${resultCount} search results</p>
                                <button class="cds-button cds-button--primary paywall-button">
                                    View All Results
                                </button>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </main>
        </div>
    `;
    
    // Expose navigation function to global scope for onclick handler
    window.navigateToPayment = function() {
        window.location.hash = '#/payment';
    };
}

function renderVehicleCard(vehicle, index, isBlurred) {
    const blurClass = isBlurred ? 'blurred-result' : '';
    const blurOverlay = isBlurred ? '<div class="blur-overlay" onclick="navigateToPayment()"><span class="blur-text">Click to unlock</span></div>' : '';
    
    return `
        <div class="query-result-item ${blurClass}" data-index="${index}" ${isBlurred ? 'onclick="navigateToPayment()"' : ''}>
            ${blurOverlay}
            <h4>${escapeHtml(vehicle.make || '')} ${escapeHtml(vehicle.model || '')} ${vehicle.year || ''}</h4>
            <div class="result-details">
                <p><strong>Price:</strong> $${vehicle.price?.toLocaleString() || 'N/A'} (${vehicle.currency === 840 ? 'USD' : vehicle.currency || 'N/A'})</p>
                <p><strong>Mileage:</strong> ${vehicle.mileage?.toLocaleString() || 'N/A'} miles</p>
                <p><strong>Body Style:</strong> ${escapeHtml(vehicle.body_style || 'N/A')}</p>
                <p><strong>Transmission:</strong> ${escapeHtml(vehicle.transmission || 'N/A')}</p>
                <p><strong>Drivetrain:</strong> ${escapeHtml(vehicle.drivetrain || 'N/A')}</p>
                ${vehicle.powertrain_types && vehicle.powertrain_types.length > 0 ? `<p><strong>Powertrain:</strong> ${vehicle.powertrain_types.map(pt => escapeHtml(pt)).join(', ')}</p>` : '<p><strong>Powertrain:</strong> N/A</p>'}
                ${vehicle.seating_capacity ? `<p><strong>Seating:</strong> ${vehicle.seating_capacity}</p>` : ''}
                ${vehicle.color ? `<p><strong>Color:</strong> ${escapeHtml(vehicle.color)}</p>` : ''}
                <p><strong>Number of Owners:</strong> ${vehicle.number_of_owners !== null && vehicle.number_of_owners !== undefined ? vehicle.number_of_owners : 'N/A'}</p>
                ${vehicle.city ? `<p><strong>Location:</strong> ${escapeHtml(vehicle.city || '')}, ${escapeHtml(vehicle.state_region || '')}</p>` : ''}
                ${vehicle.features && vehicle.features.length > 0 ? `<p><strong>Features:</strong> ${vehicle.features.map(f => escapeHtml(f)).join(', ')}</p>` : ''}
                ${vehicle.use_case_tags && vehicle.use_case_tags.length > 0 ? `<p><strong>Use Cases:</strong> ${vehicle.use_case_tags.map(t => escapeHtml(t)).join(', ')}</p>` : ''}
            </div>
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(s) {
    return String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}

// Expose renderResultsPage for routing
window.renderResultsPage = renderResultsPage;
console.log('[ResultsPage] renderResultsPage function exposed to window');

