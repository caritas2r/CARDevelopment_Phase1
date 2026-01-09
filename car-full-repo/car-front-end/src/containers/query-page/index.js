// Query Page - NLP query submission using Carbon Design System v11
const API_BASE_URL = 'http://localhost:5000';

// Sample placeholder texts that rotate
const PLACEHOLDER_TEXTS = [
    'Looking for a manual corvette under 60k',
    'Looking for a family-friendly SUV to haul me and my 2 kids and dog around to sporting events.',
    'Looking for a BMW or some other fast european car with less than 40k miles'
];

let placeholderIndex = 0;
let placeholderInterval = null;

// Create and render the query page
function renderQueryPage() {
    const appDiv = document.getElementById('app');
    
    appDiv.innerHTML = `
        <div class="container">
            <header class="cds-header">
                <h1>Car Query</h1>
                <p>Submit your vehicle search query</p>
                <nav class="cds-nav">
                    <a href="#/" class="cds-button cds-button--secondary">Back to Home</a>
                    <a href="#/query" class="cds-button cds-button--primary">New Query</a>
                </nav>
            </header>
            <main class="cds-content">
                <div class="cds-query-card">
                    <h2>What kind of car are you looking for</h2>
                    <div class="cds-query-form">
                        <textarea 
                            id="queryInput" 
                            class="cds-textarea" 
                            rows="4" 
                            placeholder=""
                            aria-label="Enter your car search query"
                        ></textarea>
                        <div id="placeholderText" class="cds-placeholder-text"></div>
                        <button id="submitButton" class="cds-button cds-button--primary cds-button--submit">
                            Submit Query
                        </button>
                    </div>
                    <div id="queryStatus" class="cds-query-status"></div>
                    <div class="cds-action-buttons">
                        <a href="#/" class="cds-button cds-button--secondary">Back to Home</a>
                    </div>
                </div>
            </main>
        </div>
    `;
    
    // Initialize rotating placeholder
    initializePlaceholder();
    
    // Setup form handlers
    setupFormHandlers();
}

// Initialize rotating placeholder text
function initializePlaceholder() {
    const input = document.getElementById('queryInput');
    const placeholderDiv = document.getElementById('placeholderText');
    
    // Function to update placeholder visibility
    const updatePlaceholderVisibility = () => {
        if (input.value.trim() || document.activeElement === input) {
            placeholderDiv.style.opacity = '0';
        } else {
            placeholderDiv.style.opacity = '1';
        }
    };
    
    // Show first placeholder
    updatePlaceholder();
    updatePlaceholderVisibility();
    
    // Update placeholder when input is focused/blurred
    input.addEventListener('focus', () => {
        updatePlaceholderVisibility();
        if (placeholderInterval) {
            clearInterval(placeholderInterval);
            placeholderInterval = null;
        }
    });
    
    input.addEventListener('blur', () => {
        updatePlaceholderVisibility();
        if (!input.value.trim()) {
            startPlaceholderRotation();
        }
    });
    
    // Update placeholder when input changes
    input.addEventListener('input', () => {
        updatePlaceholderVisibility();
        if (input.value.trim() && placeholderInterval) {
            clearInterval(placeholderInterval);
            placeholderInterval = null;
        } else if (!input.value.trim() && document.activeElement !== input) {
            startPlaceholderRotation();
        }
    });
    
    // Start rotation if input is empty
    if (!input.value.trim()) {
        startPlaceholderRotation();
    }
}

// Update placeholder text
function updatePlaceholder() {
    const placeholderDiv = document.getElementById('placeholderText');
    if (placeholderDiv) {
        placeholderDiv.textContent = PLACEHOLDER_TEXTS[placeholderIndex];
    }
}

// Start rotating placeholder text
function startPlaceholderRotation() {
    if (placeholderInterval) {
        clearInterval(placeholderInterval);
    }
    
    placeholderInterval = setInterval(() => {
        placeholderIndex = (placeholderIndex + 1) % PLACEHOLDER_TEXTS.length;
        updatePlaceholder();
    }, 3000); // Rotate every 3 seconds
}

// Setup form submission handlers
function setupFormHandlers() {
    const input = document.getElementById('queryInput');
    const submitButton = document.getElementById('submitButton');
    const statusDiv = document.getElementById('queryStatus');
    
    // Handle form submission
    const handleSubmit = async () => {
        const queryText = input.value.trim();
        
        if (!queryText) {
            statusDiv.innerHTML = `
                <div class="cds-status-indicator error">
                    <span class="cds-status-icon">✕</span>
                    <span class="cds-status-text">Please enter a query</span>
                </div>
            `;
            return;
        }
        
        // Disable submit button
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';
        
        // Show loading status
        statusDiv.innerHTML = `
            <div class="cds-status-indicator loading">
                <span class="cds-status-icon">⏳</span>
                <span class="cds-status-text">Processing query...</span>
            </div>
        `;
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/query/v1`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: queryText })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            if (data.success) {
                // Store results in sessionStorage for results page
                sessionStorage.setItem('queryResults', JSON.stringify(data));
                
                // Show success message briefly, then navigate to results page
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator success">
                        <span class="cds-status-icon">✓</span>
                        <span class="cds-status-text">Query processed successfully. Found ${data.result_count || 0} result${(data.result_count || 0) !== 1 ? 's' : ''}.</span>
                    </div>
                    <div class="cds-status-details success">
                        <p>Redirecting to results page...</p>
                    </div>
                `;
                
                // Navigate to results page after brief delay
                setTimeout(() => {
                    window.location.hash = '#/results';
                }, 1000);
            } else {
                throw new Error(data.error || 'Query failed');
            }
        } catch (error) {
            statusDiv.innerHTML = `
                <div class="cds-status-indicator error">
                    <span class="cds-status-icon">✕</span>
                    <span class="cds-status-text">Error submitting query</span>
                </div>
                <div class="cds-status-details error">
                    <p><strong>Error:</strong> ${escapeHtml(error.message)}</p>
                </div>
            `;
        } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Submit Query';
        }
    };
    
    // Submit on button click
    submitButton.addEventListener('click', handleSubmit);
    
    // Submit on Enter (but allow Shift+Enter for new lines)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });
}

// Escape HTML to prevent XSS
function escapeHtml(s) {
    return String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}

// Format SQL query with parameters for display
function formatSqlQuery(sql, params) {
    let formatted = sql;
    
    // Replace ? placeholders with parameter values
    if (params && params.length > 0) {
        params.forEach((param, idx) => {
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

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (placeholderInterval) {
        clearInterval(placeholderInterval);
    }
});

// Expose renderQueryPage for routing
window.renderQueryPage = renderQueryPage;
console.log('[QueryPage] renderQueryPage function exposed to window');

