// Home page container - IBM Carbon Design System v11
const API_BASE_URL = 'http://localhost:5000';

// Create and render the home page using Carbon design patterns
function renderHomePage() {
    const appDiv = document.getElementById('app');
    
    appDiv.innerHTML = `
        <div class="container">
            <header class="cds-header">
                <h1>Car Management System</h1>
                <p>Backend Connection Status</p>
                <nav class="cds-nav">
                    <a href="#/" class="cds-button cds-button--primary">Home</a>
                    <a href="#/query" class="cds-button cds-button--secondary">New Query</a>
                    <a href="#/db-schema" class="cds-button cds-button--secondary">View DB Schema</a>
                </nav>
            </header>
            <main class="cds-content">
                <div class="cds-status-card" data-page="home">
                    <h2>System Status</h2>
                    <div id="connectionStatus" class="cds-status-indicator loading">
                        <span class="cds-status-icon">⏳</span>
                        <span class="cds-status-text">Checking connection...</span>
                    </div>
                    <div id="statusDetails" class="cds-status-details"></div>
                    <div class="cds-action-buttons">
                        <a href="#/query" class="cds-button cds-button--primary">Start New Query</a>
                    </div>
                </div>
            </main>
        </div>
    `;
    
    // Check backend connection
    checkBackendConnection();
}

// Check if backend is connected
async function checkBackendConnection() {
    const statusDiv = document.getElementById('connectionStatus');
    const detailsDiv = document.getElementById('statusDetails');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        
        if (response.ok && data.status === 'online') {
            // Success - backend is connected
            statusDiv.className = 'cds-status-indicator success';
            statusDiv.innerHTML = `
                <span class="cds-status-icon">✓</span>
                <span class="cds-status-text">Connected to Backend</span>
            `;
            detailsDiv.innerHTML = `
                <p><strong>Status:</strong> ${data.status}</p>
                <p><strong>Message:</strong> ${data.message}</p>
                <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
            `;
            detailsDiv.className = 'cds-status-details success';
        } else {
            throw new Error('Unexpected response');
        }
    } catch (error) {
        // Error - backend is not connected
        statusDiv.className = 'cds-status-indicator error';
        statusDiv.innerHTML = `
            <span class="cds-status-icon">✕</span>
            <span class="cds-status-text">Backend Not Connected</span>
        `;
        detailsDiv.innerHTML = `
            <p>Unable to reach backend at <code>${API_BASE_URL}</code></p>
            <p><em>Please ensure the Flask backend service is running.</em></p>
        `;
        detailsDiv.className = 'cds-status-details error';
    }
}

// Expose renderHomePage for routing
window.renderHomePage = renderHomePage;
console.log('[HomePage] renderHomePage function exposed to window');