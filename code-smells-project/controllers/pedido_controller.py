import logging
from config.settings import Config
from middlewares.error_handler import ValidationError

logger = logging.getLogger(__name__)


class PedidoController:
    def __init__(self, db):
        from models.pedido_model import PedidoModel
        from models.produto_model import ProdutoModel
        self.pedido_model = PedidoModel(db)
        self.produto_model = ProdutoModel(db)

    def criar(self, usuario_id, itens):
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")
        if not itens or len(itens) == 0:
            raise ValidationError("Pedido deve ter pelo menos 1 item")

        # Batch fetch products — no N+1
        produto_ids = [item["produto_id"] for item in itens]
        produtos = self.produto_model.get_by_ids(produto_ids)

        # Validate and calculate total
        total = 0
        itens_com_preco = []
        for item in itens:
            pid = item["produto_id"]
            if pid not in produtos:
                raise ValidationError(f"Produto {pid} não encontrado")
            produto = produtos[pid]
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            total += produto["preco"] * item["quantidade"]
            itens_com_preco.append({
                "produto_id": pid,
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            })

        # Single transaction for order + items + stock update
        pedido_id = self.pedido_model.create_pedido_completo(usuario_id, itens_com_preco, total)

        logger.info("Pedido criado: id=%s, usuario=%s", pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self):
        return self.pedido_model.get_all()

    def listar_por_usuario(self, usuario_id):
        return self.pedido_model.get_by_usuario(usuario_id)

    def atualizar_status(self, pedido_id, novo_status):
        if novo_status not in Config.STATUS_PEDIDO_VALIDOS:
            raise ValidationError("Status inválido")
        self.pedido_model.update_status(pedido_id, novo_status)

        if novo_status == "aprovado":
            logger.info("Pedido %s aprovado — preparar envio", pedido_id)
        elif novo_status == "cancelado":
            logger.info("Pedido %s cancelado — devolver estoque", pedido_id)

        return True

    def relatorio_vendas(self):
        # Model returns raw data — controller applies business rules
        resumo = self.pedido_model.get_resumo_vendas()
        faturamento = resumo["faturamento"]
        total_pedidos = resumo["total_pedidos"]

        # Discount tiers — business logic in controller, not model
        desconto = 0
        for limite, taxa in Config.DESCONTO_TIERS:
            if faturamento > limite:
                desconto = faturamento * taxa
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": resumo["pedidos_pendentes"],
            "pedidos_aprovados": resumo["pedidos_aprovados"],
            "pedidos_cancelados": resumo["pedidos_cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
