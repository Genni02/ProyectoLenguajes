-- Script completo para base de datos de calculadora con mejores prácticas
-- MySQL 8.0+

-- Crear base de datos
DROP DATABASE IF EXISTS calculadora_db;
CREATE DATABASE calculadora_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE calculadora_db;

-- ===============================
-- TABLAS PRINCIPALES
-- ===============================

-- Tabla usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hash_contrasena VARCHAR(255) NULL,
    avatar_url VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    estado_cuenta ENUM('activo', 'suspendido', 'eliminado') DEFAULT 'activo',
    verificado BOOLEAN DEFAULT FALSE,
    INDEX idx_usuario_estado (estado_cuenta),
    INDEX idx_usuario_email (email)
);

-- Tabla categorias_funciones
CREATE TABLE categorias_funciones (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    icono VARCHAR(100),
    color_hex VARCHAR(7) DEFAULT '#007bff',
    orden_visualizacion INT DEFAULT 0,
    es_sistema BOOLEAN DEFAULT TRUE COMMENT 'Categorías del sistema vs. personalizadas',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla historial_calculos
CREATE TABLE historial_calculos (
    id_calculo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    expresion TEXT NOT NULL,
    resultado VARCHAR(255) NOT NULL,
    tipo_calculo ENUM('basico', 'cientifico', 'matriz', 'grafico') DEFAULT 'basico',
    timestamp_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    es_favorito BOOLEAN DEFAULT FALSE,
    etiquetas JSON COMMENT 'Tags para categorizar cálculos',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_historial_usuario_timestamp (id_usuario, timestamp_calculo DESC),
    INDEX idx_historial_favoritos (id_usuario, es_favorito, timestamp_calculo DESC),
    INDEX idx_historial_tipo (tipo_calculo)
);

-- Tabla variables_usuario
CREATE TABLE variables_usuario (
    id_variable INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_variable VARCHAR(50) NOT NULL,
    valor_variable VARCHAR(255) NOT NULL,
    tipo_valor ENUM('numero', 'texto', 'matriz', 'complejo') DEFAULT 'numero',
    descripcion TEXT,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    UNIQUE KEY uk_usuario_nombre_variable (id_usuario, nombre_variable),
    INDEX idx_variables_nombre (nombre_variable)
);

-- Tabla funciones_personalizadas mejorada
CREATE TABLE funciones_personalizadas (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_categoria INT,
    nombre_funcion VARCHAR(50) NOT NULL,
    definicion_funcion TEXT NOT NULL,
    parametros_funcion VARCHAR(255) COMMENT 'Ej: "x", "x,y"',
    descripcion TEXT,
    ejemplos_uso TEXT,
    es_publica BOOLEAN DEFAULT FALSE,
    veces_usada INT DEFAULT 0,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias_funciones(id_categoria) ON DELETE SET NULL,
    UNIQUE KEY uk_usuario_nombre_funcion (id_usuario, nombre_funcion),
    INDEX idx_funciones_busqueda (nombre_funcion, id_usuario),
    INDEX idx_funciones_categoria (id_categoria),
    INDEX idx_funciones_publicas (es_publica)
);

-- Tabla constantes_publicas
CREATE TABLE constantes_publicas (
    id_constante INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_categoria INT,
    nombre_constante VARCHAR(50) NOT NULL,
    valor_constante DECIMAL(30, 15) NOT NULL,
    unidad_constante VARCHAR(50) NULL,
    descripcion TEXT,
    fuente_referencia VARCHAR(255),
    es_publica BOOLEAN DEFAULT FALSE,
    veces_usada INT DEFAULT 0,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias_funciones(id_categoria) ON DELETE SET NULL,
    UNIQUE KEY uk_usuario_nombre_constante (id_usuario, nombre_constante),
    INDEX idx_constantes_categoria (id_categoria)
);

-- Tabla operaciones_guardadas
CREATE TABLE operaciones_guardadas (
    id_operacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    operacion TEXT NOT NULL,
    descripcion TEXT NULL,
    tags JSON NULL,
    es_favorito BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    tipo_operacion ENUM('expression', 'sequence', 'template') DEFAULT 'expression',
    metadata JSON NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_operacion_usuario (id_usuario),
    INDEX idx_operacion_favorito (id_usuario, es_favorito),
    INDEX idx_operacion_tipo (tipo_operacion),
    INDEX idx_operacion_fecha (fecha_modificacion),
    FULLTEXT INDEX idx_operacion_busqueda (titulo, descripcion, operacion)
);

-- Tabla favoritos
CREATE TABLE favoritos (
    id_favorito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_favorito ENUM('calculo', 'funcion', 'constante', 'operacion') NOT NULL,
    id_referencia INT NOT NULL,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    UNIQUE KEY uk_usuario_tipo_referencia (id_usuario, tipo_favorito, id_referencia)
);

-- ===============================
-- INSERTAR DATOS INICIALES
-- ===============================

-- Categorías de funciones del sistema
INSERT INTO categorias_funciones (nombre_categoria, descripcion, icono, color_hex, orden_visualizacion, es_sistema) VALUES
('Básicas', 'Operaciones aritméticas fundamentales', '🔢', '#007bff', 1, TRUE),
('Trigonométricas', 'Funciones trigonométricas y sus inversas', '📐', '#28a745', 2, TRUE),
('Logarítmicas', 'Logaritmos naturales y en base 10', '📊', '#ffc107', 3, TRUE),
('Exponenciales', 'Potencias y raíces', '⚡', '#dc3545', 4, TRUE),
('Hiperbólicas', 'Funciones hiperbólicas', '〰️', '#6f42c1', 5, TRUE),
('Estadísticas', 'Funciones estadísticas y probabilidad', '📈', '#20c997', 6, TRUE),
('Físicas', 'Constantes y fórmulas físicas', '⚛️', '#fd7e14', 7, TRUE),
('Matemáticas', 'Constantes matemáticas importantes', '🧮', '#6610f2', 8, TRUE),
('Personalizadas', 'Funciones definidas por el usuario', '👤', '#6c757d', 10, FALSE);

-- Usuario de ejemplo
INSERT INTO usuarios (nombre_usuario, email, estado_cuenta, verificado) VALUES
('admin', 'admin@calculadora.com', 'activo', TRUE),
('demo', 'demo@calculadora.com', 'activo', TRUE);

-- Constantes matemáticas predefinidas
INSERT INTO constantes_publicas (id_usuario, id_categoria, nombre_constante, valor_constante, descripcion, es_publica) VALUES
(1, 8, 'pi', 3.141592653589793, 'Número pi (π)', TRUE),
(1, 8, 'e', 2.718281828459045, 'Número de Euler (e)', TRUE),
(1, 8, 'phi', 1.618033988749895, 'Número áureo (φ)', TRUE),
(1, 7, 'c', 299792458.0, 'Velocidad de la luz en el vacío (m/s)', TRUE),
(1, 7, 'g', 9.80665, 'Aceleración de la gravedad estándar (m/s²)', TRUE),
(1, 7, 'h', 6.62607015e-34, 'Constante de Planck (J⋅s)', TRUE),
(1, 7, 'k_B', 1.380649e-23, 'Constante de Boltzmann (J/K)', TRUE);

ALTER TABLE operaciones_guardadas 
MODIFY COLUMN tipo_operacion ENUM('expression', 'sequence', 'template', 'basico', 'trigonometrica', 'logaritmica', 'matriz', 'variable', 'calculo') DEFAULT 'expression';

-- Mensaje final de éxito
SELECT 'Base de datos de calculadora creada exitosamente con mejores prácticas aplicadas' AS resultado;
SELECT CONCAT('Total de categorías: ', COUNT(*)) AS categorias_creadas FROM categorias_funciones;