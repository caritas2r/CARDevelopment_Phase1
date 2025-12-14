// Database Schema Page - Visualizes SQLite database schema
const API_BASE_URL = 'http://localhost:5000';

// Escape HTML to prevent XSS
function escapeHtml(s) {
    return String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}

// Render the database schema page
function renderDbSchemaPage() {
    const appDiv = document.getElementById('app');
    
    appDiv.innerHTML = `
        <div class="container">
            <header class="cds-header">
                <h1>Database Schema</h1>
                <p>SQLite layout validation</p>
                <nav class="cds-nav">
                    <a href="#/" class="cds-button cds-button--secondary">Back to Home</a>
                    <a href="#/db-schema" class="cds-button cds-button--primary">DB Schema</a>
                </nav>
            </header>
            <main class="cds-content">
                <div class="cds-status-card" data-page="db-schema">
                    <h2>Schema Snapshot</h2>
                    <div id="schemaStatus">
                        <div class="cds-status-indicator loading">
                            <span class="cds-status-icon">⏳</span>
                            <span class="cds-status-text">Loading schema...</span>
                        </div>
                    </div>
                    <div id="schemaBody"></div>
                </div>
            </main>
        </div>
    `;
    
    loadSchema();
}

// Load schema from backend API
async function loadSchema() {
    const statusDiv = document.getElementById('schemaStatus');
    const bodyDiv = document.getElementById('schemaBody');
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/db/schema`);
        
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        const data = await res.json();
        
        statusDiv.innerHTML = `
            <div class="cds-status-indicator success">
                <span class="cds-status-icon">✓</span>
                <span class="cds-status-text">Schema loaded successfully</span>
            </div>
            <div class="cds-status-details success">
                <p><strong>Database:</strong> ${escapeHtml(data.database_path)}</p>
            </div>
        `;
        
        if (data.tables && data.tables.length > 0) {
            bodyDiv.innerHTML = data.tables.map(t => `
                <div class="schema-table">
                    <h3>Table: ${escapeHtml(t.name)}</h3>
                    <div class="schema-details">
                        <h4>Columns (${t.columns.length}):</h4>
                        <table class="schema-table-data">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>NOT NULL</th>
                                    <th>Default</th>
                                    <th>Primary Key</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${t.columns.map(col => `
                                    <tr>
                                        <td><strong>${escapeHtml(col.name)}</strong></td>
                                        <td>${escapeHtml(col.type)}</td>
                                        <td>${col.notnull ? 'Yes' : 'No'}</td>
                                        <td>${col.default ? escapeHtml(String(col.default)) : '-'}</td>
                                        <td>${col.pk ? 'Yes' : 'No'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        
                        ${t.indexes && t.indexes.length > 0 ? `
                            <h4>Indexes (${t.indexes.length}):</h4>
                            <ul>
                                ${t.indexes.map(idx => `
                                    <li>
                                        <strong>${escapeHtml(idx.name)}</strong>
                                        ${idx.unique ? '(UNIQUE)' : ''}
                                        - Columns: ${idx.columns.filter(c => c != null).map(c => escapeHtml(c)).join(', ') || 'None'}
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                        
                        ${t.foreign_keys && t.foreign_keys.length > 0 ? `
                            <h4>Foreign Keys (${t.foreign_keys.length}):</h4>
                            <ul>
                                ${t.foreign_keys.map(fk => `
                                    <li>
                                        ${escapeHtml(fk.from)} → ${escapeHtml(fk.table)}.${escapeHtml(fk.to)}
                                        (ON DELETE: ${escapeHtml(fk.on_delete)}, ON UPDATE: ${escapeHtml(fk.on_update)})
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        } else {
            bodyDiv.innerHTML = '<p>No tables found in database.</p>';
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="cds-status-indicator error">
                <span class="cds-status-icon">✕</span>
                <span class="cds-status-text">Failed to load schema</span>
            </div>
            <div class="cds-status-details error">
                <p><strong>Error:</strong> ${escapeHtml(error.message)}</p>
                <p>Please ensure the backend is running at ${API_BASE_URL}</p>
            </div>
        `;
        bodyDiv.innerHTML = '';
    }
}

// Expose renderDbSchemaPage for routing
window.renderDbSchemaPage = renderDbSchemaPage;
console.log('[DbSchemaPage] renderDbSchemaPage function exposed to window');

