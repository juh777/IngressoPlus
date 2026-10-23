CREATE PROCEDURE obter_mapa_assentos(IN p_evento_id INT)
SELECT a.id, a.setor, a.fila, a.numero,
    CASE WHEN EXISTS (
        SELECT 1 FROM reservas r WHERE r.assento_id = a.id
        AND (r.status = 'paga' OR (r.status = 'reservada' AND r.expira_em > UTC_TIMESTAMP(6)))
    ) THEN 'ocupado' ELSE 'disponivel' END AS status
FROM assentos a WHERE a.evento_id = p_evento_id ORDER BY a.fila, a.numero
