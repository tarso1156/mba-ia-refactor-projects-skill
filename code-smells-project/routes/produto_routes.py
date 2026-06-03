from flask import Blueprint, request
from controllers.produto_controller import ProdutoController
from database import get_db

produto_bp = Blueprint("produtos", __name__)


def _controller():
    return ProdutoController(get_db())


@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = _controller().listar_todos()
    return {"dados": produtos, "sucesso": True}, 200


@produto_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    try:
        if preco_min:
            preco_min = float(preco_min)
        if preco_max:
            preco_max = float(preco_max)
    except ValueError:
        return {"erro": "preco_min e preco_max devem ser números", "sucesso": False}, 400

    resultados = _controller().buscar(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200


@produto_bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    produto = _controller().buscar_por_id(produto_id)
    return {"dados": produto, "sucesso": True}, 200


@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    produto_id = _controller().criar(dados)
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


@produto_bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados = request.get_json()
    _controller().atualizar(produto_id, dados)
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


@produto_bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    _controller().deletar(produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200
