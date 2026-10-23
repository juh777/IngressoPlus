import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from flask import current_app

from app.extensions import consultar
from app.services.conta_service import ler_cofre
from app.utils.vendas import agora


def recomendar(usuario_id):
    eventos = consultar('SELECT id, nome, categoria, `local`, data_hora_evento FROM eventos WHERE ativo = TRUE AND data_hora_evento > %s ORDER BY data_hora_evento', (agora(),))
    historico = consultar('''SELECT e.categoria, COUNT(*) AS total FROM reservas r JOIN eventos e ON e.id = r.evento_id
                            WHERE r.usuario_id = %s AND r.status = 'paga' GROUP BY e.categoria''', (usuario_id,))
    preferencias = ler_cofre(usuario_id).get('preferencias', '').casefold()
    gostos = {linha['categoria']: linha['total'] for linha in historico}
    for evento in eventos:
        categoria = evento['categoria'] or ''
        evento['pontos'] = gostos.get(categoria, 0) + (3 if categoria and categoria.casefold() in preferencias else 0)
        evento['motivo'] = 'Combina com suas preferências ou compras.' if evento['pontos'] else 'Evento disponível para você conhecer.'
    eventos.sort(key=lambda item: (-item['pontos'], item['data_hora_evento']))
    # Sem credenciais, a recomendação local continua útil e é identificada como tal.
    if not current_app.config['USAR_GEMINI'] or not current_app.config['GEMINI_API_KEY']:
        return {'origem': 'recomendação local por preferências e histórico', 'eventos': eventos[:6]}
    try:
        catalogo = [{'id': e['id'], 'nome': e['nome'], 'categoria': e['categoria']} for e in eventos]
        prompt = 'Ordene até 6 IDs de eventos deste catálogo. Responda somente um array JSON de inteiros. Catálogo: ' + json.dumps(catalogo, ensure_ascii=False)
        prompt += '. Categorias de interesse: ' + ', '.join(str(chave) for chave in gostos if chave)
        corpo = json.dumps({'contents': [{'parts': [{'text': prompt}]}]}).encode()
        modelo = current_app.config['GEMINI_MODEL']
        if not modelo.replace('-', '').replace('.', '').isalnum():
            raise ValueError('Modelo inválido')
        requisicao = Request('https://generativelanguage.googleapis.com/v1beta/models/' + modelo + ':generateContent',
                             data=corpo, headers={'Content-Type': 'application/json', 'x-goog-api-key': current_app.config['GEMINI_API_KEY']})
        with urlopen(requisicao, timeout=10) as resposta:
            resultado = json.load(resposta)
        texto = resultado['candidates'][0]['content']['parts'][0]['text'].strip().removeprefix('```json').removesuffix('```').strip()
        ids = json.loads(texto)
        if not isinstance(ids, list) or not all(isinstance(item, int) for item in ids):
            raise ValueError('Resposta inválida')
        por_id = {evento['id']: evento for evento in eventos}
        escolhidos = [por_id[item] for item in dict.fromkeys(ids) if item in por_id][:6]
        return {'origem': 'Gemini', 'eventos': escolhidos or eventos[:6]}
    except (URLError, ValueError, KeyError, IndexError, TimeoutError, TypeError, AttributeError):
        return {'origem': 'recomendação local (IA indisponível)', 'eventos': eventos[:6]}
