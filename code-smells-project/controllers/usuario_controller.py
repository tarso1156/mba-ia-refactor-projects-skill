import logging
from middlewares.error_handler import ValidationError, NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, db):
        from models.usuario_model import UsuarioModel
        self.model = UsuarioModel(db)

    def listar_todos(self):
        return self.model.get_all()

    def buscar_por_id(self, usuario_id):
        usuario = self.model.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuário não encontrado")
        return usuario

    def criar(self, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise ValidationError("Nome, email e senha são obrigatórios")
        usuario_id = self.model.create(nome, email, senha)
        logger.info("Usuário criado: id=%s", usuario_id)
        return usuario_id

    def login(self, email, senha):
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")
        usuario = self.model.verify_login(email, senha)
        if not usuario:
            raise UnauthorizedError("Email ou senha inválidos")
        logger.info("Login bem-sucedido: id=%s", usuario["id"])
        return usuario
