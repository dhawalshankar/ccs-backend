# app/routes/fees.py
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.fee_transaction import FeeTransaction
from app.services.razorpay_client import create_order, verify_payment_signature
from app.services.require_admin import require_admin, require_role

fees_bp = Blueprint("fees", __name__, url_prefix="/api/fees")

@fees_bp.post("/create-order")
def create_fee_order():
    data = request.get_json()
    student_id = data.get("student_digital_id")
    amount = data.get("amount")

    if not student_id or not amount:
        return jsonify({"error": "student_digital_id and amount are required"}), 400

    order, amount_paise = create_order(float(amount), receipt=f"ccs-{student_id}")

    txn = FeeTransaction(
        student_digital_id=student_id,
        amount_paise=amount_paise,
        razorpay_order_id=order["id"],
        status="created",
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": current_app.config["RAZORPAY_KEY_ID"],
    })

@fees_bp.post("/verify")
def verify_fee_payment():
    data = request.get_json()
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    txn = FeeTransaction.query.filter_by(razorpay_order_id=order_id).first_or_404()

    if verify_payment_signature(order_id, payment_id, signature):
        txn.status = "paid"
        txn.razorpay_payment_id = payment_id
        db.session.commit()
        return jsonify({"status": "paid"})
    else:
        txn.status = "failed"
        db.session.commit()
        return jsonify({"status": "failed"}), 400

@fees_bp.get("")
@require_admin
@require_role("super_admin")
def list_transactions():
    txns = FeeTransaction.query.order_by(FeeTransaction.created_at.desc()).all()
    return jsonify([t.to_dict() for t in txns])