import sqlalchemy_libsql

from flask import Flask
from app.config import Config
from app.extensions import db, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    cors.init_app(app, origins=[
        "https://capecomorinschool.com",
        "https://www.capecomorinschool.com",
        "https://capecomorinschool.vercel.app",
        "https://admin.capecomorinschool.com",
        "http://localhost:3000",
    ])

    from app.routes.calendar import calendar_bp
    from app.routes.notices import notices_bp
    from app.routes.fees import fees_bp

    app.register_blueprint(calendar_bp)
    app.register_blueprint(notices_bp)
    app.register_blueprint(fees_bp)

    with app.app_context():
        db.create_all()

    return app