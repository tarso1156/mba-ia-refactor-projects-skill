import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from config.settings import Config

logger = logging.getLogger(__name__)


def generate_token(usuario):
    payload = {
        "user_id": usuario["id"],
        "tipo": usuario["tipo"],
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"erro": "Token requerido", "sucesso": False}), 401
        try:
            payload = decode_token(token)
            from database import get_db
            from models.usuario_model import UsuarioModel
            db = get_db()
            g.current_user = UsuarioModel(db).get_by_id(payload["user_id"])
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado", "sucesso": False}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido", "sucesso": False}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        if not g.current_user or g.current_user.get("tipo") != "admin":
            return jsonify({"erro": "Acesso restrito a admins", "sucesso": False}), 403
        return f(*args, **kwargs)
    return decorated
