-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-10-2026 a las 16:55:29
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
-- Base de datos: `db_academica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_usss025925`
--

CREATE TABLE `usuarios_usss025925` (
  `idUsuario` int(10) NOT NULL,
  `usuario` char(35) DEFAULT NULL,
  `clave` char(35) DEFAULT NULL,
  `nombre` char(85) DEFAULT NULL,
  `direccion` char(100) DEFAULT NULL,
  `telefono` char(9) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_usss025925`
--

INSERT INTO `usuarios_usss025925` (`idUsuario`, `usuario`, `clave`, `nombre`, `direccion`, `telefono`) VALUES
(1, 'Karen_Ulloa', 'KA-3m7mXW1swyEb6k2_GI_KUGZCpUQFk', 'Karen Ulloa', 'El Transito', '4554-5412'),
(2, 'Eli..', 'ZUDnc9OWwnESFe_cPhuVCCQIaZTxZn0O', 'Elizabeth', 'Usulutan', '4545-5481'),
(3, 'ugbusu', 'unf_vsiCQ-vKF7vQis_jzoJBW5ZkIYh3', 'luis', 'San Miguel', '2222-2222');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `usuarios_usss025925`
--
ALTER TABLE `usuarios_usss025925`
  ADD PRIMARY KEY (`idUsuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `usuarios_usss025925`
--
ALTER TABLE `usuarios_usss025925`
  MODIFY `idUsuario` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
