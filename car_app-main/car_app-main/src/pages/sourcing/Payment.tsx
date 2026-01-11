import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { QueryResponse } from '../../lib/api';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').trim();

export function SourcingPayment() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [resultCount, setResultCount] = useState(0);
  const [premiumCount, setPremiumCount] = useState(0);
  
  const [cardNumber, setCardNumber] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvv, setCvv] = useState('');
  const [cardName, setCardName] = useState('');

  useEffect(() => {
    // Get results data to know how many results we're unlocking
    const resultsData = sessionStorage.getItem('queryResults');
    if (resultsData) {
      try {
        const data: QueryResponse = JSON.parse(resultsData);
        const count = data.result_count || 0;
        const results = data.results || [];
        setResultCount(count);
        // Calculate premium count: if 2 results, 1 premium; if 3+, count after first 2
        if (results.length === 2) {
          setPremiumCount(1);
        } else if (results.length > 2) {
          setPremiumCount(Math.max(0, results.length - 2));
        } else {
          setPremiumCount(0);
        }
      } catch (e) {
        console.error('Failed to parse results data:', e);
      }
    }
  }, []);

  const formatCardNumber = (value: string) => {
    const digits = value.replace(/\s/g, '').replace(/\D/g, '');
    return digits.match(/.{1,4}/g)?.join(' ') || digits;
  };

  const formatExpiry = (value: string) => {
    const digits = value.replace(/\D/g, '');
    if (digits.length >= 2) {
      return digits.substring(0, 2) + '/' + digits.substring(2, 4);
    }
    return digits;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    const cardDigits = cardNumber.replace(/\s/g, '');
    if (cardDigits.length < 13 || cardDigits.length > 19) {
      toast.error('Please enter a valid card number');
      return;
    }

    if (expiry.length !== 5 || !expiry.match(/^\d{2}\/\d{2}$/)) {
      toast.error('Please enter a valid expiry date (MM/YY)');
      return;
    }

    if (cvv.length < 3 || cvv.length > 4) {
      toast.error('Please enter a valid CVV');
      return;
    }

    if (!cardName.trim()) {
      toast.error('Please enter cardholder name');
      return;
    }

    try {
      setLoading(true);
      toast.loading('Processing payment...', { id: 'payment' });

      // Process payment through Stripe API (using test PaymentMethod ID)
      const response = await fetch(`${API_BASE}/api/payment/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: 999, // $9.99 in cents
          currency: 'usd',
          payment_method: 'pm_card_visa', // Stripe test PaymentMethod ID
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Payment failed');
      }

      // Payment succeeded - update the queryResults data with payment status
      const resultsData = sessionStorage.getItem('queryResults');
      if (resultsData) {
        try {
          const queryData: QueryResponse = JSON.parse(resultsData);
          (queryData as any).paymentCompleted = true;
          sessionStorage.setItem('queryResults', JSON.stringify(queryData));
        } catch (e) {
          console.error('Failed to update payment status:', e);
        }
      }

      toast.success('Payment successful! Redirecting...', { id: 'payment' });
      
      // Redirect to results page (which will now show all results)
      setTimeout(() => {
        navigate('/sourcing/candidates');
      }, 1500);
    } catch (error: any) {
      console.error('Payment error:', error);
      toast.error(`Payment failed: ${error.message}`, { id: 'payment' });
    } finally {
      setLoading(false);
    }
  };

  if (premiumCount === 0) {
    // No premium results to unlock, redirect back
    navigate('/sourcing/candidates');
    return null;
  }

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/sourcing/candidates')}
          className="flex items-center space-x-2 text-brand-gold hover:opacity-80 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Results</span>
        </button>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-8">
          <div className="text-center mb-8">
            <CreditCard className="h-12 w-12 text-brand-gold mx-auto mb-4" />
            <h1 className="text-3xl font-extrabold text-white mb-2">Unlock Full Results</h1>
            <p className="text-gray-400">
              Complete payment to view all {resultCount} search results
            </p>
          </div>

          {/* Payment Summary */}
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <h2 className="text-lg font-semibold text-brand-gold mb-4">Payment Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-400">
                  Unlock {premiumCount} additional result{premiumCount !== 1 ? 's' : ''}
                </span>
                <span className="text-white font-medium">$9.99</span>
              </div>
              <div className="border-t border-gray-700 pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-white font-semibold">Total</span>
                  <span className="text-brand-gold text-xl font-bold">$9.99</span>
                </div>
              </div>
            </div>
          </div>

          {/* Payment Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Payment Information</h3>
              <p className="text-gray-400 text-sm mb-6">
                Secure payment processing via Stripe (sandbox/test mode)
              </p>
            </div>

            <div>
              <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-300 mb-2">
                Card Number
              </label>
              <input
                id="cardNumber"
                type="text"
                value={cardNumber}
                onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                placeholder="4242 4242 4242 4242"
                maxLength={19}
                className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                disabled={loading}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="expiry" className="block text-sm font-medium text-gray-300 mb-2">
                  Expiry Date
                </label>
                <input
                  id="expiry"
                  type="text"
                  value={expiry}
                  onChange={(e) => setExpiry(formatExpiry(e.target.value))}
                  placeholder="MM/YY"
                  maxLength={5}
                  className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  disabled={loading}
                />
              </div>
              <div>
                <label htmlFor="cvv" className="block text-sm font-medium text-gray-300 mb-2">
                  CVV
                </label>
                <input
                  id="cvv"
                  type="text"
                  value={cvv}
                  onChange={(e) => setCvv(e.target.value.replace(/\D/g, ''))}
                  placeholder="123"
                  maxLength={4}
                  className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label htmlFor="cardName" className="block text-sm font-medium text-gray-300 mb-2">
                Cardholder Name
              </label>
              <input
                id="cardName"
                type="text"
                value={cardName}
                onChange={(e) => setCardName(e.target.value)}
                placeholder="John Doe"
                className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-brand-gold text-black font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : 'Pay $9.99'}
            </button>

            <p className="text-gray-500 text-xs text-center">
              Note: For testing, a valid Stripe test card will be used automatically regardless of the entered card details.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

