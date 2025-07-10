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

-- Tabla tipos_unidades para conversiones con algoritmos
CREATE TABLE tipos_unidades (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    icono VARCHAR(100),
    algoritmo_conversion ENUM('lineal', 'logaritmico', 'potencia', 'custom') DEFAULT 'lineal',
    precision_decimal TINYINT DEFAULT 10,
    requiere_conversion_especial BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tipo_algoritmo (algoritmo_conversion)
);

-- Tabla para handlers de conversiones especiales
CREATE TABLE conversion_handlers (
    id_handler INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo INT NOT NULL,
    nombre_handler VARCHAR(50) NOT NULL,
    clase_conversion VARCHAR(100) NOT NULL COMMENT 'Nombre de la clase/función que maneja la conversión',
    configuracion JSON COMMENT 'Configuración específica del handler',
    version VARCHAR(10) DEFAULT '1.0',
    es_activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo) REFERENCES tipos_unidades(id_tipo) ON DELETE CASCADE,
    UNIQUE KEY uk_tipo_handler (id_tipo, nombre_handler)
);

-- Tabla unidades_medida optimizada
CREATE TABLE unidades_medida (
    id_unidad INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo INT NOT NULL,
    nombre_unidad VARCHAR(50) NOT NULL,
    simbolo VARCHAR(20) NOT NULL,
    -- Para conversiones lineales normales
    factor_conversion DECIMAL(45, 20) NULL,
    offset_conversion DECIMAL(45, 20) DEFAULT 0 COMMENT 'Para temperatura principalmente',
    -- Para conversiones especiales (datos, etc.)
    conversion_metadata JSON COMMENT 'Metadatos para conversiones complejas',
    es_unidad_base BOOLEAN DEFAULT FALSE,
    es_activa BOOLEAN DEFAULT TRUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tipo) REFERENCES tipos_unidades(id_tipo) ON DELETE CASCADE,
    UNIQUE KEY uk_tipo_simbolo (id_tipo, simbolo),
    INDEX idx_unidad_tipo_activa (id_tipo, es_activa),
    INDEX idx_unidad_base (id_tipo, es_unidad_base)
);

-- Tabla configuraciones_usuario
CREATE TABLE configuraciones_usuario (
    id_configuracion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    modo_angulo ENUM('grados', 'radianes', 'gradianes') DEFAULT 'grados',
    decimales_mostrar INT DEFAULT 2,
    tema_interfaz VARCHAR(50) DEFAULT 'default',
    notacion_cientifica BOOLEAN DEFAULT FALSE,
    historial_maximo INT DEFAULT 1000,
    autoguardado_sesion BOOLEAN DEFAULT TRUE,
    sonidos_activados BOOLEAN DEFAULT TRUE,
    idioma VARCHAR(10) DEFAULT 'es',
    formato_fecha VARCHAR(20) DEFAULT 'DD/MM/YYYY',
    mostrar_conversiones BOOLEAN DEFAULT TRUE,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- Tabla historial_calculos
CREATE TABLE historial_calculos (
    id_calculo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    expresion TEXT NOT NULL,
    resultado VARCHAR(255) NOT NULL,
    tipo_calculo ENUM('basico', 'cientifico', 'conversion', 'matriz', 'grafico') DEFAULT 'basico',
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

-- Tabla constantes_usuario
CREATE TABLE constantes_usuario (
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

-- ===============================
-- TABLAS PARA CONVERSIONES
-- ===============================

-- Tabla historial_conversiones
CREATE TABLE historial_conversiones (
    id_conversion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_tipo_unidad INT NOT NULL,
    valor_origen DECIMAL(30, 15) NOT NULL,
    id_unidad_origen INT NOT NULL,
    valor_destino DECIMAL(30, 15) NOT NULL,
    id_unidad_destino INT NOT NULL,
    expresion_completa TEXT,
    timestamp_conversion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    es_favorito BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_tipo_unidad) REFERENCES tipos_unidades(id_tipo) ON DELETE CASCADE,
    FOREIGN KEY (id_unidad_origen) REFERENCES unidades_medida(id_unidad) ON DELETE CASCADE,
    FOREIGN KEY (id_unidad_destino) REFERENCES unidades_medida(id_unidad) ON DELETE CASCADE,
    INDEX idx_conversion_usuario_tipo (id_usuario, id_tipo_unidad),
    INDEX idx_conversion_timestamp (timestamp_conversion DESC)
);

-- Tabla conversiones_favoritas
CREATE TABLE conversiones_favoritas (
    id_favorito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_tipo_unidad INT NOT NULL,
    id_unidad_origen INT NOT NULL,
    id_unidad_destino INT NOT NULL,
    nombre_favorito VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_tipo_unidad) REFERENCES tipos_unidades(id_tipo) ON DELETE CASCADE,
    FOREIGN KEY (id_unidad_origen) REFERENCES unidades_medida(id_unidad) ON DELETE CASCADE,
    FOREIGN KEY (id_unidad_destino) REFERENCES unidades_medida(id_unidad) ON DELETE CASCADE,
    UNIQUE KEY uk_usuario_conversion (id_usuario, id_unidad_origen, id_unidad_destino)
);

-- Tabla sesiones_guardadas
CREATE TABLE sesiones_guardadas (
    id_sesion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_sesion VARCHAR(100) NOT NULL,
    estado_calculadora_json JSON NULL,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_sesion_usuario_nombre (id_usuario, nombre_sesion)
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
('Conversiones', 'Factores de conversión de unidades', '🔄', '#17a2b8', 9, TRUE),
('Personalizadas', 'Funciones definidas por el usuario', '👤', '#6c757d', 10, FALSE);

-- Tipos de unidades con algoritmos específicos
INSERT INTO tipos_unidades (nombre_tipo, descripcion, icono, algoritmo_conversion, precision_decimal, requiere_conversion_especial) VALUES
('Longitud', 'Medidas de distancia y longitud', '📏', 'lineal', 10, FALSE),
('Masa', 'Medidas de peso y masa', '⚖️', 'lineal', 10, FALSE),
('Tiempo', 'Medidas temporales', '⏰', 'lineal', 10, FALSE),
('Temperatura', 'Escalas de temperatura', '🌡️', 'custom', 6, TRUE),
('Área', 'Medidas de superficie', '⬜', 'lineal', 10, FALSE),
('Volumen', 'Medidas de capacidad y volumen', '🧊', 'lineal', 10, FALSE),
('Velocidad', 'Medidas de velocidad', '🏃', 'lineal', 8, FALSE),
('Energía', 'Medidas de energía y trabajo', '⚡', 'lineal', 8, FALSE),
('Potencia', 'Medidas de potencia', '💪', 'lineal', 8, FALSE),
('Presión', 'Medidas de presión', '💨', 'lineal', 8, FALSE),
('Ángulo', 'Medidas angulares', '📐', 'lineal', 10, FALSE),
('Datos', 'Almacenamiento de información digital', '💾', 'potencia', 6, TRUE);

-- Handlers para conversiones especiales
INSERT INTO conversion_handlers (id_tipo, nombre_handler, clase_conversion, configuracion) VALUES
(4, 'TemperatureConverter', 'TemperatureHandler', '{"supports_all_scales": true, "precision": 6}'),
(12, 'DataConverter', 'DataSizeHandler', '{"binary_base": 1024, "decimal_base": 1000, "max_precision": 6}');

-- ===============================
-- UNIDADES CON CONVERSIONES LINEALES
-- ===============================

-- Unidades de Longitud (base: metro)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(1, 'Metro', 'm', 1.0, TRUE, TRUE),
(1, 'Kilómetro', 'km', 1000.0, FALSE, TRUE),
(1, 'Centímetro', 'cm', 0.01, FALSE, TRUE),
(1, 'Milímetro', 'mm', 0.001, FALSE, TRUE),
(1, 'Micrómetro', 'μm', 0.000001, FALSE, TRUE),
(1, 'Nanómetro', 'nm', 0.000000001, FALSE, TRUE),
(1, 'Pulgada', 'in', 0.0254, FALSE, TRUE),
(1, 'Pie', 'ft', 0.3048, FALSE, TRUE),
(1, 'Yarda', 'yd', 0.9144, FALSE, TRUE),
(1, 'Milla', 'mi', 1609.344, FALSE, TRUE),
(1, 'Milla náutica', 'nmi', 1852.0, FALSE, TRUE),
(1, 'Año luz', 'ly', 9460730472580800.0, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Masa (base: kilogramo)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(2, 'Kilogramo', 'kg', 1.0, TRUE, TRUE),
(2, 'Gramo', 'g', 0.001, FALSE, TRUE),
(2, 'Miligramo', 'mg', 0.000001, FALSE, TRUE),
(2, 'Tonelada métrica', 't', 1000.0, FALSE, TRUE),
(2, 'Libra', 'lb', 0.45359237, FALSE, TRUE),
(2, 'Onza', 'oz', 0.028349523125, FALSE, TRUE),
(2, 'Stone', 'st', 6.35029318, FALSE, TRUE),
(2, 'Tonelada corta', 'ton US', 907.18474, FALSE, TRUE),
(2, 'Tonelada larga', 'ton UK', 1016.0469088, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Tiempo (base: segundo)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(3, 'Segundo', 's', 1.0, TRUE, TRUE),
(3, 'Milisegundo', 'ms', 0.001, FALSE, TRUE),
(3, 'Microsegundo', 'μs', 0.000001, FALSE, TRUE),
(3, 'Nanosegundo', 'ns', 0.000000001, FALSE, TRUE),
(3, 'Minuto', 'min', 60.0, FALSE, TRUE),
(3, 'Hora', 'h', 3600.0, FALSE, TRUE),
(3, 'Día', 'd', 86400.0, FALSE, TRUE),
(3, 'Semana', 'sem', 604800.0, FALSE, TRUE),
(3, 'Mes', 'mes', 2629746.0, FALSE, TRUE),
(3, 'Año', 'año', 31556952.0, FALSE, TRUE),
(3, 'Década', 'década', 315569520.0, FALSE, TRUE),
(3, 'Siglo', 'siglo', 3155695200.0, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Área (base: metro cuadrado)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(5, 'Metro cuadrado', 'm²', 1.0, TRUE, TRUE),
(5, 'Kilómetro cuadrado', 'km²', 1000000.0, FALSE, TRUE),
(5, 'Centímetro cuadrado', 'cm²', 0.0001, FALSE, TRUE),
(5, 'Milímetro cuadrado', 'mm²', 0.000001, FALSE, TRUE),
(5, 'Hectárea', 'ha', 10000.0, FALSE, TRUE),
(5, 'Acre', 'ac', 4046.8564224, FALSE, TRUE),
(5, 'Pie cuadrado', 'ft²', 0.09290304, FALSE, TRUE),
(5, 'Pulgada cuadrada', 'in²', 0.00064516, FALSE, TRUE),
(5, 'Yarda cuadrada', 'yd²', 0.83612736, FALSE, TRUE),
(5, 'Milla cuadrada', 'mi²', 2589988.110336, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Volumen (base: metro cúbico)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(6, 'Metro cúbico', 'm³', 1.0, TRUE, TRUE),
(6, 'Litro', 'L', 0.001, FALSE, TRUE),
(6, 'Mililitro', 'mL', 0.000001, FALSE, TRUE),
(6, 'Centímetro cúbico', 'cm³', 0.000001, FALSE, TRUE),
(6, 'Kilolitro', 'kL', 1.0, FALSE, TRUE),
(6, 'Galón estadounidense', 'gal US', 0.003785411784, FALSE, TRUE),
(6, 'Galón imperial', 'gal UK', 0.00454609, FALSE, TRUE),
(6, 'Cuarto estadounidense', 'qt US', 0.000946352946, FALSE, TRUE),
(6, 'Pinta estadounidense', 'pt US', 0.000473176473, FALSE, TRUE),
(6, 'Onza fluida estadounidense', 'fl oz US', 0.0000295735, FALSE, TRUE),
(6, 'Taza', 'cup', 0.000236588, FALSE, TRUE),
(6, 'Cucharada', 'tbsp', 0.00001478676, FALSE, TRUE),
(6, 'Cucharadita', 'tsp', 0.00000492892, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Velocidad (base: metro por segundo)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(7, 'Metro por segundo', 'm/s', 1.0, TRUE, TRUE),
(7, 'Kilómetro por hora', 'km/h', 0.277778, FALSE, TRUE),
(7, 'Milla por hora', 'mph', 0.44704, FALSE, TRUE),
(7, 'Pie por segundo', 'ft/s', 0.3048, FALSE, TRUE),
(7, 'Nudo', 'kn', 0.514444, FALSE, TRUE),
(7, 'Mach', 'Ma', 343.0, FALSE, TRUE),
(7, 'Velocidad de la luz', 'c', 299792458.0, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Energía (base: julio)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(8, 'Julio', 'J', 1.0, TRUE, TRUE),
(8, 'Kilojulio', 'kJ', 1000.0, FALSE, TRUE),
(8, 'Megajulio', 'MJ', 1000000.0, FALSE, TRUE),
(8, 'Kilovatio hora', 'kWh', 3600000.0, FALSE, TRUE),
(8, 'Caloría', 'cal', 4.184, FALSE, TRUE),
(8, 'Kilocaloría', 'kcal', 4184.0, FALSE, TRUE),
(8, 'BTU', 'BTU', 1055.06, FALSE, TRUE),
(8, 'Pie-libra', 'ft⋅lbf', 1.3558179483314004, FALSE, TRUE),
(8, 'Electronvoltio', 'eV', 1.602176634e-19, FALSE, TRUE),
(8, 'Erg', 'erg', 1e-7, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Potencia (base: vatio)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(9, 'Vatio', 'W', 1.0, TRUE, TRUE),
(9, 'Kilovatio', 'kW', 1000.0, FALSE, TRUE),
(9, 'Megavatio', 'MW', 1000000.0, FALSE, TRUE),
(9, 'Gigavatio', 'GW', 1000000000.0, FALSE, TRUE),
(9, 'Caballo de fuerza', 'hp', 745.7, FALSE, TRUE),
(9, 'Caballo de vapor', 'CV', 735.49875, FALSE, TRUE),
(9, 'BTU por hora', 'BTU/h', 0.29307107, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Presión (base: pascal)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(10, 'Pascal', 'Pa', 1.0, TRUE, TRUE),
(10, 'Kilopascal', 'kPa', 1000.0, FALSE, TRUE),
(10, 'Megapascal', 'MPa', 1000000.0, FALSE, TRUE),
(10, 'Bar', 'bar', 100000.0, FALSE, TRUE),
(10, 'Milibar', 'mbar', 100.0, FALSE, TRUE),
(10, 'Atmósfera', 'atm', 101325.0, FALSE, TRUE),
(10, 'Torr', 'Torr', 133.322368, FALSE, TRUE),
(10, 'mmHg', 'mmHg', 133.322368, FALSE, TRUE),
(10, 'PSI', 'psi', 6894.757293168, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Ángulo (base: radián)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, factor_conversion, es_unidad_base, es_activa) VALUES
(11, 'Radián', 'rad', 1.0, TRUE, TRUE),
(11, 'Grado', '°', 0.0174532925, FALSE, TRUE),
(11, 'Minuto de arco', "'", 0.0002908882, FALSE, TRUE),
(11, 'Segundo de arco', '"', 0.0000048481, FALSE, TRUE),
(11, 'Gradián', 'gon', 0.0157079633, FALSE, TRUE),
(11, 'Vuelta completa', 'rev', 6.2831853072, FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- ===============================
-- UNIDADES CON CONVERSIONES ESPECIALES
-- ===============================

-- Unidades de Temperatura (usando metadatos)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, conversion_metadata, es_unidad_base, es_activa) VALUES
(4, 'Kelvin', 'K', '{"escala": "K"}', TRUE, TRUE),
(4, 'Celsius', '°C', '{"escala": "C"}', FALSE, TRUE),
(4, 'Fahrenheit', '°F', '{"escala": "F"}', FALSE, TRUE),
(4, 'Rankine', '°R', '{"escala": "R"}', FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- Unidades de Datos (usando potencias)
INSERT INTO unidades_medida (id_tipo, nombre_unidad, simbolo, conversion_metadata, es_unidad_base, es_activa) VALUES
(12, 'Bit', 'bit', '{"potencia": -3, "base_decimal": false}', FALSE, TRUE),
(12, 'Byte', 'B', '{"potencia": 0, "base_decimal": false}', TRUE, TRUE),
(12, 'Kilobyte', 'KB', '{"potencia": 1, "base_decimal": false}', FALSE, TRUE),
(12, 'Megabyte', 'MB', '{"potencia": 2, "base_decimal": false}', FALSE, TRUE),
(12, 'Gigabyte', 'GB', '{"potencia": 3, "base_decimal": false}', FALSE, TRUE),
(12, 'Terabyte', 'TB', '{"potencia": 4, "base_decimal": false}', FALSE, TRUE),
(12, 'Petabyte', 'PB', '{"potencia": 5, "base_decimal": false}', FALSE, TRUE),
(12, 'Exabyte', 'EB', '{"potencia": 6, "base_decimal": false}', FALSE, TRUE),
-- Unidades decimales (base 1000)
(12, 'Kilobyte decimal', 'kB', '{"potencia": 1, "base_decimal": true}', FALSE, TRUE),
(12, 'Megabyte decimal', 'MB dec', '{"potencia": 2, "base_decimal": true}', FALSE, TRUE),
(12, 'Gigabyte decimal', 'GB dec', '{"potencia": 3, "base_decimal": true}', FALSE, TRUE)
ON DUPLICATE KEY UPDATE 
    simbolo = unidades_medida.simbolo;

-- ===============================
-- FUNCIONES DE CONVERSIÓN
-- ===============================

DELIMITER //

-- Función para conversión de datos usando potencias
CREATE FUNCTION ConvertirDatosPotencia(
    p_valor DECIMAL(25,10),
    p_metadata_origen JSON,
    p_metadata_destino JSON
) RETURNS DECIMAL(25,10)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_potencia_origen, v_potencia_destino INT;
    DECLARE v_base_origen, v_base_destino INT DEFAULT 1024;
    DECLARE v_diferencia INT;
    DECLARE v_valor_bits DECIMAL(25,10);
    
    SET v_potencia_origen = JSON_UNQUOTE(JSON_EXTRACT(p_metadata_origen, '$.potencia'));
    SET v_potencia_destino = JSON_UNQUOTE(JSON_EXTRACT(p_metadata_destino, '$.potencia'));
    
    -- Verificar bases (1024 vs 1000)
    IF JSON_UNQUOTE(JSON_EXTRACT(p_metadata_origen, '$.base_decimal')) = 'true' THEN
        SET v_base_origen = 1000;
    END IF;
    
    IF JSON_UNQUOTE(JSON_EXTRACT(p_metadata_destino, '$.base_decimal')) = 'true' THEN
        SET v_base_destino = 1000;
    END IF;
    
    -- Convertir todo a bits primero
    IF v_potencia_origen = -3 THEN
        SET v_valor_bits = p_valor; -- Ya son bits
    ELSE
        SET v_valor_bits = p_valor * POWER(v_base_origen, v_potencia_origen) * 8;
    END IF;
    
    -- Convertir de bits a unidad destino
    IF v_potencia_destino = -3 THEN
        RETURN v_valor_bits; -- Devolver bits
    ELSE
        RETURN v_valor_bits / (POWER(v_base_destino, v_potencia_destino) * 8);
    END IF;
END //

-- Función para conversión de temperatura
CREATE FUNCTION ConvertirTemperatura(
    p_valor DECIMAL(25,10),
    p_metadata_origen JSON,
    p_metadata_destino JSON
) RETURNS DECIMAL(25,10)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_escala_origen, v_escala_destino VARCHAR(10);
    DECLARE v_kelvin DECIMAL(25,10);
    
    SET v_escala_origen = JSON_UNQUOTE(JSON_EXTRACT(p_metadata_origen, '$.escala'));
    SET v_escala_destino = JSON_UNQUOTE(JSON_EXTRACT(p_metadata_destino, '$.escala'));
    
    -- Primero convertir a Kelvin
    CASE v_escala_origen
        WHEN 'C' THEN SET v_kelvin = p_valor + 273.15;
        WHEN 'F' THEN SET v_kelvin = (p_valor - 32) * 5/9 + 273.15;
        WHEN 'R' THEN SET v_kelvin = p_valor * 5/9;
        ELSE SET v_kelvin = p_valor; -- Ya es Kelvin
    END CASE;
    
    -- Luego convertir de Kelvin a destino
    CASE v_escala_destino
        WHEN 'C' THEN RETURN v_kelvin - 273.15;
        WHEN 'F' THEN RETURN (v_kelvin - 273.15) * 9/5 + 32;
        WHEN 'R' THEN RETURN v_kelvin * 9/5;
        ELSE RETURN v_kelvin; -- Mantener Kelvin
    END CASE;
END //

-- Función principal de conversión universal
CREATE FUNCTION ConvertirUnidadUniversal(
    p_valor DECIMAL(25,10),
    p_id_unidad_origen INT,
    p_id_unidad_destino INT
) RETURNS DECIMAL(25,10)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_tipo_conversion VARCHAR(20);
    DECLARE v_factor_origen, v_factor_destino, v_offset_origen, v_offset_destino DECIMAL(25,10);
    DECLARE v_metadata_origen, v_metadata_destino JSON;
    DECLARE v_resultado DECIMAL(25,10);
    DECLARE v_valor_base DECIMAL(25,10);
    
    -- Obtener información de las unidades
    SELECT 
        tu.algoritmo_conversion,
        uo.factor_conversion, uo.offset_conversion, uo.conversion_metadata,
        ud.factor_conversion, ud.offset_conversion, ud.conversion_metadata
    INTO 
        v_tipo_conversion,
        v_factor_origen, v_offset_origen, v_metadata_origen,
        v_factor_destino, v_offset_destino, v_metadata_destino
    FROM unidades_medida uo
    JOIN tipos_unidades tu ON uo.id_tipo = tu.id_tipo
    JOIN unidades_medida ud ON tu.id_tipo = ud.id_tipo
    WHERE uo.id_unidad = p_id_unidad_origen 
    AND ud.id_unidad = p_id_unidad_destino
    AND uo.es_activa = TRUE AND ud.es_activa = TRUE;
    
    -- Aplicar algoritmo según el tipo
    CASE v_tipo_conversion
        WHEN 'lineal' THEN
            -- Conversión lineal estándar
            SET v_valor_base = (p_valor + IFNULL(v_offset_origen, 0)) * IFNULL(v_factor_origen, 1);
            SET v_resultado = (v_valor_base / IFNULL(v_factor_destino, 1)) - IFNULL(v_offset_destino, 0);
            
        WHEN 'potencia' THEN
            -- Para unidades de datos usando potencias
            SET v_resultado = ConvertirDatosPotencia(p_valor, v_metadata_origen, v_metadata_destino);
            
        WHEN 'custom' THEN
            -- Para casos especiales como temperatura
            SET v_resultado = ConvertirTemperatura(p_valor, v_metadata_origen, v_metadata_destino);
            
        ELSE
            SET v_resultado = p_valor; -- Sin conversión
    END CASE;
    
    RETURN v_resultado;
END //

DELIMITER ;

-- ===============================
-- PROCEDIMIENTOS ALMACENADOS
-- ===============================

DELIMITER //

-- Procedimiento principal para realizar conversiones
CREATE PROCEDURE RealizarConversion(
    IN p_id_usuario INT,
    IN p_valor DECIMAL(25,10),
    IN p_id_unidad_origen INT,
    IN p_id_unidad_destino INT,
    OUT p_valor_resultado DECIMAL(25,10),
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_tipo_origen, v_tipo_destino INT;
    DECLARE v_algoritmo VARCHAR(20);
    DECLARE v_nombre_origen, v_nombre_destino, v_simbolo_origen, v_simbolo_destino VARCHAR(50);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            p_mensaje = MESSAGE_TEXT;
        SET p_valor_resultado = NULL;
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    -- Validar que las unidades existan y sean del mismo tipo
    SELECT 
        u1.id_tipo, u2.id_tipo, t.algoritmo_conversion,
        u1.nombre_unidad, u1.simbolo, u2.nombre_unidad, u2.simbolo
    INTO 
        v_tipo_origen, v_tipo_destino, v_algoritmo,
        v_nombre_origen, v_simbolo_origen, v_nombre_destino, v_simbolo_destino
    FROM unidades_medida u1
    JOIN unidades_medida u2 ON u1.id_tipo = u2.id_tipo
    JOIN tipos_unidades t ON u1.id_tipo = t.id_tipo
    WHERE u1.id_unidad = p_id_unidad_origen 
    AND u2.id_unidad = p_id_unidad_destino
    AND u1.es_activa = TRUE AND u2.es_activa = TRUE;
    
    IF v_tipo_origen IS NULL OR v_tipo_destino IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Una o ambas unidades no existen o están inactivas';
    END IF;
    
    IF v_tipo_origen != v_tipo_destino THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Las unidades deben ser del mismo tipo';
    END IF;
    
    -- Realizar conversión
    SET p_valor_resultado = ConvertirUnidadUniversal(p_valor, p_id_unidad_origen, p_id_unidad_destino);
    
    -- Registrar en historial
    INSERT INTO historial_conversiones (
        id_usuario, id_tipo_unidad, valor_origen, id_unidad_origen,
        valor_destino, id_unidad_destino, 
        expresion_completa, timestamp_conversion
    ) VALUES (
        p_id_usuario, v_tipo_origen, p_valor, p_id_unidad_origen,
        p_valor_resultado, p_id_unidad_destino,
        CONCAT(p_valor, ' ', v_simbolo_origen, ' = ', p_valor_resultado, ' ', v_simbolo_destino),
        NOW()
    );
    
    SET p_mensaje = CONCAT('Conversión exitosa: ', p_valor, ' ', v_simbolo_origen, ' = ', p_valor_resultado, ' ', v_simbolo_destino);
    COMMIT;
    
END //

DELIMITER ;

-- ===============================
-- VISTAS ÚTILES
-- ===============================

-- Vista completa de conversiones con información detallada
CREATE VIEW vista_conversiones_completa AS
SELECT 
    hc.id_conversion,
    u.nombre_usuario,
    tu.nombre_tipo,
    tu.algoritmo_conversion,
    hc.valor_origen,
    uo.nombre_unidad as unidad_origen,
    uo.simbolo as simbolo_origen,
    hc.valor_destino,
    ud.nombre_unidad as unidad_destino,
    ud.simbolo as simbolo_destino,
    hc.expresion_completa,
    hc.timestamp_conversion,
    hc.es_favorito,
    ch.clase_conversion as handler_usado
FROM historial_conversiones hc
JOIN usuarios u ON hc.id_usuario = u.id_usuario
JOIN tipos_unidades tu ON hc.id_tipo_unidad = tu.id_tipo
JOIN unidades_medida uo ON hc.id_unidad_origen = uo.id_unidad
JOIN unidades_medida ud ON hc.id_unidad_destino = ud.id_unidad
LEFT JOIN conversion_handlers ch ON tu.id_tipo = ch.id_tipo AND ch.es_activo = TRUE;

-- Vista para funciones categorizadas
CREATE VIEW vista_funciones_categorizadas AS
SELECT 
    fp.id_funcion,
    u.nombre_usuario,
    COALESCE(cf.nombre_categoria, 'Sin categoría') as nombre_categoria,
    COALESCE(cf.color_hex, '#6c757d') as color_hex,
    fp.nombre_funcion,
    fp.definicion_funcion,
    fp.parametros_funcion,
    fp.descripcion,
    fp.ejemplos_uso,
    fp.es_publica,
    fp.veces_usada,
    fp.ultima_modificacion
FROM funciones_personalizadas fp
JOIN usuarios u ON fp.id_usuario = u.id_usuario
LEFT JOIN categorias_funciones cf ON fp.id_categoria = cf.id_categoria;

-- Vista para unidades disponibles por tipo
CREATE VIEW vista_unidades_disponibles AS
SELECT 
    tu.id_tipo,
    tu.nombre_tipo,
    tu.icono as tipo_icono,
    tu.algoritmo_conversion,
    um.id_unidad,
    um.nombre_unidad,
    um.simbolo,
    um.es_unidad_base,
    um.descripcion,
    CASE 
        WHEN um.conversion_metadata IS NOT NULL THEN 'Conversión especial'
        WHEN um.factor_conversion IS NOT NULL THEN CONCAT('Factor: ', um.factor_conversion)
        ELSE 'Sin información'
    END as info_conversion
FROM tipos_unidades tu
JOIN unidades_medida um ON tu.id_tipo = um.id_tipo
WHERE um.es_activa = TRUE
ORDER BY tu.nombre_tipo, um.es_unidad_base DESC, um.nombre_unidad;

-- ===============================
-- DATOS DE EJEMPLO Y CONFIGURACIONES
-- ===============================

-- Usuario de ejemplo
INSERT INTO usuarios (nombre_usuario, email, estado_cuenta, verificado) VALUES
('admin', 'admin@calculadora.com', 'activo', TRUE),
('demo', 'demo@calculadora.com', 'activo', TRUE);

-- Configuraciones por defecto
INSERT INTO configuraciones_usuario (id_usuario, decimales_mostrar, tema_interfaz, idioma) VALUES
(1, 4, 'dark', 'es'),
(2, 2, 'light', 'es');

-- Constantes matemáticas predefinidas
INSERT INTO constantes_usuario (id_usuario, id_categoria, nombre_constante, valor_constante, descripcion, es_publica) VALUES
(1, 8, 'pi', 3.141592653589793, 'Número pi (π)', TRUE),
(1, 8, 'e', 2.718281828459045, 'Número de Euler (e)', TRUE),
(1, 8, 'phi', 1.618033988749895, 'Número áureo (φ)', TRUE),
(1, 7, 'c', 299792458.0, 'Velocidad de la luz en el vacío (m/s)', TRUE),
(1, 7, 'g', 9.80665, 'Aceleración de la gravedad estándar (m/s²)', TRUE),
(1, 7, 'h', 6.62607015e-34, 'Constante de Planck (J⋅s)', TRUE),
(1, 7, 'k_B', 1.380649e-23, 'Constante de Boltzmann (J/K)', TRUE);

-- Mensaje final de éxito
SELECT 'Base de datos de calculadora creada exitosamente con mejores prácticas aplicadas' AS resultado;
SELECT CONCAT('Total de unidades creadas: ', COUNT(*)) AS unidades_creadas FROM unidades_medida;
SELECT CONCAT('Total de tipos de unidades: ', COUNT(*)) AS tipos_creados FROM tipos_unidades;
SELECT CONCAT('Total de categorías: ', COUNT(*)) AS categorias_creadas FROM categorias_funciones;