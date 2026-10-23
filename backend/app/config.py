import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', '3307'))
    DB_USER = os.environ.get('DB_USER', 'ingressos_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'ingressos_pass')
    DB_NAME = os.environ.get('DB_NAME', 'ingressos_db')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    MODO_DEMONSTRACAO = os.environ.get('MODO_DEMONSTRACAO', 'true').lower() == 'true'
    COFRE_SECRET_KEY = os.environ.get('COFRE_SECRET_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
    USAR_GEMINI = os.environ.get('USAR_GEMINI', 'false').lower() == 'true'
