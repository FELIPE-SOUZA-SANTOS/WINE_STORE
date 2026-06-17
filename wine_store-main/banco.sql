CREATE DATABASE wine_store;

USE wine_store;

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    descricao TEXT,
    preco DECIMAL(10,2),
    estoque INT,
    imagem VARCHAR(255)
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20)
);

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2)
);

CREATE TABLE itens_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    produto_id INT,
    quantidade INT,
    subtotal DECIMAL(10,2),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

INSERT INTO produtos(nome, descricao, preco, estoque, imagem)
VALUES
-- Tintos
('Cabernet Sauvignon Reserva', 'Vinho tinto encorpado com notas de frutas vermelhas', 89.90, 20, 'cabernet.jpg'),
('Merlot Premium', 'Vinho tinto macio e equilibrado', 74.90, 15, 'merlot.jpg'),

-- Brancos
('Chardonnay Selection', 'Vinho branco fresco com notas cítricas', 79.90, 18, 'chardonnay.jpg'),
('Sauvignon Blanc', 'Vinho branco leve e aromático', 69.90, 12, 'sauvignon_blanc.jpg'),

-- Rosés
('Rosé Provence', 'Vinho rosé delicado com aromas florais', 72.90, 10, 'rose_provence.jpg'),
('Rosé Premium', 'Vinho rosé refrescante com notas de frutas vermelhas', 76.90, 14, 'rose_premium.jpg');

DROP TABLE usuarios;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50),
    senha VARCHAR(50)
);

INSERT INTO usuarios(usuario, senha)
VALUES ('admin', '123456');
INSERT INTO usuarios(usuario, senha)
VALUES ('felipe', '0901');

select * from usuarios;

