from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def _to_public(row):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"],
        }

    @staticmethod
    def _to_full(row):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "senha": row["senha"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"],
        }

    def get_all(self):
        cursor = self.db.execute("SELECT * FROM usuarios")
        return [self._to_public(row) for row in cursor.fetchall()]

    def get_by_id(self, usuario_id):
        cursor = self.db.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        )
        row = cursor.fetchone()
        return self._to_public(row) if row else None

    def get_by_email(self, email):
        cursor = self.db.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        )
        row = cursor.fetchone()
        return self._to_full(row) if row else None

    def create(self, nome, email, senha, tipo="cliente"):
        hashed = generate_password_hash(senha)
        cursor = self.db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, hashed, tipo),
        )
        self.db.commit()
        return cursor.lastrowid

    def verify_login(self, email, senha):
        cursor = self.db.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        )
        row = cursor.fetchone()
        if row and check_password_hash(row["senha"], senha):
            return self._to_public(row)
        return None
