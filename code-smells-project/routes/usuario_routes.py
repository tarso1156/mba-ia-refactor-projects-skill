from flask import Blueprint, request
from controllers.usuario_controller import UsuarioController
from services.auth_service import generate_token
from database import get_db

usuario_bp = Blueprint("usuarios", __name__)


def _controller():
    return UsuarioController(get_db())


@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = _controller().listar_todos()
    return {"dados": usuarios, "sucesso": True}, 200


@usuario_bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    usuario = _controller().buscar_por_id(usuario_id)
    return {"dados": usuario, "sucesso": True}, 200


@usuario_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    usuario_id = _controller().criar(dados)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


@usuario_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return {"erro": "Dados inválidos", "sucesso": False}, 400
    usuario = _controller().login(dados.get("email", ""), dados.get("senha", ""))
    token = generate_token(usuario)
    return {"dados": {"usuario": usuario, "token": token}, "sucesso": True, "mensagem": "Login OK"}, 200
