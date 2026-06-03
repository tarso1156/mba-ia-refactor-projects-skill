import logging
from config.settings import Config
from middlewares.error_handler import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, db):
        from models.produto_model import ProdutoModel
        self.model = ProdutoModel(db)

    def listar_todos(self):
        return self.model.get_all()

    def buscar_por_id(self, produto_id):
        produto = self.model.get_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        return produto

    def criar(self, dados):
        self._validar_produto(dados)
        produto_id = self.model.create(
            nome=dados["nome"],
            descricao=dados.get("descricao", ""),
            preco=dados["preco"],
            estoque=dados["estoque"],
            categoria=dados.get("categoria", "geral"),
        )
        logger.info("Produto criado: id=%s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        produto = self.model.get_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        self._validar_produto(dados)
        self.model.update(
            produto_id,
            nome=dados["nome"],
            descricao=dados.get("descricao", ""),
            preco=dados["preco"],
            estoque=dados["estoque"],
            categoria=dados.get("categoria", "geral"),
        )
        logger.info("Produto atualizado: id=%s", produto_id)
        return True

    def deletar(self, produto_id):
        produto = self.model.get_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        self.model.delete(produto_id)
        logger.info("Produto deletado: id=%s", produto_id)
        return True

    def buscar(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        return self.model.search(termo, categoria, preco_min, preco_max)

    def _validar_produto(self, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        if "nome" not in dados:
            raise ValidationError("Nome é obrigatório")
        if "preco" not in dados:
            raise ValidationError("Preço é obrigatório")
        if "estoque" not in dados:
            raise ValidationError("Estoque é obrigatório")

        preco = dados["preco"]
        estoque = dados["estoque"]
        nome = dados["nome"]
        categoria = dados.get("categoria", "geral")

        if not isinstance(preco, (int, float)) or preco < 0:
            raise ValidationError("Preço não pode ser negativo")
        if not isinstance(estoque, (int, float)) or estoque < 0:
            raise ValidationError("Estoque não pode ser negativo")
        if len(nome) < 2:
            raise ValidationError("Nome muito curto")
        if len(nome) > 200:
            raise ValidationError("Nome muito longo")
        if categoria not in Config.CATEGORIAS_VALIDAS:
            raise ValidationError("Categoria inválida. Válidas: " + str(Config.CATEGORIAS_VALIDAS))
