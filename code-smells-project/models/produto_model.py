class ProdutoModel:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def _serialize(row):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"],
        }

    def get_all(self):
        cursor = self.db.execute("SELECT * FROM produtos")
        return [self._serialize(row) for row in cursor.fetchall()]

    def get_by_id(self, produto_id):
        cursor = self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        )
        row = cursor.fetchone()
        return self._serialize(row) if row else None

    def get_by_ids(self, produto_ids):
        if not produto_ids:
            return {}
        placeholders = ",".join("?" * len(produto_ids))
        cursor = self.db.execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})",
            produto_ids,
        )
        return {row["id"]: self._serialize(row) for row in cursor.fetchall()}

    def create(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.commit()
        return cursor.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        self.db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.commit()
        return True

    def delete(self, produto_id):
        self.db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.commit()
        return True

    def update_estoque(self, produto_id, quantidade):
        self.db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )

    def search(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params.extend([f"%{termo}%", f"%{termo}%"])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        cursor = self.db.execute(query, params)
        return [self._serialize(row) for row in cursor.fetchall()]
