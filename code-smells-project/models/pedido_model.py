class PedidoModel:
    def __init__(self, db):
        self.db = db

    def create_pedido_completo(self, usuario_id, itens_com_preco, total):
        cursor = self.db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens_com_preco:
            self.db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            self.db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        self.db.commit()
        return pedido_id

    def update_status(self, pedido_id, status):
        self.db.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (status, pedido_id),
        )
        self.db.commit()
        return True

    def get_by_usuario(self, usuario_id):
        return self._get_pedidos("WHERE p.usuario_id = ?", (usuario_id,))

    def get_all(self):
        return self._get_pedidos("")

    def get_resumo_vendas(self):
        cursor = self.db.execute(
            "SELECT COUNT(*) as total_pedidos, COALESCE(SUM(total), 0) as faturamento FROM pedidos"
        )
        row = cursor.fetchone()
        total_pedidos = row["total_pedidos"]
        faturamento = row["faturamento"]

        pendentes = self._count_by_status("pendente")
        aprovados = self._count_by_status("aprovado")
        cancelados = self._count_by_status("cancelado")

        return {
            "total_pedidos": total_pedidos,
            "faturamento": faturamento,
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
        }

    def _count_by_status(self, status):
        cursor = self.db.execute(
            "SELECT COUNT(*) as cnt FROM pedidos WHERE status = ?", (status,)
        )
        return cursor.fetchone()["cnt"]

    def _get_pedidos(self, where_clause="", params=()):
        query = """
            SELECT p.id as pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                   ip.id as item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   pr.nome as produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
        """
        if where_clause:
            query += " " + where_clause
        query += " ORDER BY p.id"

        cursor = self.db.execute(query, params)
        rows = cursor.fetchall()

        pedidos = {}
        for row in rows:
            pid = row["pedido_id"]
            if pid not in pedidos:
                pedidos[pid] = {
                    "id": row["pedido_id"],
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                }
            if row["item_id"]:
                pedidos[pid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                })

        return list(pedidos.values())
