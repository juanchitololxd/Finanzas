-- DROPS

CREATE TABLE entradas(
	id number(10) not null,
	monto number(8) not null, 
	fecha date not null);


CREATE TABLE salidas(
	id number(10) not null, 
	monto number(8) not null, 
	categoria varchar(50) not null, 
	fecha date not null);


CREATE TABLE subcategorias(
	categoria varchar(50) not null, 
	subcategoria varchar(50) not null, 
	descripcion varchar(2000));

CREATE TABLE categorias(
	cat varchar(50) not null,
	vf char(1) not null,
	mensual number(8) not null, 
	saldoActual number(8) not null, 
	meta number(8) not null,
	M number(2) not null,
	A number(4) not null
	);


CREATE TABLE deudas(
fecha date not null, 
monto number(8) not null, 
Acreedor varchar(50) not null);


CREATE TABLE totales(
	cat varchar(30) not null,
	saldo number(8) not null);

-- CLAVES O LLAVES
ALTER TABLE entradas ADD CONSTRAINT PK_entradas
	PRIMARY KEY (id);

ALTER TABLE salidas ADD CONSTRAINT PK_salidas
	PRIMARY KEY (id);

ALTER TABLE subcategorias ADD CONSTRAINT PK_subcategorias
	PRIMARY KEY (categoria, subcategoria);

ALTER TABLE categorias ADD CONSTRAINT PK_categorias
	PRIMARY KEY (cat);

ALTER TABLE deudas ADD CONSTRAINT PK_deudas
	PRIMARY KEY (monto, Acreedor);

ALTER TABLE totales ADD CONSTRAINT PK_saldoTotales
	PRIMARY KEY (cat);


-- TUPLAS

-- CHECKS

--TRIGGERS

CREATE TRIGGER AI_deudas
-- Sumar el monto de las deudas en totales
AFTER INSERT ON deudas
FOR EACH ROW
DECLARE
	oldSaldo NUMBER(8);
BEGIN
	SELECT saldo INTO oldSaldo FROM totales where cat = 'deudas';
	UPDATE totales set saldo = oldSaldo + :new.monto where cat = 'deudas';
END;
/

CREATE TRIGGER BI_entradas
-- Automatizaciones
BEFORE INSERT ON entradas
FOR EACH ROW
DECLARE
	cont number(10);
BEGIN
	select count(id)+1 into cont from entradas;
	:new.id := cont;
	:new.fecha := CURRENT_TIMESTAMP;
END;

/
CREATE TRIGGER AI_entradas
-- Sumar la entrada en totales.entradas
AFTER INSERT ON entradas
FOR EACH ROW

DECLARE
	total number(8);
BEGIN
	SELECT saldo INTO total FROM totales WHERE cat = 'entradas';
	UPDATE totales set CAT = total + :new.MONTO WHERE cat = 'entradas';
END;


/
CREATE TRIGGER BI_Salidas
-- Automatizaciones
BEFORE INSERT ON salidas
FOR EACH ROW
DECLARE 
	cont number(10);
BEGIN
	SELECT COUNT(id)+1 INTO cont FROM salidas;
	:new.id := cont;
	:new.fecha := CURRENT_TIMESTAMP;
END;

/
CREATE TRIGGER AI_salidas
AFTER INSERT ON salidas
FOR EACH ROW
DECLARE
	saldo number(8);
	saldoTotales number(8);

BEGIN
	-- Descontar en la respectiva categoria
	SELECT saldoActual INTO saldo FROM categorias WHERE cat = :new.categoria;
	UPDATE categorias set saldoActual = saldo - :new.monto;
	-- Sumar en totales
	SELECT saldo INTO saldoTotales FROM totales WHERE cat = 'salidas';
	UPDATE totales set saldo = saldoTotales + :new.monto;
END;

/
CREATE TRIGGER BI_subcategorias
-- Automatizacion
BEFORE INSERT ON subcategorias
FOR EACH ROW
BEGIN
	:new.descripcion := null;
END;

/

CREATE TRIGGER BI_categorias
-- Automatizaciones
BEFORE INSERT ON categorias
BEGIN
	:new.meta := 0;
	:new.M := 13;
	:new.A := 9999;
END;

/

CREATE TRIGGER AI_categorias
FOR EACH ROW
-- Agregar la categoria como subcategoria
AFTER INSERT ON categorias

BEGIN
	INSERT INTO subcategorias VALUES (:new.cat, :new.cat);
	COMMIT;
END;
