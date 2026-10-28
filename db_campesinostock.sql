-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 28-10-2026 a las 23:23:55
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_campesinostock`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `telefono` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion`
--

CREATE TABLE `configuracion` (
  `clave` varchar(50) NOT NULL,
  `valor` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `configuracion`
--

INSERT INTO `configuracion` (`clave`, `valor`) VALUES
('codigo_admin_hash', 'pbkdf2_sha256$600000$PNTe7OzZq3ldCbQquDAavd$X3vXKLUnVDlH3SS6pKbEeA7MR0F71Z8SOe5eb5YdXwE=');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_compra`
--

CREATE TABLE `detalle_compra` (
  `id_detalle_compra` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_compra` decimal(10,2) NOT NULL,
  `id_compra` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_venta`
--

CREATE TABLE `detalle_venta` (
  `id_detalle_venta` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_venta` decimal(10,2) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_venta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(7, 'inventario', 'categorias'),
(8, 'inventario', 'clientes'),
(19, 'inventario', 'detallecompra'),
(18, 'inventario', 'detalleventa'),
(9, 'inventario', 'empleados'),
(10, 'inventario', 'metodospago'),
(11, 'inventario', 'motivosmerma'),
(17, 'inventario', 'ordenescompra'),
(20, 'inventario', 'productoproveedo'),
(12, 'inventario', 'productos'),
(13, 'inventario', 'proveedores'),
(16, 'inventario', 'registrosmerma'),
(14, 'inventario', 'ubicaciones'),
(15, 'inventario', 'ventas'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-10-04 19:22:18.470367'),
(2, 'auth', '0001_initial', '2026-10-04 19:22:22.899850'),
(3, 'admin', '0001_initial', '2026-10-04 19:22:23.419937'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-10-04 19:22:23.432755'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-10-04 19:22:23.476257'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-10-04 19:22:23.719771'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-10-04 19:22:23.919908'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-10-04 19:22:23.939888'),
(9, 'auth', '0004_alter_user_username_opts', '2026-10-04 19:22:23.949322'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-10-04 19:22:24.101154'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-10-04 19:22:24.114534'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-10-04 19:22:24.150708'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-10-04 19:22:24.213249'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-10-04 19:22:24.321856'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-10-04 19:22:24.497308'),
(16, 'auth', '0011_update_proxy_permissions', '2026-10-04 19:22:24.512854'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-10-04 19:22:24.540250'),
(18, 'inventario', '0001_initial', '2026-10-04 19:22:28.066462'),
(19, 'sessions', '0001_initial', '2026-10-04 19:22:28.148096');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'Empleado',
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `foto` varchar(255) DEFAULT NULL,
  `ultimo_acceso` datetime(6) DEFAULT NULL,
  `sesion_version` int(11) NOT NULL DEFAULT 0,
  `intentos_fallidos` int(11) NOT NULL DEFAULT 0,
  `bloqueado_hasta` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodos_pago`
--

CREATE TABLE `metodos_pago` (
  `id_metodo_pago` int(11) NOT NULL,
  `nombre_metodo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `motivos_merma`
--

CREATE TABLE `motivos_merma` (
  `id_motivo` int(11) NOT NULL,
  `descripcion` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ordenes_compra`
--

CREATE TABLE `ordenes_compra` (
  `id_compra` int(11) NOT NULL,
  `fecha_compra` datetime(6) NOT NULL,
  `id_proveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(150) NOT NULL,
  `precio_producto` decimal(10,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_ubicacion` int(11) DEFAULT NULL,
  `precio_compra` decimal(10,2) NOT NULL DEFAULT 0.00,
  `stock` int(11) NOT NULL DEFAULT 0,
  `stock_minimo` int(11) NOT NULL DEFAULT 5
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre_producto`, `precio_producto`, `imagen`, `id_categoria`, `id_ubicacion`, `precio_compra`, `stock`, `stock_minimo`) VALUES
(1, 'Tornillo para madera 1/4\" x 2\"', 0.10, NULL, 1, NULL, 0.04, 0, 5),
(2, 'Tornillo para madera 1/4\" x 3\"', 0.12, NULL, 1, NULL, 0.06, 0, 5),
(3, 'Tornillo goloso 10 x 1\"', 0.08, NULL, 1, NULL, 0.03, 0, 5),
(4, 'Tornillo de fijación para lámina 14 x 1\"', 0.10, NULL, 1, NULL, 0.05, 0, 5),
(5, 'Tornillo para drywall 6 x 1\"', 0.05, NULL, 1, NULL, 0.02, 0, 5),
(6, 'Perno hexagonal grado 2 3/8\" x 2\"', 0.35, NULL, 1, NULL, 0.15, 0, 5),
(7, 'Tuerca hexagonal 1/4\"', 0.05, NULL, 1, NULL, 0.02, 0, 5),
(8, 'Tuerca hexagonal 3/8\"', 0.10, NULL, 1, NULL, 0.04, 0, 5),
(9, 'Arandela plana 1/4\"', 0.10, NULL, 1, NULL, 0.02, 0, 5),
(10, 'Arandela de presión 3/8\"', 0.13, NULL, 1, NULL, 0.05, 0, 5),
(11, 'Clavo con cabeza para madera 2\" (libra)', 1.25, NULL, 1, NULL, 0.75, 0, 5),
(12, 'Clavo con cabeza para madera 3\" (libra)', 1.25, NULL, 1, NULL, 0.75, 0, 5),
(13, 'Clavo para concreto 2\" (libra)', 1.75, NULL, 1, NULL, 1.10, 0, 5),
(14, 'Clavo para concreto 3\" (libra)', 1.75, NULL, 1, NULL, 1.10, 0, 5),
(15, 'Taquete / Tarugo plástico 1/4\"', 0.05, NULL, 1, NULL, 0.02, 0, 5),
(16, 'Taquete / Tarugo plástico 3/8\"', 0.10, NULL, 1, NULL, 0.04, 0, 5),
(17, 'Lija para agua N° 80', 0.75, NULL, 2, NULL, 0.35, 0, 5),
(18, 'Lija para agua N° 120', 0.75, NULL, 2, NULL, 0.35, 0, 5),
(19, 'Lija para agua N° 220', 0.75, NULL, 2, NULL, 0.35, 0, 5),
(20, 'Lija para agua N° 400', 0.80, NULL, 2, NULL, 0.40, 0, 5),
(21, 'Lija para madera N° 60', 1.00, NULL, 2, NULL, 0.30, 0, 5),
(22, 'Lija para madera N° 100', 0.60, NULL, 2, NULL, 0.30, 0, 5),
(23, 'Pintura de aceite Rojo Óxido (Galón)', 18.00, NULL, 3, NULL, 12.50, 0, 5),
(24, 'Pintura de aceite Blanco Hueso (Galón)', 19.50, NULL, 3, NULL, 13.00, 0, 5),
(25, 'Pintura de aceite Negro Mate (Galón)', 18.00, NULL, 3, NULL, 12.50, 0, 5),
(26, 'Pintura látex Blanco (Galón)', 14.50, NULL, 3, NULL, 9.50, 0, 5),
(27, 'Pintura látex Azul Colonial (Galón)', 15.50, NULL, 3, NULL, 10.00, 0, 5),
(28, 'Pintura látex Verde Bosque (Galón)', 15.50, NULL, 3, NULL, 10.00, 0, 5),
(29, 'Anti-corrosivo Gris (Galón)', 16.50, NULL, 3, NULL, 11.00, 0, 5),
(30, 'Thinner corriente (Galón)', 8.50, NULL, 3, NULL, 5.50, 0, 5),
(31, 'Solvente Mineral / Aguarrás (Galón)', 9.00, NULL, 3, NULL, 6.00, 0, 5),
(32, 'Brocha para pintura 1\"', 1.00, NULL, 3, NULL, 0.45, 0, 5),
(33, 'Brocha para pintura 2\"', 1.75, NULL, 3, NULL, 0.85, 0, 5),
(34, 'Brocha para pintura 3\"', 2.50, NULL, 3, NULL, 1.25, 0, 5),
(35, 'Rodillo para pintura felpa 9\"', 3.00, NULL, 3, NULL, 1.50, 0, 5),
(36, 'Martillo de uña curva 16 oz', 7.50, NULL, 4, NULL, 4.25, 0, 5),
(37, 'Alicate universal 7\"', 6.00, NULL, 4, NULL, 3.50, 0, 5),
(38, 'Tenaza de presión 10\"', 9.00, NULL, 4, NULL, 5.00, 0, 5),
(39, 'Destornillador plano 1/4\" x 4\"', 2.50, NULL, 4, NULL, 1.20, 0, 5),
(40, 'Destornillador de estrella (Phillips) #2 x 4\"', 2.50, NULL, 4, NULL, 1.20, 0, 5),
(41, 'Llave ajustable (Cinta/Perica) 8\"', 7.50, NULL, 4, NULL, 4.00, 0, 5),
(42, 'Cinta métrica (Flexómetro) 5 metros / 16 pies', 4.00, NULL, 4, NULL, 2.00, 0, 5),
(43, 'Arco de sierra para metal 12\"', 5.50, NULL, 4, NULL, 3.00, 0, 5),
(44, 'Hoja de sierra para metal 18 dientes', 1.25, NULL, 5, NULL, 0.60, 0, 5),
(45, 'Disco de corte para metal 4 1/2\" x 1/16\"', 1.35, NULL, 5, NULL, 0.70, 0, 5),
(46, 'Disco de corte para concreto 4 1/2\"', 4.50, NULL, 5, NULL, 2.50, 0, 5),
(47, 'Broca para concreto 1/4\" x 4\"', 1.75, NULL, 5, NULL, 0.90, 0, 5),
(48, 'Broca para concreto 3/8\" x 6\"', 2.75, NULL, 5, NULL, 1.40, 0, 5),
(49, 'Broca para metal HSS 1/8\"', 1.10, NULL, 5, NULL, 0.50, 0, 5),
(50, 'Broca para metal HSS 1/4\"', 1.80, NULL, 5, NULL, 0.90, 0, 5),
(51, 'Foco LED 9W luz blanca (Rosca E27)', 1.75, NULL, 6, NULL, 0.85, 0, 5),
(52, 'Foco LED 12W luz blanca (Rosca E27)', 2.25, NULL, 6, NULL, 1.10, 0, 5),
(53, 'Foco LED 15W luz cálida (Rosca E27)', 2.75, NULL, 6, NULL, 1.40, 0, 5),
(54, 'Tomacorriente doble polarizado (Blanco)', 2.25, NULL, 6, NULL, 1.10, 0, 5),
(55, 'Interruptor sencillo de pared (Blanco)', 1.85, NULL, 6, NULL, 0.90, 0, 5),
(56, 'Cinta aislante negra 18m (3M o similar)', 1.60, NULL, 6, NULL, 0.80, 0, 5),
(57, 'Socket / Plafón de porcelana E27', 1.00, NULL, 6, NULL, 0.45, 0, 5),
(58, 'Breaker / Cordoncillo 1 polo 20A', 5.00, NULL, 6, NULL, 2.80, 0, 5),
(59, 'Cable eléctrico THHN N° 12 (Metro)', 0.85, NULL, 6, NULL, 0.45, 0, 5),
(60, 'Cable eléctrico THHN N° 14 (Metro)', 0.65, NULL, 6, NULL, 0.32, 0, 5),
(61, 'Tubo PVC agua potable 1/2\" SDR 13.5 (6m)', 3.60, NULL, 7, NULL, 2.00, 0, 5),
(62, 'Tubo PVC agua potable 3/4\" SDR 21 (6m)', 4.80, NULL, 7, NULL, 2.80, 0, 5),
(63, 'Codo PVC 1/2\" a 90° para agua', 0.35, NULL, 7, NULL, 0.15, 0, 5),
(64, 'Te PVC 1/2\" para agua', 0.45, NULL, 7, NULL, 0.20, 0, 5),
(65, 'Pegamento para PVC (Pega PVC) 4 oz', 3.00, NULL, 7, NULL, 1.60, 0, 5),
(66, 'Cinta de teflón 1/2\" x 260\"', 0.60, NULL, 7, NULL, 0.25, 0, 5),
(67, 'Llave de chorro bronce 1/2\"', 6.00, NULL, 7, NULL, 3.20, 0, 5),
(68, 'Silicón transparente uso general 280ml', 4.00, NULL, 7, NULL, 2.20, 0, 5),
(69, 'Cemento CUSCATLÁNEO / HOLCIM (Bolsa 42.5 kg)', 9.25, NULL, 8, NULL, 7.80, 0, 5),
(70, 'Varilla de hierro corrugado 3/8\" (Grade 40 - 6m)', 3.80, NULL, 8, NULL, 2.60, 0, 5),
(71, 'Varilla de hierro corrugado 1/2\" (Grade 40 - 6m)', 6.50, NULL, 8, NULL, 4.60, 0, 5),
(72, 'Alambre de amarre (Libra)', 1.20, NULL, 8, NULL, 0.70, 0, 5),
(73, 'Candado de hierro 40mm', 4.80, NULL, 9, NULL, 2.50, 0, 5),
(74, 'Cuchilla / Exacto universal 18mm', 1.25, NULL, 9, NULL, 0.60, 0, 5),
(75, 'Guantes de lona con puntos de PVC (Par)', 1.50, NULL, 9, NULL, 0.75, 0, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto_proveedo`
--

CREATE TABLE `producto_proveedo` (
  `id` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL,
  `nombre_proveedor` varchar(150) NOT NULL,
  `contacto_proveedor` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedores`
--

INSERT INTO `proveedores` (`id_proveedor`, `nombre_proveedor`, `contacto_proveedor`) VALUES
(1, 'XXXXXXX', '0000-0000');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registos_merma`
--

CREATE TABLE `registos_merma` (
  `id_merma` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `fecha_merma` datetime(6) NOT NULL,
  `id_motivo` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicaciones`
--

CREATE TABLE `ubicaciones` (
  `id_ubicacion` int(11) NOT NULL,
  `pasillo` varchar(50) NOT NULL,
  `estante` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL,
  `fecha_venta` datetime(6) NOT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `id_metodo_pago` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`);

--
-- Indices de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  ADD PRIMARY KEY (`clave`);

--
-- Indices de la tabla `detalle_compra`
--
ALTER TABLE `detalle_compra`
  ADD PRIMARY KEY (`id_detalle_compra`),
  ADD KEY `detalle_compra_id_compra_6f0e9d75_fk_ordenes_compra_id_compra` (`id_compra`),
  ADD KEY `detalle_compra_id_producto_76583d63_fk_productos_id_producto` (`id_producto`);

--
-- Indices de la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  ADD PRIMARY KEY (`id_detalle_venta`),
  ADD KEY `detalle_venta_id_producto_998ddd77_fk_productos_id_producto` (`id_producto`),
  ADD KEY `detalle_venta_id_venta_89bd49dc_fk_ventas_id_venta` (`id_venta`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleado`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- Indices de la tabla `metodos_pago`
--
ALTER TABLE `metodos_pago`
  ADD PRIMARY KEY (`id_metodo_pago`);

--
-- Indices de la tabla `motivos_merma`
--
ALTER TABLE `motivos_merma`
  ADD PRIMARY KEY (`id_motivo`);

--
-- Indices de la tabla `ordenes_compra`
--
ALTER TABLE `ordenes_compra`
  ADD PRIMARY KEY (`id_compra`),
  ADD KEY `ordenes_compra_id_proveedor_0dc1c7e5_fk_proveedores_id_proveedor` (`id_proveedor`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `productos_id_ubicacion_500f9600_fk_ubicaciones_id_ubicacion` (`id_ubicacion`),
  ADD KEY `productos_id_categoria_6ba52eae_fk_categorias_id_categoria` (`id_categoria`);

--
-- Indices de la tabla `producto_proveedo`
--
ALTER TABLE `producto_proveedo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `producto_proveedo_id_producto_id_proveedor_0c4ce294_uniq` (`id_producto`,`id_proveedor`),
  ADD KEY `producto_proveedo_id_proveedor_fb074583_fk_proveedor` (`id_proveedor`);

--
-- Indices de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  ADD PRIMARY KEY (`id_proveedor`);

--
-- Indices de la tabla `registos_merma`
--
ALTER TABLE `registos_merma`
  ADD PRIMARY KEY (`id_merma`),
  ADD KEY `registos_merma_id_motivo_b92dee15_fk_motivos_merma_id_motivo` (`id_motivo`),
  ADD KEY `registos_merma_id_producto_53067f0d_fk_productos_id_producto` (`id_producto`);

--
-- Indices de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  ADD PRIMARY KEY (`id_ubicacion`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`),
  ADD KEY `ventas_id_cliente_e685d518_fk_clientes_id_cliente` (`id_cliente`),
  ADD KEY `ventas_id_empleado_100b8983_fk_empleados_id_empleado` (`id_empleado`),
  ADD KEY `ventas_id_metodo_pago_0b1de702_fk_metodos_pago_id_metodo_pago` (`id_metodo_pago`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_compra`
--
ALTER TABLE `detalle_compra`
  MODIFY `id_detalle_compra` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  MODIFY `id_detalle_venta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `metodos_pago`
--
ALTER TABLE `metodos_pago`
  MODIFY `id_metodo_pago` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `motivos_merma`
--
ALTER TABLE `motivos_merma`
  MODIFY `id_motivo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ordenes_compra`
--
ALTER TABLE `ordenes_compra`
  MODIFY `id_compra` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;

--
-- AUTO_INCREMENT de la tabla `producto_proveedo`
--
ALTER TABLE `producto_proveedo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `registos_merma`
--
ALTER TABLE `registos_merma`
  MODIFY `id_merma` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  MODIFY `id_ubicacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `detalle_compra`
--
ALTER TABLE `detalle_compra`
  ADD CONSTRAINT `detalle_compra_id_compra_6f0e9d75_fk_ordenes_compra_id_compra` FOREIGN KEY (`id_compra`) REFERENCES `ordenes_compra` (`id_compra`),
  ADD CONSTRAINT `detalle_compra_id_producto_76583d63_fk_productos_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  ADD CONSTRAINT `detalle_venta_id_producto_998ddd77_fk_productos_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  ADD CONSTRAINT `detalle_venta_id_venta_89bd49dc_fk_ventas_id_venta` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `ordenes_compra`
--
ALTER TABLE `ordenes_compra`
  ADD CONSTRAINT `ordenes_compra_id_proveedor_0dc1c7e5_fk_proveedores_id_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_id_categoria_6ba52eae_fk_categorias_id_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`),
  ADD CONSTRAINT `productos_id_ubicacion_500f9600_fk_ubicaciones_id_ubicacion` FOREIGN KEY (`id_ubicacion`) REFERENCES `ubicaciones` (`id_ubicacion`);

--
-- Filtros para la tabla `producto_proveedo`
--
ALTER TABLE `producto_proveedo`
  ADD CONSTRAINT `producto_proveedo_id_producto_903b0998_fk_productos_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  ADD CONSTRAINT `producto_proveedo_id_proveedor_fb074583_fk_proveedor` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`);

--
-- Filtros para la tabla `registos_merma`
--
ALTER TABLE `registos_merma`
  ADD CONSTRAINT `registos_merma_id_motivo_b92dee15_fk_motivos_merma_id_motivo` FOREIGN KEY (`id_motivo`) REFERENCES `motivos_merma` (`id_motivo`),
  ADD CONSTRAINT `registos_merma_id_producto_53067f0d_fk_productos_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_id_cliente_e685d518_fk_clientes_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  ADD CONSTRAINT `ventas_id_empleado_100b8983_fk_empleados_id_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`),
  ADD CONSTRAINT `ventas_id_metodo_pago_0b1de702_fk_metodos_pago_id_metodo_pago` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodos_pago` (`id_metodo_pago`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
