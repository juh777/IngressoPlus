from flask import jsonify

def responder_erro(erro):
    return jsonify({'erro': erro.message}), erro.status_code
