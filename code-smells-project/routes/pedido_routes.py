from flask import Blueprint, request
from controllers.pedido_controller import PedidoController
from database import get_db

pedido_bp = Blueprint("pedidos", __name__)


def _controller():
    return PedidoController(get_db())


@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    if not dados:
        return {"erro": "Dados inválidos", "sucesso": False}, 400
    resultado = _controller().criar(
        usuario_id=dados.get("usuario_id"),
        itens=dados.get("itens", []),
    )
    return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


@pedido_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    pedidos = _controller().listar_todos()
    return {"dados": pedidos, "sucesso": True}, 200


@pedido_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = _controller().listar_por_usuario(usuario_id)
    return {"dados": pedidos, "sucesso": True}, 200


@pedido_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    if not dados or "status" not in dados:
        return {"erro": "Status é obrigatório", "sucesso": False}, 400
    _controller().atualizar_status(pedido_id, dados["status"])
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


@pedido_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = _controller().relatorio_vendas()
    return {"dados": relatorio, "sucesso": True}, 200
