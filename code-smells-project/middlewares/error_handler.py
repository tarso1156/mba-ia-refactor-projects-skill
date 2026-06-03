import logging
from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(AppError):
    def __init__(self, message):
        super().__init__(message, 404)


class UnauthorizedError(AppError):
    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    def __init__(self, message="Acesso restrito"):
        super().__init__(message, 403)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"erro": e.message, "sucesso": False}), e.status_code

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        logger.error("Internal error: %s", e, exc_info=True)
        return jsonify({"erro": "Internal server error", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error("Unhandled exception: %s", e, exc_info=True)
        return jsonify({"erro": "Internal server error", "sucesso": False}), 500
