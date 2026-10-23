from flask import Flask, jsonify, request

from app.config import Config
from app.controllers.base_controller import responder_erro
from app.extensions import configurar_banco, cors
from app.utils.errors import ServiceError

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    configurar_banco(app)
    cors.init_app(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGINS']}}, supports_credentials=True)

    from app.controllers.usuario_controller import usuario_bp
    from app.controllers.evento_controller import evento_bp
    from app.controllers.relatorio_evento_controller import relatorio_evento_bp

    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(evento_bp, url_prefix='/api/eventos')
    app.register_blueprint(relatorio_evento_bp, url_prefix='/api/relatorios')
    app.register_error_handler(ServiceError, responder_erro)
    from app.controllers.conta_controller import conta_bp
    from app.controllers.vendas_controller import vendas_bp
    from app.controllers.comunidade_controller import comunidade_bp
    app.register_blueprint(conta_bp, url_prefix='/api')
    app.register_blueprint(vendas_bp, url_prefix='/api')
    app.register_blueprint(comunidade_bp, url_prefix='/api')
    from app.demo import configurar_demo
    configurar_demo(app)

    @app.before_request
    def conferir_origem():
        origem = request.headers.get('Origin')
        if request.method not in ['GET', 'HEAD', 'OPTIONS'] and origem:
            if origem not in app.config['CORS_ORIGINS'].split(','):
                from app.utils.errors import ServiceError
                raise ServiceError('Origem da requisição não permitida.', 403)

    @app.after_request
    def proteger_resposta(resposta):
        resposta.headers['X-Content-Type-Options'] = 'nosniff'
        if request.path.startswith('/api/'):
            resposta.headers['Cache-Control'] = 'no-store'
        return resposta

    @app.errorhandler(413)
    def arquivo_grande(erro):
        return jsonify({'erro': 'Arquivo muito grande. Envie um comprovante de até 2 MB.'}), 413


    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    return app
