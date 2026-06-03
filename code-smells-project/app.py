import logging
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from database import init_app
from middlewares.error_handler import register_error_handlers
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp


def create_app():
    Config.validate()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    CORS(app)

    # Database
    init_app(app)

    # Error handlers
    register_error_handlers(app)

    # Blueprints (routes)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)

    # Index
    @app.route("/")
    def index():
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }

    # Health check — no sensitive data exposed
    @app.route("/health", methods=["GET"])
    def health_check():
        from database import get_db

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos,
            },
        }, 200

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print(f"Debug: {Config.DEBUG}")
    print("=" * 50)
    app.run(
        host="0.0.0.0" if Config.DEBUG else "127.0.0.1",
        port=5000,
        debug=Config.DEBUG,
    )
