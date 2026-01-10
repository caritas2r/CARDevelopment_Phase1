// Payment Page - Stripe payment processing for unlocking results
const API_BASE_URL = 'http://localhost:5000';

// Test cards cache (loaded once)
let testCardsCache = null;

// Load test cards from sample_cards.json
async function loadTestCards() {
    if (testCardsCache) {
        return testCardsCache;
    }
    
    try {
        const response = await fetch('/sample_cards.json');
        if (!response.ok) {
            throw new Error('Failed to load test cards');
        }
        testCardsCache = await response.json();
        return testCardsCache;
    } catch (error) {
        console.error('Error loading test cards:', error);
        // Fallback to a default test card
        testCardsCache = [{
            brand: "Visa",
            number: "4242424242424242",
            cvc: "123",
            exp_month: 12,
            exp_year: 2025
        }];
        return testCardsCache;
    }
}

// Get a random test card from the list
async function getRandomTestCard() {
    const cards = await loadTestCards();
    const randomIndex = Math.floor(Math.random() * cards.length);
    return cards[randomIndex];
}

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
                        <p class="payment-note">Secure payment processing via Stripe (sandbox/test mode)</p>
                        <p class="payment-note" style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">
                            Note: For testing, a valid Stripe test card will be used automatically regardless of the entered card details.
                        </p>
                        
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
                        
                        <div id="debugCardInfo" class="debug-card-info" style="display: none; margin-top: 1rem; padding: 0.75rem; background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; font-size: 0.875rem;">
                            <strong>Card details being sent to Stripe:</strong>
                            <div id="debugCardDetails" style="margin-top: 0.5rem; font-family: monospace; color: #333;"></div>
                        </div>
                        
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
    
    // Format expiry date (MM/YY) - improved to allow full editing including backspace
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            const cursorPos = e.target.selectionStart;
            let value = e.target.value.replace(/\D/g, ''); // Remove all non-digits
            
            // Limit to 4 digits
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            
            // Format as MM/YY
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            
            e.target.value = value;
            
            // Adjust cursor position - if we added a slash, move cursor forward
            let newCursorPos = cursorPos;
            if (value.length > 0 && value.includes('/')) {
                // If cursor was at position 2 (after first 2 digits), move it past the slash
                if (cursorPos === 2 && value.length > 2) {
                    newCursorPos = 3;
                }
                // If we just typed a digit and it created a slash, move past it
                else if (value.length === 3 && cursorPos === 2) {
                    newCursorPos = 3;
                }
            }
            
            // Set cursor position
            setTimeout(() => {
                e.target.setSelectionRange(newCursorPos, newCursorPos);
            }, 0);
        });
        
        // Handle backspace to allow deleting through the slash
        expiryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace') {
                const cursorPos = e.target.selectionStart;
                const value = e.target.value;
                
                // If cursor is right after the slash, delete the slash and the digit before it
                if (cursorPos === 3 && value.length > 0 && value[2] === '/') {
                    e.preventDefault();
                    let digits = value.replace(/\D/g, '');
                    if (digits.length > 0) {
                        digits = digits.substring(0, digits.length - 1);
                        if (digits.length >= 2) {
                            e.target.value = digits.substring(0, 2) + '/' + digits.substring(2, 4);
                            e.target.setSelectionRange(2, 2); // Position cursor before where slash was
                        } else {
                            e.target.value = digits;
                            e.target.setSelectionRange(digits.length, digits.length);
                        }
                    }
                }
            }
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
        submitButton.addEventListener('click', async () => {
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
            
            // Process payment through Stripe API
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';
            statusDiv.innerHTML = `
                <div class="cds-status-indicator loading">
                    <span class="cds-status-icon">⏳</span>
                    <span class="cds-status-text">Processing payment...</span>
                </div>
            `;
            
            // Parse expiry date (MM/YY format) with validation
            const expiryParts = expiry.split('/');
            if (expiryParts.length !== 2 || !expiryParts[0] || !expiryParts[1]) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Invalid expiry date format</span>
                    </div>
                `;
                submitButton.disabled = false;
                submitButton.textContent = 'Pay $9.99';
                return;
            }
            
            const expMonth = expiryParts[0].trim();
            const expYear = expiryParts[1].trim();
            
            // Validate month (1-12)
            const monthInt = parseInt(expMonth, 10);
            if (isNaN(monthInt) || monthInt < 1 || monthInt > 12) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Invalid expiry month (must be 01-12)</span>
                    </div>
                `;
                submitButton.disabled = false;
                submitButton.textContent = 'Pay $9.99';
                return;
            }
            
            // Validate year (should be 2 digits)
            if (expYear.length !== 2 || isNaN(parseInt(expYear, 10))) {
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Invalid expiry year format (must be YY)</span>
                    </div>
                `;
                submitButton.disabled = false;
                submitButton.textContent = 'Pay $9.99';
                return;
            }
            
            // Prepare payment data using Stripe PaymentMethod ID (recommended approach)
            // Using pm_card_visa test PaymentMethod ID
            const paymentMethodId = 'pm_card_visa';
            
            const paymentData = {
                amount: 999, // $9.99 in cents
                currency: 'usd',
                payment_method: paymentMethodId  // Stripe test PaymentMethod ID
            };
            
            // Display payment method details being sent (for debugging)
            const debugCardInfo = document.getElementById('debugCardInfo');
            const debugCardDetails = document.getElementById('debugCardDetails');
            if (debugCardInfo && debugCardDetails) {
                debugCardDetails.innerHTML = `
                    <div><strong>Payment Method ID:</strong> ${paymentMethodId}</div>
                    <div><strong>Amount:</strong> $9.99 (999 cents)</div>
                    <div><strong>Currency:</strong> USD</div>
                    <div><strong>Cardholder Name (from form):</strong> ${cardName.trim() || 'Test User'}</div>
                    <div style="margin-top: 0.5rem; font-size: 0.8125rem; color: #666;">
                        Note: Using Stripe test PaymentMethod ID (pm_card_visa) - this simulates a successful Visa payment.
                    </div>
                `;
                debugCardInfo.style.display = 'block';
            }
            
            // Call backend payment API
            fetch(`${API_BASE_URL}/api/payment/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(paymentData)
            })
            .then(async response => {
                // Check HTTP status before parsing JSON
                let result;
                try {
                    result = await response.json();
                } catch (e) {
                    // If JSON parsing fails, create error response
                    throw new Error(`Server error: HTTP ${response.status} ${response.statusText}`);
                }
                
                // Check if response indicates failure (non-2xx status or success:false)
                if (!response.ok || !result.success) {
                    const errorMsg = result.error || `Payment failed (HTTP ${response.status})`;
                    throw new Error(errorMsg);
                }
                
                return result;
            })
            .then(result => {
                // Payment succeeded
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
            })
            .catch(error => {
                console.error('Payment processing error:', error);
                statusDiv.innerHTML = `
                    <div class="cds-status-indicator error">
                        <span class="cds-status-icon">✕</span>
                        <span class="cds-status-text">Payment failed</span>
                    </div>
                    <div class="cds-status-details error">
                        <p><strong>Error:</strong> ${escapeHtml(error.message || 'Failed to process payment. Please try again.')}</p>
                    </div>
                `;
                submitButton.disabled = false;
                submitButton.textContent = 'Pay $9.99';
            });
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


