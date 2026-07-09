# app/__init__.py
from flask import Flask, app, jsonify
from app.config import Config
from app.extensions import db, cors
from app.services.firebase_client import init_firebase
from app.routes.teachers import teachers_bp
from app.routes.auth import auth_bp 
from app.routes.students import students_bp
from app.routes.registers import registers_bp

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False  
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(
        app,
        origins=[
            "https://capecomorinschool.com",
            "https://www.capecomorinschool.com",
            "https://capecomorinschool.vercel.app",
            "https://admin.capecomorinschool.com",
            "http://localhost:3000",
        ],
    )

    # Initialize Firebase Admin once at startup — safe even if it fails,
    # since init_firebase() catches its own errors internally and logs a
    # warning instead of crashing the whole app.
    with app.app_context():
        init_firebase()

    from app.routes.calendar import calendar_bp
    from app.routes.notices import notices_bp
   
    app.register_blueprint(auth_bp)  
    app.register_blueprint(calendar_bp)
    app.register_blueprint(notices_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(registers_bp)
    

    @app.get("/")
    def home():
        routes = []
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
            if rule.endpoint == "static":
                continue
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": sorted(list(rule.methods - {"HEAD", "OPTIONS"})),
                    "path": rule.rule,
                }
            )
        return jsonify(
            {
                "name": "Cape Comorin School Backend API",
                "status": "Running",
                "version": "1.0.0",
                "database": "PostgreSQL (Neon)",
                "routes": routes,
            }
        )

    @app.get("/health/firebase")
    def firebase_health():
        from app.services.firebase_client import _firebase_app as fb_app, _init_error as fb_err
        if fb_app is not None:
            return {"status": "ok", "firebase": "initialized"}
        return {"status": "error", "detail": str(fb_err) if fb_err else "not initialized"}, 500

    with app.app_context():
        db.create_all()

    return app