// Payment Page - Stripe payment simulation for unlocking results

// Create and render the payment page
function renderPaymentPage() {
    const appDiv = document.getElementById('app');
    
    // Get results data to know how many results we're unlocking
    const resultsData = sessionStorage.getItem('queryResults');
    let resultCount = 0;
    let premiumCount = 0;
    
    if (resultsData) {
        try {
            const data = JSON.parse(resultsData);
            resultCount = data.result_count || 0;
            const results = data.results || [];
            premiumCount = Math.max(0, results.length - 2); // Results beyond first 2
        } catch (e) {
            console.error('Failed to parse results data:', e);
        }
    }
    
    appDiv.innerHTML = `
        <div class="container">
            <header class="cds-header">
                <h1>Unlock Full Results</h1>
                <p>Complete payment to view all ${resultCount} search results</p>
                <nav class="cds-nav">
                    <a href="#/results" class="cds-button cds-button--secondary">Back to Results</a>
                    <a href="#/" class="cds-button cds-button--secondary">Home</a>
                </nav>
            </header>
            <main class="cds-content">
                <div class="cds-payment-card">
                    <div class="payment-summary">
                        <h2>Payment Summary</h2>
                        <div class="summary-item">
                            <span>Unlock ${premiumCount} additional result${premiumCount !== 1 ? 's' : ''}</span>
                            <span class="price">$9.99</span>
                        </div>
                        <div class="summary-divider"></div>
                        <div class="summary-item total">
                            <span><strong>Total</strong></span>
                            <span class="price"><strong>$9.99</strong></span>
                        </div>
                    </div>
                    
                    <div class="payment-form">
                        <h3>Payment Information</h3>
                        <p class="payment-note">This is a simulation - no real payment will be processed</p>
                        
                        <div class="form-group">
                            <label for="cardNumber">Card Number</label>
                            <input 
                                type="text" 
                                id="cardNumber" 
                                class="cds-input" 
                                placeholder="4242 4242 4242 4242"
                                maxlength="19"
                            />
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="expiry">Expiry Date</label>
                                <input 
                                    type="text" 
                                    id="expiry" 
                                    class="cds-input" 
                                    placeholder="MM/YY"
                                    maxlength="5"
                                />
                            </div>
                            <div class="form-group">
                                <label for="cvv">CVV</label>
                                <input 
                                    type="text" 
                                    id="cvv" 
                                    class="cds-input" 
                                    placeholder="123"
                                    maxlength="4"
                                />
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="cardName">Cardholder Name</label>
                            <input 
                                type="text" 
                                id="cardName" 
                                class="cds-input" 
                                placeholder="John Doe"
                            />
                        </div>
                        
                        <button id="submitPayment" class="cds-button cds-button--primary payment-submit">
                            Pay $9.99
                        </button>
                        
                        <div id="paymentStatus" class="payment-status"></div>
                    </div>
                </div>
            </main>
        </div>
    `;
    
    setupPaymentForm();
}

function setupPaymentForm() {
    const cardNumberInput = document.getElementById('cardNumber');
    const expiryInput = document.getElementById('expiry');
    const cvvInput = document.getElementById('cvv');
    const submitButton = document.getElementById('submitPayment');
    const statusDiv = document.getElementById('paymentStatus');
    
    // Format card number with spaces
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
            let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formatted;
        });
    }
    
    // Format expiry date (MM/YY)
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
    
    // CVV - numbers only
    if (cvvInput) {
        cvvInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }
    
    // Handle payment submission
    if (submitButton) {
        submitButton.addEventListener('click', () => {
            const cardNumber = cardNumberInput?.value.replace(/\s/g, '') || '';
            const expiry = expiryInput?.value || '';
            const cvv = cvvInput?.value || '';
            const cardName = document.getElementById('cardName')?.value || '';
            
            // Basic validation
            if (cardNumber.length < 13 || cardNumber.length > 19) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Please enter a valid card number</span>
                    </div>
                `;
                return;
            }
            
            if (expiry.length !== 5 || !expiry.match(/^\d{2}\/\d{2}$/)) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Please enter a valid expiry date (MM/YY)</span>
                    </div>
                `;
                return;
            }
            
            if (cvv.length < 3 || cvv.length > 4) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Please enter a valid CVV</span>
                    </div>
                `;
                return;
            }
            
            if (!cardName.trim()) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Please enter cardholder name</span>
                    </div>
                `;
                return;
            }
            
            // Simulate payment processing
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';
            statusDiv.innerHTML = `
                <div class="cds-status-indicator loading">
                    <span class="cds-status-icon">⏳</span>
                    <span class="cds-status-text">Processing payment...</span>
                </div>
            `;
            
            // Simulate API call delay
            setTimeout(() => {
                // Mark payment as completed in sessionStorage
                sessionStorage.setItem('paymentCompleted', 'true');
                
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator success">
                        <span class="cds-status-icon">✓</span>
                        <span class="cds-status-text">Payment successful! Redirecting...</span>
                    </div>
                `;
                
                // Redirect to results page (which will now show all results)
                setTimeout(() => {
                    window.location.hash = '#/results';
                }, 1500);
            }, 2000);
        });
    }
}

// Escape HTML to prevent XSS
function escapeHtml(s) {
    return String(s ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
}

// Expose renderPaymentPage for routing
window.renderPaymentPage = renderPaymentPage;
console.log('[PaymentPage] renderPaymentPage function exposed to window');


