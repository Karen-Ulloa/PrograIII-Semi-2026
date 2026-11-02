-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 02-11-2026 a las 14:46:36
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
CREATE DATABASE IF NOT EXISTS `db_campesinostock` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `db_campesinostock`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add categorias', 7, 'add_categorias'),
(26, 'Can change categorias', 7, 'change_categorias'),
(27, 'Can delete categorias', 7, 'delete_categorias'),
(28, 'Can view categorias', 7, 'view_categorias'),
(29, 'Can add clientes', 8, 'add_clientes'),
(30, 'Can change clientes', 8, 'change_clientes'),
(31, 'Can delete clientes', 8, 'delete_clientes'),
(32, 'Can view clientes', 8, 'view_clientes'),
(33, 'Can add configuracion', 9, 'add_configuracion'),
(34, 'Can change configuracion', 9, 'change_configuracion'),
(35, 'Can delete configuracion', 9, 'delete_configuracion'),
(36, 'Can view configuracion', 9, 'view_configuracion'),
(37, 'Can add empleados', 10, 'add_empleados'),
(38, 'Can change empleados', 10, 'change_empleados'),
(39, 'Can delete empleados', 10, 'delete_empleados'),
(40, 'Can view empleados', 10, 'view_empleados'),
(41, 'Can add metodos pago', 11, 'add_metodospago'),
(42, 'Can change metodos pago', 11, 'change_metodospago'),
(43, 'Can delete metodos pago', 11, 'delete_metodospago'),
(44, 'Can view metodos pago', 11, 'view_metodospago'),
(45, 'Can add motivos merma', 12, 'add_motivosmerma'),
(46, 'Can change motivos merma', 12, 'change_motivosmerma'),
(47, 'Can delete motivos merma', 12, 'delete_motivosmerma'),
(48, 'Can view motivos merma', 12, 'view_motivosmerma'),
(49, 'Can add productos', 13, 'add_productos'),
(50, 'Can change productos', 13, 'change_productos'),
(51, 'Can delete productos', 13, 'delete_productos'),
(52, 'Can view productos', 13, 'view_productos'),
(53, 'Can add proveedores', 14, 'add_proveedores'),
(54, 'Can change proveedores', 14, 'change_proveedores'),
(55, 'Can delete proveedores', 14, 'delete_proveedores'),
(56, 'Can view proveedores', 14, 'view_proveedores'),
(57, 'Can add ubicaciones', 15, 'add_ubicaciones'),
(58, 'Can change ubicaciones', 15, 'change_ubicaciones'),
(59, 'Can delete ubicaciones', 15, 'delete_ubicaciones'),
(60, 'Can view ubicaciones', 15, 'view_ubicaciones'),
(61, 'Can add ventas', 16, 'add_ventas'),
(62, 'Can change ventas', 16, 'change_ventas'),
(63, 'Can delete ventas', 16, 'delete_ventas'),
(64, 'Can view ventas', 16, 'view_ventas'),
(65, 'Can add registros merma', 17, 'add_registrosmerma'),
(66, 'Can change registros merma', 17, 'change_registrosmerma'),
(67, 'Can delete registros merma', 17, 'delete_registrosmerma'),
(68, 'Can view registros merma', 17, 'view_registrosmerma'),
(69, 'Can add ordenes compra', 18, 'add_ordenescompra'),
(70, 'Can change ordenes compra', 18, 'change_ordenescompra'),
(71, 'Can delete ordenes compra', 18, 'delete_ordenescompra'),
(72, 'Can view ordenes compra', 18, 'view_ordenescompra'),
(73, 'Can add detalle venta', 19, 'add_detalleventa'),
(74, 'Can change detalle venta', 19, 'change_detalleventa'),
(75, 'Can delete detalle venta', 19, 'delete_detalleventa'),
(76, 'Can view detalle venta', 19, 'view_detalleventa'),
(77, 'Can add detalle compra', 20, 'add_detallecompra'),
(78, 'Can change detalle compra', 20, 'change_detallecompra'),
(79, 'Can delete detalle compra', 20, 'delete_detallecompra'),
(80, 'Can view detalle compra', 20, 'view_detallecompra'),
(81, 'Can add producto proveedo', 21, 'add_productoproveedo'),
(82, 'Can change producto proveedo', 21, 'change_productoproveedo'),
(83, 'Can delete producto proveedo', 21, 'delete_productoproveedo'),
(84, 'Can view producto proveedo', 21, 'view_productoproveedo');

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`) VALUES
(1, 'Tornillería y fijación'),
(2, 'Lijas'),
(3, 'Pinturas y accesorios'),
(4, 'Herramientas manuales'),
(5, 'Discos y brocas'),
(6, 'Eléctrico'),
(7, 'Plomería'),
(8, 'Construcción'),
(9, 'Otros');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `telefono` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion`
--

CREATE TABLE `configuracion` (
  `clave` varchar(50) NOT NULL,
  `valor` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(9, 'inventario', 'configuracion'),
(20, 'inventario', 'detallecompra'),
(19, 'inventario', 'detalleventa'),
(10, 'inventario', 'empleados'),
(11, 'inventario', 'metodospago'),
(12, 'inventario', 'motivosmerma'),
(18, 'inventario', 'ordenescompra'),
(21, 'inventario', 'productoproveedo'),
(13, 'inventario', 'productos'),
(14, 'inventario', 'proveedores'),
(17, 'inventario', 'registrosmerma'),
(15, 'inventario', 'ubicaciones'),
(16, 'inventario', 'ventas'),
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-11-02 13:07:06.886919'),
(2, 'auth', '0001_initial', '2026-11-02 13:07:08.528657'),
(3, 'admin', '0001_initial', '2026-11-02 13:07:08.788612'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-11-02 13:07:08.813652'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-11-02 13:07:08.830402'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-11-02 13:07:09.108040'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-11-02 13:07:09.245171'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-11-02 13:07:09.298622'),
(9, 'auth', '0004_alter_user_username_opts', '2026-11-02 13:07:09.328705'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-11-02 13:07:09.489314'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-11-02 13:07:09.500975'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-11-02 13:07:09.526158'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-11-02 13:07:09.569203'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-11-02 13:07:09.611098'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-11-02 13:07:09.673149'),
(16, 'auth', '0011_update_proxy_permissions', '2026-11-02 13:07:09.702632'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-11-02 13:07:09.768462'),
(18, 'inventario', '0001_initial', '2026-11-02 13:07:13.618070'),
(19, 'sessions', '0001_initial', '2026-11-02 13:07:13.705255');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  `rol` varchar(20) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `foto` varchar(100) DEFAULT NULL,
  `ultimo_acceso` datetime(6) DEFAULT NULL,
  `sesion_version` int(11) NOT NULL,
  `intentos_fallidos` int(11) NOT NULL,
  `bloqueado_hasta` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodos_pago`
--

CREATE TABLE `metodos_pago` (
  `id_metodo_pago` int(11) NOT NULL,
  `nombre_metodo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `motivos_merma`
--

CREATE TABLE `motivos_merma` (
  `id_motivo` int(11) NOT NULL,
  `descripcion` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ordenes_compra`
--

CREATE TABLE `ordenes_compra` (
  `id_compra` int(11) NOT NULL,
  `fecha_compra` datetime(6) NOT NULL,
  `id_proveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(150) NOT NULL,
  `precio_producto` decimal(10,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `precio_compra` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `stock_minimo` int(11) NOT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_ubicacion` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre_producto`, `precio_producto`, `imagen`, `precio_compra`, `stock`, `stock_minimo`, `id_categoria`, `id_ubicacion`) VALUES
(1, 'Tornillo para madera 1/4\" x 2\"', 0.10, NULL, 0.04, 0, 5, 1, NULL),
(2, 'Tornillo para madera 1/4\" x 3\"', 0.12, NULL, 0.06, 0, 5, 1, NULL),
(3, 'Tornillo goloso 10 x 1\"', 0.08, NULL, 0.03, 0, 5, 1, NULL),
(4, 'Tornillo de fijación para lámina 14 x 1\"', 0.10, NULL, 0.05, 0, 5, 1, NULL),
(5, 'Tornillo para drywall 6 x 1\"', 0.05, NULL, 0.02, 0, 5, 1, NULL),
(6, 'Perno hexagonal grado 2 3/8\" x 2\"', 0.35, NULL, 0.15, 0, 5, 1, NULL),
(7, 'Tuerca hexagonal 1/4\"', 0.05, NULL, 0.02, 0, 5, 1, NULL),
(8, 'Tuerca hexagonal 3/8\"', 0.10, NULL, 0.04, 0, 5, 1, NULL),
(9, 'Arandela plana 1/4\"', 0.10, NULL, 0.02, 0, 5, 1, NULL),
(10, 'Arandela de presión 3/8\"', 0.13, NULL, 0.05, 0, 5, 1, NULL),
(11, 'Clavo con cabeza para madera 2\" (libra)', 1.25, NULL, 0.75, 0, 5, 1, NULL),
(12, 'Clavo con cabeza para madera 3\" (libra)', 1.25, NULL, 0.75, 0, 5, 1, NULL),
(13, 'Clavo para concreto 2\" (libra)', 1.75, NULL, 1.10, 0, 5, 1, NULL),
(14, 'Clavo para concreto 3\" (libra)', 1.75, NULL, 1.10, 0, 5, 1, NULL),
(15, 'Taquete / Tarugo plástico 1/4\"', 0.05, NULL, 0.02, 0, 5, 1, NULL),
(16, 'Taquete / Tarugo plástico 3/8\"', 0.10, NULL, 0.04, 0, 5, 1, NULL),
(17, 'Lija para agua N° 80', 0.75, NULL, 0.35, 0, 5, 2, NULL),
(18, 'Lija para agua N° 120', 0.75, NULL, 0.35, 0, 5, 2, NULL),
(19, 'Lija para agua N° 220', 0.75, NULL, 0.35, 0, 5, 2, NULL),
(20, 'Lija para agua N° 400', 0.80, NULL, 0.40, 0, 5, 2, NULL),
(21, 'Lija para madera N° 60', 1.00, NULL, 0.30, 0, 5, 2, NULL),
(22, 'Lija para madera N° 100', 0.60, NULL, 0.30, 0, 5, 2, NULL),
(23, 'Pintura de aceite Rojo Óxido (Galón)', 18.00, NULL, 12.50, 0, 5, 3, NULL),
(24, 'Pintura de aceite Blanco Hueso (Galón)', 19.50, NULL, 13.00, 0, 5, 3, NULL),
(25, 'Pintura de aceite Negro Mate (Galón)', 18.00, NULL, 12.50, 0, 5, 3, NULL),
(26, 'Pintura látex Blanco (Galón)', 14.50, NULL, 9.50, 0, 5, 3, NULL),
(27, 'Pintura látex Azul Colonial (Galón)', 15.50, NULL, 10.00, 0, 5, 3, NULL),
(28, 'Pintura látex Verde Bosque (Galón)', 15.50, NULL, 10.00, 0, 5, 3, NULL),
(29, 'Anti-corrosivo Gris (Galón)', 16.50, NULL, 11.00, 0, 5, 3, NULL),
(30, 'Thinner corriente (Galón)', 8.50, NULL, 5.50, 0, 5, 3, NULL),
(31, 'Solvente Mineral / Aguarrás (Galón)', 9.00, NULL, 6.00, 0, 5, 3, NULL),
(32, 'Brocha para pintura 1\"', 1.00, NULL, 0.45, 0, 5, 3, NULL),
(33, 'Brocha para pintura 2\"', 1.75, NULL, 0.85, 0, 5, 3, NULL),
(34, 'Brocha para pintura 3\"', 2.50, NULL, 1.25, 0, 5, 3, NULL),
(35, 'Rodillo para pintura felpa 9\"', 3.00, NULL, 1.50, 0, 5, 3, NULL),
(36, 'Martillo de uña curva 16 oz', 7.50, NULL, 4.25, 0, 5, 4, NULL),
(37, 'Alicate universal 7\"', 6.00, NULL, 3.50, 0, 5, 4, NULL),
(38, 'Tenaza de presión 10\"', 9.00, NULL, 5.00, 0, 5, 4, NULL),
(39, 'Destornillador plano 1/4\" x 4\"', 2.50, NULL, 1.20, 0, 5, 4, NULL),
(40, 'Destornillador de estrella (Phillips) #2 x 4\"', 2.50, NULL, 1.20, 0, 5, 4, NULL),
(41, 'Llave ajustable (Cinta/Perica) 8\"', 7.50, NULL, 4.00, 0, 5, 4, NULL),
(42, 'Cinta métrica (Flexómetro) 5 metros / 16 pies', 4.00, NULL, 2.00, 0, 5, 4, NULL),
(43, 'Arco de sierra para metal 12\"', 5.50, NULL, 3.00, 0, 5, 4, NULL),
(44, 'Hoja de sierra para metal 18 dientes', 1.25, NULL, 0.60, 0, 5, 5, NULL),
(45, 'Disco de corte para metal 4 1/2\" x 1/16\"', 1.35, NULL, 0.70, 0, 5, 5, NULL),
(46, 'Disco de corte para concreto 4 1/2\"', 4.50, NULL, 2.50, 0, 5, 5, NULL),
(47, 'Broca para concreto 1/4\" x 4\"', 1.75, NULL, 0.90, 0, 5, 5, NULL),
(48, 'Broca para concreto 3/8\" x 6\"', 2.75, NULL, 1.40, 0, 5, 5, NULL),
(49, 'Broca para metal HSS 1/8\"', 1.10, NULL, 0.50, 0, 5, 5, NULL),
(50, 'Broca para metal HSS 1/4\"', 1.80, NULL, 0.90, 0, 5, 5, NULL),
(51, 'Foco LED 9W luz blanca (Rosca E27)', 1.75, NULL, 0.85, 0, 5, 6, NULL),
(52, 'Foco LED 12W luz blanca (Rosca E27)', 2.25, NULL, 1.10, 0, 5, 6, NULL),
(53, 'Foco LED 15W luz cálida (Rosca E27)', 2.75, NULL, 1.40, 0, 5, 6, NULL),
(54, 'Tomacorriente doble polarizado (Blanco)', 2.25, NULL, 1.10, 0, 5, 6, NULL),
(55, 'Interruptor sencillo de pared (Blanco)', 1.85, NULL, 0.90, 0, 5, 6, NULL),
(56, 'Cinta aislante negra 18m (3M o similar)', 1.60, NULL, 0.80, 0, 5, 6, NULL),
(57, 'Socket / Plafón de porcelana E27', 1.00, NULL, 0.45, 0, 5, 6, NULL),
(58, 'Breaker / Cordoncillo 1 polo 20A', 5.00, NULL, 2.80, 0, 5, 6, NULL),
(59, 'Cable eléctrico THHN N° 12 (Metro)', 0.85, NULL, 0.45, 0, 5, 6, NULL),
(60, 'Cable eléctrico THHN N° 14 (Metro)', 0.65, NULL, 0.32, 0, 5, 6, NULL),
(61, 'Tubo PVC agua potable 1/2\" SDR 13.5 (6m)', 3.60, NULL, 2.00, 0, 5, 7, NULL),
(62, 'Tubo PVC agua potable 3/4\" SDR 21 (6m)', 4.80, NULL, 2.80, 0, 5, 7, NULL),
(63, 'Codo PVC 1/2\" a 90° para agua', 0.35, NULL, 0.15, 0, 5, 7, NULL),
(64, 'Te PVC 1/2\" para agua', 0.45, NULL, 0.20, 0, 5, 7, NULL),
(65, 'Pegamento para PVC (Pega PVC) 4 oz', 3.00, NULL, 1.60, 0, 5, 7, NULL),
(66, 'Cinta de teflón 1/2\" x 260\"', 0.60, NULL, 0.25, 0, 5, 7, NULL),
(67, 'Llave de chorro bronce 1/2\"', 6.00, NULL, 3.20, 0, 5, 7, NULL),
(68, 'Silicón transparente uso general 280ml', 4.00, NULL, 2.20, 0, 5, 7, NULL),
(69, 'Cemento CUSCATLÁNEO / HOLCIM (Bolsa 42.5 kg)', 9.25, NULL, 7.80, 0, 5, 8, NULL),
(70, 'Varilla de hierro corrugado 3/8\" (Grade 40 - 6m)', 3.80, NULL, 2.60, 0, 5, 8, NULL),
(71, 'Varilla de hierro corrugado 1/2\" (Grade 40 - 6m)', 6.50, NULL, 4.60, 0, 5, 8, NULL),
(72, 'Alambre de amarre (Libra)', 1.20, NULL, 0.70, 0, 5, 8, NULL),
(73, 'Candado de hierro 40mm', 4.80, NULL, 2.50, 0, 5, 9, NULL),
(74, 'Cuchilla / Exacto universal 18mm', 1.25, NULL, 0.60, 0, 5, 9, NULL),
(75, 'Guantes de lona con puntos de PVC (Par)', 1.50, NULL, 0.75, 0, 5, 9, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto_proveedo`
--

CREATE TABLE `producto_proveedo` (
  `id` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL,
  `nombre_proveedor` varchar(150) NOT NULL,
  `contacto_proveedor` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicaciones`
--

CREATE TABLE `ubicaciones` (
  `id_ubicacion` int(11) NOT NULL,
  `pasillo` varchar(50) NOT NULL,
  `estante` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

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
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

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
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT;

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
