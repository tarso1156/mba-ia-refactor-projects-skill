import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'loja.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')

    # Business constants
    CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
    STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

    LIMITE_DESCONTO_PLATINA = 10_000
    LIMITE_DESCONTO_OURO = 5_000
    LIMITE_DESCONTO_PRATA = 1_000
    TAXA_DESCONTO_PLATINA = 0.10
    TAXA_DESCONTO_OURO = 0.05
    TAXA_DESCONTO_PRATA = 0.02
    DESCONTO_TIERS = [
        (LIMITE_DESCONTO_PLATINA, TAXA_DESCONTO_PLATINA),
        (LIMITE_DESCONTO_OURO, TAXA_DESCONTO_OURO),
        (LIMITE_DESCONTO_PRATA, TAXA_DESCONTO_PRATA),
    ]

    JWT_EXPIRATION_HOURS = 24

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            env = os.environ.get('FLASK_ENV', 'development')
            if env == 'production':
                raise RuntimeError("SECRET_KEY environment variable is required in production")
            cls.SECRET_KEY = 'dev-key-change-in-prod'
