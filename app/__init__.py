from flask import Flask, Response
from .config import Config
from .routes.webhook import webhook_bp
from .routes.subtitle import subtitle_bp
from .routes.hot import hot_bp
from .routes.collect import collect_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.register_blueprint(webhook_bp)
    app.register_blueprint(subtitle_bp)
    app.register_blueprint(hot_bp)
    app.register_blueprint(collect_bp)
    
    @app.route("/")
    def index():
        with open("app/templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        return Response(html, content_type="text/html;charset=utf-8")
    
    return app


app = create_app()
