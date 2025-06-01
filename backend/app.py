import os
import stripe
from flask import jsonify, request

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        plan_type = data.get('planType')
        
        # Define prices based on plan type
        prices = {
            'monthly': {
                'price_id': os.getenv('STRIPE_MONTHLY_PRICE_ID'),
                'amount': 999,  # $9.99
            },
            'annual': {
                'price_id': os.getenv('STRIPE_ANNUAL_PRICE_ID'),
                'amount': 9588,  # $95.88
            }
        }
        
        if plan_type not in prices:
            return jsonify({'error': 'Invalid plan type'}), 400
            
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': prices[plan_type]['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'payment/cancelled',
        )
        
        return jsonify({'sessionId': session.id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 