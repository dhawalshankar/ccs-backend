# app/models/fee_transaction.py
from app.extensions import db
from datetime import datetime

class FeeTransaction(db.Model):
    __tablename__ = "fee_transactions"

    id = db.Column(db.Integer, primary_key=True)
    student_digital_id = db.Column(db.String(50), nullable=False)
    amount_paise = db.Column(db.Integer, nullable=False)
    razorpay_order_id = db.Column(db.String(100), nullable=False)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default="created")  # created / paid / failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "student_digital_id": self.student_digital_id,
            "amount": self.amount_paise / 100,
            "razorpay_order_id": self.razorpay_order_id,
            "razorpay_payment_id": self.razorpay_payment_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }