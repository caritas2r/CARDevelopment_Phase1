// Shared utility functions used across multiple containers

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} s - String to escape
 * @returns {string} Escaped string
 */
export function escapeHtml(s) {
    return String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}

/**
 * Format SQL query with parameters for display
 * Replaces ? placeholders with parameter values and formats SQL for readability
 * @param {string} sql - SQL query string
 * @param {Array} params - Array of parameter values
 * @returns {string} Formatted SQL query string
 */
export function formatSqlQuery(sql, params) {
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

