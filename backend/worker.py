"""Processa notificações internas e expira reservas, sem enviar e-mails externos."""
import time
from app import create_app
from app.services.alerta_service import processar_alertas
from app.services.reserva_service import expirar_reservas

app = create_app()
while True:
    try:
        with app.app_context():
            processar_alertas()
            expirar_reservas()
    except Exception:
        app.logger.exception('Falha ao processar agendamentos; nova tentativa em 10 segundos.')
    time.sleep(10)
