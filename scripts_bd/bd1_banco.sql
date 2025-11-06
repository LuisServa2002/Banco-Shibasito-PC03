--
-- PostgreSQL database dump
--

\restrict X76NotdYu2QikCL5yT1Xeod1TcIZ1peL80suEg0rmdwgWX6DLEmqWygbIXblael

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cuentas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cuentas (
    id_cuenta integer NOT NULL,
    nombre_cliente character varying(255) NOT NULL,
    dni character varying(8) NOT NULL,
    saldo numeric(10,2) NOT NULL,
    CONSTRAINT cuentas_saldo_check CHECK ((saldo >= (0)::numeric))
);


ALTER TABLE public.cuentas OWNER TO postgres;

--
-- Name: prestamos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prestamos (
    id_prestamo integer NOT NULL,
    id_cuenta integer NOT NULL,
    dni character varying(8) NOT NULL,
    monto numeric(10,2) NOT NULL,
    monto_pendiente numeric(10,2) NOT NULL,
    estado character varying(20) NOT NULL,
    fecha_solicitud timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    plazo_meses integer,
    CONSTRAINT prestamos_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'pagado'::character varying, 'rechazado'::character varying])::text[])))
);


ALTER TABLE public.prestamos OWNER TO postgres;

--
-- Name: prestamos_id_prestamo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prestamos_id_prestamo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prestamos_id_prestamo_seq OWNER TO postgres;

--
-- Name: prestamos_id_prestamo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prestamos_id_prestamo_seq OWNED BY public.prestamos.id_prestamo;


--
-- Name: transacciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transacciones (
    id_transaccion integer NOT NULL,
    id_cuenta integer NOT NULL,
    tipo character varying(50) NOT NULL,
    monto numeric(10,2) NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.transacciones OWNER TO postgres;

--
-- Name: transacciones_id_transaccion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transacciones_id_transaccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transacciones_id_transaccion_seq OWNER TO postgres;

--
-- Name: transacciones_id_transaccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transacciones_id_transaccion_seq OWNED BY public.transacciones.id_transaccion;


--
-- Name: prestamos id_prestamo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prestamos ALTER COLUMN id_prestamo SET DEFAULT nextval('public.prestamos_id_prestamo_seq'::regclass);


--
-- Name: transacciones id_transaccion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transacciones ALTER COLUMN id_transaccion SET DEFAULT nextval('public.transacciones_id_transaccion_seq'::regclass);


--
-- Name: cuentas cuentas_dni_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuentas
    ADD CONSTRAINT cuentas_dni_key UNIQUE (dni);


--
-- Name: cuentas cuentas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuentas
    ADD CONSTRAINT cuentas_pkey PRIMARY KEY (id_cuenta);


--
-- Name: prestamos prestamos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prestamos
    ADD CONSTRAINT prestamos_pkey PRIMARY KEY (id_prestamo);


--
-- Name: transacciones transacciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transacciones
    ADD CONSTRAINT transacciones_pkey PRIMARY KEY (id_transaccion);


--
-- Name: prestamos prestamos_id_cuenta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prestamos
    ADD CONSTRAINT prestamos_id_cuenta_fkey FOREIGN KEY (id_cuenta) REFERENCES public.cuentas(id_cuenta);


--
-- Name: transacciones transacciones_id_cuenta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transacciones
    ADD CONSTRAINT transacciones_id_cuenta_fkey FOREIGN KEY (id_cuenta) REFERENCES public.cuentas(id_cuenta);


--
-- PostgreSQL database dump complete
--

\unrestrict X76NotdYu2QikCL5yT1Xeod1TcIZ1peL80suEg0rmdwgWX6DLEmqWygbIXblael

--
-- PostgreSQL database dump
--

\restrict rBgkaUOI80XM2gQzJaICxFlOzKQApdzEmjbAZlwV9zs8VXVD282wziwguyqJ8fg

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: cuentas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cuentas (id_cuenta, nombre_cliente, dni, saldo) FROM stdin;
1002	JUAN CARLOS RAMÍREZ QUISPE	78901234	1500.50
1003	LUIS ALBERTO TORRES MENDOZA	12345678	980.75
8009	CARLOS JUAN PÉREZ VÁSQUEZ	34567890	3200.00
1001	MARÍA ELENA GARCÍA FLORES	45678912	4000.00
8008	ANA SOFÍA CHÁVEZ ROJAS	23456789	7300.00
\.


--
-- Data for Name: prestamos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prestamos (id_prestamo, id_cuenta, dni, monto, monto_pendiente, estado, fecha_solicitud, plazo_meses) FROM stdin;
1	1001	45678912	5000.00	5000.00	activo	2025-11-04 06:14:16.285435	24
2	1001	45678912	5000.00	5000.00	activo	2025-11-04 06:59:27.037007	24
3	1001	45678912	5000.00	5000.00	activo	2025-11-04 19:26:19.255004	12
4	1001	45678912	1000.00	1000.00	activo	2025-11-04 19:45:19.609396	12
5	1001	45678912	1000.00	1000.00	activo	2025-11-04 20:28:07.106451	12
6	1001	45678912	2000.00	2000.00	activo	2025-11-04 21:46:08.482291	12
7	1001	45678912	300.00	300.00	activo	2025-11-05 21:39:19.382406	12
8	1001	45678912	500.00	500.00	activo	2025-11-05 21:43:42.130678	12
\.


--
-- Data for Name: transacciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transacciones (id_transaccion, id_cuenta, tipo, monto, fecha) FROM stdin;
1	1001	DEBITO	-100.00	2025-11-04 06:09:53.912514
2	8008	CREDITO	100.00	2025-11-04 06:09:53.912514
3	1001	DEBITO	-100.00	2025-11-04 06:14:15.981527
4	8008	CREDITO	100.00	2025-11-04 06:14:15.981527
5	1001	DEBITO	-100.00	2025-11-04 06:59:26.725422
6	8008	CREDITO	100.00	2025-11-04 06:59:26.725422
7	1001	DEBITO	-100.00	2025-11-04 19:11:47.116176
8	8008	CREDITO	100.00	2025-11-04 19:11:47.116176
9	1001	DEBITO	-1000.00	2025-11-04 19:45:40.484045
10	8008	CREDITO	1000.00	2025-11-04 19:45:40.484045
11	1001	DEBITO	-100.00	2025-11-04 20:00:18.073901
12	8008	CREDITO	100.00	2025-11-04 20:00:18.073901
13	1001	CREDITO	1000.00	2025-11-04 20:28:07.106451
14	1001	CREDITO	2000.00	2025-11-04 21:46:08.482291
15	1001	CREDITO	300.00	2025-11-05 21:39:19.382406
16	1001	CREDITO	500.00	2025-11-05 21:43:42.130678
17	1001	DEBITO	-800.00	2025-11-06 11:51:20.596252
18	8008	CREDITO	800.00	2025-11-06 11:51:20.596252
\.


--
-- Name: prestamos_id_prestamo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prestamos_id_prestamo_seq', 8, true);


--
-- Name: transacciones_id_transaccion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transacciones_id_transaccion_seq', 18, true);


--
-- PostgreSQL database dump complete
--

\unrestrict rBgkaUOI80XM2gQzJaICxFlOzKQApdzEmjbAZlwV9zs8VXVD282wziwguyqJ8fg

