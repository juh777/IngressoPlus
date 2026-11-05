"""Persistência do cofre, auditoria e exportação dos dados da própria conta."""
from app.extensions import consultar, executar


def registrar_acao(usuario_id, acao, agora):
    executar('INSERT INTO auditoria (usuario_id, acao, criado_em) VALUES (%s, %s, %s)', (usuario_id, acao, agora))


def ler_cofre(usuario_id):
    return consultar('SELECT conteudo FROM cofre_dados WHERE usuario_id = %s', (usuario_id,), apenas_um=True)


def excluir_cofre(usuario_id):
    executar('DELETE FROM cofre_dados WHERE usuario_id = %s', (usuario_id,))


def salvar_cofre(usuario_id, conteudo, agora):
    executar('''INSERT INTO cofre_dados (usuario_id, conteudo, atualizado_em) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE conteudo = VALUES(conteudo), atualizado_em = VALUES(atualizado_em)''',
             (usuario_id, conteudo, agora))


def exportar_dados(usuario_id):
    return {
        'reservas': consultar('SELECT * FROM reservas WHERE usuario_id = %s', (usuario_id,)),
        'ingressos': consultar('SELECT * FROM ingressos WHERE usuario_id = %s', (usuario_id,)),
        'pagamentos': consultar('''SELECT p.* FROM pagamentos p JOIN reservas r ON r.id = p.reserva_id
                                  WHERE r.usuario_id = %s''', (usuario_id,)),
        'documentos': consultar('''SELECT id, tipo, nome_arquivo, validade, status, observacao
                                  FROM documentos_meia WHERE usuario_id = %s''', (usuario_id,)),
        'alertas': consultar('SELECT * FROM alertas WHERE usuario_id = %s', (usuario_id,)),
        'grupos': consultar('''SELECT g.id, g.nome, g.evento_id FROM grupos g JOIN grupo_membros m
                              ON m.grupo_id = g.id WHERE m.usuario_id = %s''', (usuario_id,)),
        'historico': consultar('SELECT acao, criado_em FROM auditoria WHERE usuario_id = %s ORDER BY id DESC',
                              (usuario_id,)),
    }
