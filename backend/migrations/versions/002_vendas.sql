CREATE TABLE IF NOT EXISTS lotes (
    id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT NOT NULL, nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL, quantidade INT NOT NULL, taxa_percentual DECIMAL(5,2) NOT NULL DEFAULT 10,
    inicio DATETIME(6) NOT NULL, fim DATETIME(6) NOT NULL, ativo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (evento_id) REFERENCES eventos(id), INDEX (evento_id, inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS assentos (
    id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT NOT NULL, setor VARCHAR(80) NOT NULL,
    fila VARCHAR(10) NOT NULL, numero INT NOT NULL,
    UNIQUE (evento_id, fila, numero), FOREIGN KEY (evento_id) REFERENCES eventos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS documentos_meia (
    id INT AUTO_INCREMENT PRIMARY KEY, usuario_id INT NOT NULL, tipo VARCHAR(40) NOT NULL,
    nome_arquivo VARCHAR(150) NOT NULL, mime VARCHAR(40) NOT NULL, conteudo MEDIUMBLOB NOT NULL,
    validade DATE NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    observacao VARCHAR(300), criado_em DATETIME(6) NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id), INDEX (usuario_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY, usuario_id INT NOT NULL, evento_id INT NOT NULL,
    lote_id INT NOT NULL, assento_id INT, quantidade INT NOT NULL, tipo VARCHAR(20) NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL, taxa_total DECIMAL(10,2) NOT NULL, total DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'reservada', expira_em DATETIME(6) NOT NULL,
    criado_em DATETIME(6) NOT NULL, FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id), FOREIGN KEY (lote_id) REFERENCES lotes(id),
    FOREIGN KEY (assento_id) REFERENCES assentos(id), INDEX (lote_id, status, expira_em),
    INDEX (assento_id, status), INDEX (usuario_id, criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY, reserva_id INT NOT NULL UNIQUE,
    valor DECIMAL(10,2) NOT NULL, status VARCHAR(20) NOT NULL, provedor VARCHAR(40) NOT NULL,
    referencia VARCHAR(100) NOT NULL UNIQUE, criado_em DATETIME(6) NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS ingressos (
    id INT AUTO_INCREMENT PRIMARY KEY, reserva_id INT NOT NULL, usuario_id INT NOT NULL,
    evento_id INT NOT NULL, assento_id INT, codigo VARCHAR(100) NOT NULL UNIQUE,
    utilizado_em DATETIME(6), criado_em DATETIME(6) NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id), FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id), FOREIGN KEY (assento_id) REFERENCES assentos(id),
    INDEX (usuario_id, evento_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS grupos (
    id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT NOT NULL, criador_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL, codigo VARCHAR(24) NOT NULL UNIQUE, criado_em DATETIME(6) NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES eventos(id), FOREIGN KEY (criador_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS grupo_membros (
    grupo_id INT NOT NULL, usuario_id INT NOT NULL, PRIMARY KEY (grupo_id, usuario_id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS alertas (
    id INT AUTO_INCREMENT PRIMARY KEY, usuario_id INT NOT NULL, evento_id INT NOT NULL,
    lote_id INT, tipo VARCHAR(20) NOT NULL, agendado_em DATETIME(6) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'agendado', lido BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em DATETIME(6) NOT NULL, FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id), FOREIGN KEY (lote_id) REFERENCES lotes(id),
    INDEX (status, agendado_em), INDEX (usuario_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS cofre_dados (
    usuario_id INT PRIMARY KEY, conteudo TEXT NOT NULL, atualizado_em DATETIME(6) NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY, usuario_id INT NOT NULL, acao VARCHAR(100) NOT NULL,
    criado_em DATETIME(6) NOT NULL, FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    INDEX (usuario_id, criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
