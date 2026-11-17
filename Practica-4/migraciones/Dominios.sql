
-- ----------------------------------------------------------------------------
-- DOMINIOS
-- ----------------------------------------------------------------------------

-- Regla: Todo monto monetario del restaurante debe ser mayor o igual a cero y manejar centavos exactos.
CREATE DOMAIN dom_moneda AS NUMERIC(10, 2)
    CHECK (VALUE >= 0);

-- Regla: Todo número telefónico debe constar exactamente de 10 dígitos numéricos nacionales.
CREATE DOMAIN dom_telefono AS CHAR(10)
    CHECK (VALUE ~ '^[0-9]{10}$');

-- Regla: Los meseros solo pueden operar dentro de los tres turnos establecidos por el restaurante.
CREATE TYPE tipo_turno AS ENUM ('Matutino', 'Vespertino', 'Mixto');

-- Ajuste de tipos de columna hacia los dominios creados y limpieza de esquema
ALTER TABLE EMPLEADO
    ALTER COLUMN Telefono TYPE dom_telefono USING TRIM(Telefono)::dom_telefono;

ALTER TABLE MESERO
    ALTER COLUMN Turno TYPE tipo_turno USING Turno::tipo_turno;

ALTER TABLE CLIENTE
    ALTER COLUMN Telefono TYPE dom_telefono USING TRIM(Telefono)::dom_telefono;

ALTER TABLE TELEFONO_CLIENTE
    ALTER COLUMN Telefono TYPE dom_telefono USING TRIM(Telefono)::dom_telefono;

ALTER TABLE PLATILLO
    ALTER COLUMN Precio TYPE dom_moneda USING Precio::dom_moneda;

ALTER TABLE PEDIDO
    ALTER COLUMN Total TYPE dom_moneda USING Total::dom_moneda;

ALTER TABLE DETALLE_PEDIDO
    ALTER COLUMN PrecioUnitario TYPE dom_moneda USING PrecioUnitario::dom_moneda,
    ALTER COLUMN Subtotal TYPE dom_moneda USING Subtotal::dom_moneda;


-- Regla: Todo empleado debe tener nombre, teléfono, fecha de contratación y RFC registrados para su expediente.
ALTER TABLE EMPLEADO
    ALTER COLUMN Nombre SET NOT NULL,
    ALTER COLUMN Telefono SET NOT NULL,
    ALTER COLUMN FechaContratacion SET NOT NULL,
    ALTER COLUMN RFC SET NOT NULL;

-- Regla: Todo mesero debe tener asignado un turno operativo de trabajo.
ALTER TABLE MESERO
    ALTER COLUMN Turno SET NOT NULL;

-- Regla: Todo chef debe contar con una especialidad culinaria y años de experiencia registrados.
ALTER TABLE CHEF
    ALTER COLUMN Especialidad SET NOT NULL,
    ALTER COLUMN AniosExperiencia SET NOT NULL;

-- Regla: Todo cliente registrado debe contar al menos con nombre y teléfono de contacto.
ALTER TABLE CLIENTE
    ALTER COLUMN Nombre SET NOT NULL,
    ALTER COLUMN Telefono SET NOT NULL;

-- Regla: Todo platillo en el menú debe tener nombre, precio y un chef responsable asignado (cardinalidad 1:1).
ALTER TABLE PLATILLO
    ALTER COLUMN Nombre SET NOT NULL,
    ALTER COLUMN Precio SET NOT NULL,
    ALTER COLUMN ID_Empleado SET NOT NULL;

-- Regla: Toda asignación chef-platillo requiere registrar la fecha en que se otorgó la responsabilidad.
ALTER TABLE ASIGNACION_CHEF_PLATILLO
    ALTER COLUMN FechaAsignacion SET NOT NULL;

-- Regla: Todo pedido debe registrar fecha/hora, total, el cliente que ordena (1,1) y el mesero que atiende (1,1).
ALTER TABLE PEDIDO
    ALTER COLUMN FechaHora SET NOT NULL,
    ALTER COLUMN ID_Cliente SET NOT NULL,
    ALTER COLUMN ID_Mesero SET NOT NULL,
    ALTER COLUMN Total SET NOT NULL;

-- Regla: Todo renglón de detalle debe especificar platillo (1,1), cantidad, precio unitario y subtotal.
ALTER TABLE DETALLE_PEDIDO
    ALTER COLUMN ID_Platillo SET NOT NULL,
    ALTER COLUMN Cantidad SET NOT NULL,
    ALTER COLUMN PrecioUnitario SET NOT NULL,
    ALTER COLUMN Subtotal SET NOT NULL;


-- Regla: Si no se indica fecha de contratación al registrar un empleado, se asume el día actual.
ALTER TABLE EMPLEADO
    ALTER COLUMN FechaContratacion SET DEFAULT CURRENT_DATE;

-- Regla: Un chef recién registrado sin historial previo inicia con 0 años de experiencia.
ALTER TABLE CHEF
    ALTER COLUMN AniosExperiencia SET DEFAULT 0;

-- Regla: La fecha de asignación de un platillo a un chef toma el día actual por defecto.
ALTER TABLE ASIGNACION_CHEF_PLATILLO
    ALTER COLUMN FechaAsignacion SET DEFAULT CURRENT_DATE;

-- Regla: Todo pedido nuevo toma la fecha y hora exacta del sistema al abrirse e inicia con total en $0.00.
ALTER TABLE PEDIDO
    ALTER COLUMN FechaHora SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN Total SET DEFAULT 0.00;

-- Regla: Al agregar un platillo a un pedido, la cantidad inicial por defecto es 1 unidad.
ALTER TABLE DETALLE_PEDIDO
    ALTER COLUMN Cantidad SET DEFAULT 1;

-- Regla: Dos empleados distintos no pueden compartir el mismo RFC fiscal.
ALTER TABLE EMPLEADO
    ADD CONSTRAINT uq_empleado_rfc UNIQUE (RFC);

--  Regla: Cada cliente registrado debe tener una dirección de correo electrónico única.
ALTER TABLE CLIENTE
    ADD CONSTRAINT uq_cliente_correo UNIQUE (Correo);

--  Regla: No pueden existir dos platillos con exactamente el mismo nombre en la carta.
ALTER TABLE PLATILLO
    ADD CONSTRAINT uq_platillo_nombre UNIQUE (Nombre);

--  Regla: Un mismo platillo no debe aparecer duplicado en renglones separados dentro del mismo pedido.
ALTER TABLE DETALLE_PEDIDO
    ADD CONSTRAINT uq_detalle_pedido_platillo UNIQUE (ID_Pedido, ID_Platillo);


--  Regla: El RFC del empleado debe cumplir con la estructura oficial mexicana de 13 caracteres (4 letras, 6 dígitos de fecha y 3 de homoclave).
ALTER TABLE EMPLEADO
    ADD CONSTRAINT chk_empleado_rfc_formato
    CHECK (RFC ~ '^[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}$');

--  Regla: Ningún empleado puede registrarse con una fecha de contratación futura ni anterior a la fundación del restaurante (2010-01-01).
ALTER TABLE EMPLEADO
    ADD CONSTRAINT chk_empleado_fecha_contratacion
    CHECK (FechaContratacion BETWEEN '2010-01-01' AND CURRENT_DATE);

--  Regla: Los años de experiencia de un chef deben estar en un rango realista entre 0 y 60 años.
ALTER TABLE CHEF
    ADD CONSTRAINT chk_chef_anios_experiencia
    CHECK (AniosExperiencia BETWEEN 0 AND 60);

--  Regla: La especialidad de un chef debe pertenecer a las áreas culinarias autorizadas del restaurante.
ALTER TABLE CHEF
    ADD CONSTRAINT chk_chef_especialidad_valida
    CHECK (Especialidad IN ('Cocina Mexicana', 'Parrilla', 'Mariscos', 'Repostería', 'Pastas', 'Cocina Internacional', 'Entradas y Ensaladas'));

--  Regla: El correo electrónico del cliente debe contener un usuario, un arroba (@) y un dominio válido.
ALTER TABLE CLIENTE
    ADD CONSTRAINT chk_cliente_correo_formato
    CHECK (Correo ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

--  Regla: Todo platillo en venta debe tener un precio estrictamente mayor a $0.00 (no se permiten platillos gratuitos en carta).
ALTER TABLE PLATILLO
    ADD CONSTRAINT chk_platillo_precio_positivo
    CHECK (Precio > 0);

--  Regla: La cantidad solicitada de un platillo en un pedido debe ser de al menos 1 y máximo 50 unidades por renglón.
ALTER TABLE DETALLE_PEDIDO
    ADD CONSTRAINT chk_detalle_cantidad_rango
    CHECK (Cantidad BETWEEN 1 AND 50);

--  Regla: El precio unitario congelado en el detalle del pedido debe ser estrictamente mayor a cero.
ALTER TABLE DETALLE_PEDIDO
    ADD CONSTRAINT chk_detalle_precio_unitario
    CHECK (PrecioUnitario > 0);

--  Regla: El subtotal de cada renglón del detalle debe ser exactamente igual a la cantidad multiplicada por el precio unitario.
ALTER TABLE DETALLE_PEDIDO
    ADD CONSTRAINT chk_detalle_subtotal_exacto
    CHECK (Subtotal = Cantidad * PrecioUnitario);

--  Regla: La fecha de asignación de un platillo a un chef no puede ser futura respecto al día actual.
ALTER TABLE ASIGNACION_CHEF_PLATILLO
    ADD CONSTRAINT chk_asignacion_fecha_valida
    CHECK (FechaAsignacion <= CURRENT_DATE);

