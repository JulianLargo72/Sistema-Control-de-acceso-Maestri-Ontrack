-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 23-02-2024 a las 13:54:02
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
-- Base de datos: `registros_qr`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `externos`
--

CREATE TABLE `externos` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `identificacion` varchar(100) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `compañia` varchar(100) NOT NULL,
  `motivo` varchar(100) NOT NULL,
  `dependencia` varchar(100) NOT NULL,
  `recibe` varchar(100) DEFAULT NULL,
  `arl` varchar(100) NOT NULL,
  `equipo` varchar(100) NOT NULL,
  `qr_path` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `externos`
--

INSERT INTO `externos` (`id`, `identificacion`, `nombre`, `area`, `correo`, `compañia`, `motivo`, `dependencia`, `recibe`, `arl`, `equipo`, `qr_path`) VALUES
(3, '343434', 'Proveedor Smilco', 'Tercero', 'julianbetancur104@gmail.com', 'Smilco', 'Diligencia', 'Administrativa', 'Renato Maestri', 'Positiva', 'Tablet', 'static/qr_images/T343434.png'),
(6, '5445211', 'prueba qr febrero', 'Tercero', 'julianbetancur104@gmail.com', 'Colanta', 'Diligencia', 'Comercial', 'Prueba qr', 'Positiva', 'PC', 'static/qr_images/T5445211.png');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `login`
--

CREATE TABLE `login` (
  `id` int(11) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `login`
--

INSERT INTO `login` (`id`, `correo`, `password`) VALUES
(1, 'julianbetancur104@gmail.com', 'julian123'),
(10, 'julian.72004@gmail.com', '1234');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `identificacion` varchar(100) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `fecha` date NOT NULL,
  `hora_escaneo` varchar(100) NOT NULL,
  `hora_entrada` varchar(100) NOT NULL,
  `hora_salida` varchar(100) NOT NULL,
  `rango` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `registros`
--

INSERT INTO `registros` (`id`, `identificacion`, `nombre`, `area`, `fecha`, `hora_escaneo`, `hora_entrada`, `hora_salida`, `rango`) VALUES
(1, '1054398414', 'Julian Betancur', 'Administrativa', '2024-02-14', '10:26:36', '10:26:36', '10:26:36', 'Revisar'),
(2, '1054398415', 'Renato Maestri', 'Administrativa', '2024-02-14', '10:27:10', '10:27:10', '10:27:10', 'Revisar'),
(3, '1054398414', 'Julian Betancur', 'Administrativa', '2024-02-14', '10:30:52', '10:26:36', '10:30:52', 'Revisar'),
(4, '1054398414', 'Julian Betancur', 'Administrativa', '2024-02-14', '13:33:33', '10:26:36', '13:33:34', 'Entrada PM'),
(5, '1054398415', 'Renato Maestri', 'Administrativa', '2024-02-15', '10:19:19', '10:19:19', '10:19:19', 'Revisado tuvo una cita medica');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tercero`
--

CREATE TABLE `tercero` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `identificacion` varchar(100) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `fecha` date NOT NULL,
  `hora_escaneo` varchar(100) NOT NULL,
  `hora_entrada` varchar(100) NOT NULL,
  `hora_salida` varchar(100) NOT NULL,
  `compañia` varchar(100) NOT NULL,
  `motivo` varchar(100) NOT NULL,
  `dependencia` varchar(100) NOT NULL,
  `recibe` varchar(100) NOT NULL,
  `arl` varchar(100) NOT NULL,
  `equipo` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tercero`
--

INSERT INTO `tercero` (`id`, `identificacion`, `nombre`, `area`, `fecha`, `hora_escaneo`, `hora_entrada`, `hora_salida`, `compañia`, `motivo`, `dependencia`, `recibe`, `arl`, `equipo`) VALUES
(21, '343434', 'Proveedor Smilco', 'Tercero', '2024-02-14', '10:27:56', '10:27:56', '10:27:56', 'Smilco', 'Diligencia', 'Administrativa', 'Julian Betancur', 'Positiva', 'Tablet'),
(22, '343434', 'Proveedor Smilco', 'Tercero', '2024-02-14', '10:31:09', '10:27:56', '10:31:09', 'Smilco', 'Diligencia', 'Administrativa', 'Renato Maestri', 'Positiva', 'Tablet'),
(23, '343434', 'Proveedor Smilco', 'Tercero', '2024-02-14', '13:34:33', '10:27:56', '13:34:33', 'Smilco', 'Diligencia', 'Administrativa', 'Renato Maestri', 'Positiva', 'Tablet'),
(24, '1235555', 'Normandy', 'Tercero', '2024-02-14', '15:45:33', '15:45:33', '15:45:33', 'Normandy SAS', 'Ventas', 'Administrativa', 'Renato Maestri', 'POSITIVA', 'N/A'),
(25, '23443434', 'Fabio', 'Tercero', '2024-02-15', '10:19:31', '10:19:31', '10:19:31', 'Smilcoo', 'Diligenciaa', 'Comercial', 'Renato Maestri', 'Positiva', 'N/A');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `identificacion` varchar(100) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `qr_path` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `identificacion`, `nombre`, `area`, `correo`, `qr_path`) VALUES
(12, '1054398415', 'Renato Maestri', 'Administrativa', 'julianbetancur104@gmail.com', 'static/qr_images/A1054398415.png'),
(13, '1054398414', 'Julian Betancur', 'Administrativa', 'julianbetancur104@gmail.com', 'static/qr_images/A1054398414.png'),
(14, '5566634', 'Prueba qr', 'Gerencial', 'julianbetancur104@gmail.com', 'static/qr_images/G5566634.png');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `externos`
--
ALTER TABLE `externos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `login`
--
ALTER TABLE `login`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tercero`
--
ALTER TABLE `tercero`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `externos`
--
ALTER TABLE `externos`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `login`
--
ALTER TABLE `login`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `tercero`
--
ALTER TABLE `tercero`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
