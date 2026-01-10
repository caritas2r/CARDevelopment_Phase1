"""
Payment Service - Handles Stripe payment processing
"""
import os
from datetime import datetime
import stripe
from flask import jsonify, request


class PaymentService:
    """Service responsible for processing payments via Stripe"""
    
    def __init__(self):
        """Initialize the payment service"""
        self.name = "payment-service"
        self.initialized = False
        self.stripe_api_key = None
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        @app.route('/api/payment/process', methods=['POST'])
        def process_payment():
            """
            Process a payment through Stripe
            
            Expected request body:
            {
                "amount": 999,  // Amount in cents (e.g., 999 = $9.99)
                "currency": "usd",
                "payment_method": "pm_card_visa"  // Stripe PaymentMethod ID for testing
            }
            
            Returns:
                JSON response with payment result
            """
            try:
                if not self.stripe_api_key:
                    return jsonify({
                        'success': False,
                        'error': 'Stripe API key not configured',
                        'error_type': 'configuration_error'
                    }), 503
                
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing request body',
                        'error_type': 'validation'
                    }), 400
                
                amount = data.get('amount', 999)  # Default $9.99 in cents
                currency = data.get('currency', 'usd')
                payment_method_id = data.get('payment_method')
                
                if not payment_method_id:
                    return jsonify({
                        'success': False,
                        'error': 'Missing payment_method in request body',
                        'error_type': 'validation'
                    }), 400
                
                # Validate payment_method is a string (PaymentMethod ID like "pm_card_visa")
                if not isinstance(payment_method_id, str) or not payment_method_id.strip():
                    return jsonify({
                        'success': False,
                        'error': 'payment_method must be a valid PaymentMethod ID string',
                        'error_type': 'validation'
                    }), 400
                
                # Set Stripe API key
                stripe.api_key = self.stripe_api_key
                
                # Create and confirm PaymentIntent with PaymentMethod ID
                try:
                    # Create PaymentIntent directly with PaymentMethod ID (recommended approach)
                    payment_intent = stripe.PaymentIntent.create(
                        amount=amount,
                        currency=currency,
                        payment_method=payment_method_id,
                        payment_method_types=["card"],
                        confirmation_method='manual',
                        confirm=True
                    )
                    
                    # Check if payment requires additional action
                    if payment_intent.status == 'requires_action':
                        return jsonify({
                            'success': False,
                            'error': 'Payment requires additional authentication',
                            'error_type': 'payment_action_required',
                            'payment_intent': {
                                'id': payment_intent.id,
                                'client_secret': payment_intent.client_secret
                            }
                        }), 402
                    
                    # Check if payment succeeded
                    if payment_intent.status == 'succeeded':
                        return jsonify({
                            'success': True,
                            'message': 'Payment processed successfully',
                            'payment_intent_id': payment_intent.id,
                            'amount': amount,
                            'currency': currency
                        }), 200
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Payment failed with status: {payment_intent.status}',
                            'error_type': 'payment_failed',
                            'status': payment_intent.status
                        }), 402
                    
                except stripe.error.CardError as e:
                    # Card was declined
                    return jsonify({
                        'success': False,
                        'error': e.user_message or 'Your card was declined.',
                        'error_type': 'card_error',
                        'stripe_error': str(e)
                    }), 402
                    
                except stripe.error.RateLimitError as e:
                    # Too many requests - Stripe test mode has very high limits, so this is unlikely
                    # But we handle it gracefully
                    return jsonify({
                        'success': False,
                        'error': 'Payment service temporarily unavailable. Please try again in a moment.',
                        'error_type': 'rate_limit_error',
                        'stripe_error': 'Rate limit exceeded'
                    }), 429
                    
                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters
                    return jsonify({
                        'success': False,
                        'error': 'Invalid payment information',
                        'error_type': 'invalid_request',
                        'stripe_error': str(e)
                    }), 400
                    
                except stripe.error.AuthenticationError as e:
                    # Authentication failed (invalid API key)
                    return jsonify({
                        'success': False,
                        'error': 'Payment service authentication failed',
                        'error_type': 'authentication_error'
                    }), 500
                    
                except stripe.error.StripeError as e:
                    # Generic Stripe error
                    return jsonify({
                        'success': False,
                        'error': 'Payment processing error',
                        'error_type': 'stripe_error',
                        'stripe_error': str(e)
                    }), 500
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_type': 'internal_error'
                }), 500
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            
            # Get Stripe API key from environment variable
            self.stripe_api_key = os.getenv("STRIPE_API_KEY", "").strip()
            
            if not self.stripe_api_key:
                print(f"[{self.name}] WARNING: STRIPE_API_KEY environment variable not set")
                print(f"[{self.name}] Payment processing will be disabled")
                print(f"[{self.name}] Set STRIPE_API_KEY to your Stripe sandbox/test API key to enable payments")
            else:
                print(f"[{self.name}] Stripe API key configured (sandbox/test mode)")
            
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")

