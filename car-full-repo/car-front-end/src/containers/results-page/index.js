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
    const extractedFields = data.extracted_fields || {};
    const sqlQuery = data.sql_query || '';
    const sqlParams = data.sql_params || [];
    
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
                <!-- Left Sidebar: Query Validation Info -->
                <div class="cds-validation-sidebar">
                    <h3>Query Validation</h3>
                    <div class="validation-section">
                        <h4>Extracted Fields</h4>
                        <div class="extracted-fields">
                            ${renderExtractedFields(extractedFields)}
                        </div>
                    </div>
                    <div class="validation-section">
                        <h4>Generated SQL</h4>
                        <div class="sql-query-display">
                            <pre><code>${escapeHtml(formatSqlQuery(sqlQuery, sqlParams))}</code></pre>
                        </div>
                    </div>
                </div>
                
                <!-- Main Results Card -->
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

// Render extracted fields in a readable format
function renderExtractedFields(fields) {
    if (!fields || Object.keys(fields).length === 0) {
        return '<p class="no-data">No fields extracted</p>';
    }
    
    const formatValue = (value) => {
        if (value === null || value === undefined) {
            return '<span class="value-null">null</span>';
        }
        if (Array.isArray(value)) {
            return `<span class="value-array">[${value.map(v => escapeHtml(String(v))).join(', ')}]</span>`;
        }
        if (typeof value === 'object') {
            return `<span class="value-object">{${Object.keys(value).length} keys}</span>`;
        }
        return `<span class="value-text">${escapeHtml(String(value))}</span>`;
    };
    
    const formatKey = (key) => {
        // Convert snake_case or camelCase to Title Case
        return key
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    };
    
    let html = '<dl class="fields-list">';
    for (const [key, value] of Object.entries(fields)) {
        html += `
            <dt>${escapeHtml(formatKey(key))}</dt>
            <dd>${formatValue(value)}</dd>
        `;
    }
    html += '</dl>';
    
    return html;
}

// Format SQL query with parameters for display
function formatSqlQuery(sql, params) {
    if (!sql) {
        return 'No SQL query generated';
    }
    
    let formatted = sql;
    
    // Replace ? placeholders with parameter values
    if (params && params.length > 0) {
        params.forEach((param) => {
            // Handle different parameter types
            let displayValue;
            if (param === null || param === undefined) {
                displayValue = 'NULL';
            } else if (typeof param === 'string') {
                displayValue = `'${param.replace(/'/g, "''")}'`; // Escape single quotes in SQL strings
            } else if (Array.isArray(param)) {
                displayValue = `(${param.map(p => typeof p === 'string' ? `'${p.replace(/'/g, "''")}'` : p).join(', ')})`;
            } else {
                displayValue = param;
            }
            
            // Replace first occurrence of ? with the parameter value
            formatted = formatted.replace('?', displayValue);
        });
    }
    
    // Basic SQL formatting - add line breaks before major keywords
    formatted = formatted
        .replace(/\bSELECT\b/gi, '\nSELECT')
        .replace(/\bFROM\b/gi, '\nFROM')
        .replace(/\bWHERE\b/gi, '\nWHERE')
        .replace(/\bAND\b/gi, '\n  AND')
        .replace(/\bOR\b/gi, '\n  OR')
        .replace(/\bORDER BY\b/gi, '\nORDER BY')
        .replace(/\bGROUP BY\b/gi, '\nGROUP BY')
        .replace(/\bHAVING\b/gi, '\nHAVING')
        .replace(/\bEXISTS\b/gi, '\n  EXISTS')
        .replace(/\(\s*SELECT/gi, '(\n    SELECT')
        .trim();
    
    return formatted;
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

