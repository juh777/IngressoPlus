class ServiceError(Exception):
    """Erro de regra de negocio, carregando o status HTTP a ser retornado pelo controller."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
