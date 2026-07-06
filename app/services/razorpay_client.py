# app/services/razorpay_client.py
from flask import current_app

def get_client():
    import razorpay  # imported here, not at module load time

    key_id = current_app.config.get("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        raise RuntimeError("Razorpay keys are not configured yet — add them to .env")

    return razorpay.Client(auth=(key_id, key_secret))

def create_order(amount_rupees: float, receipt: str):
    client = get_client()
    amount_paise = int(round(amount_rupees * 100))
    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": receipt,
        "payment_capture": 1,
    })
    return order, amount_paise

def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    client = get_client()
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        return True
    except Exception:
        return False