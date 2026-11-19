# 2.4. Edición de valores y transacciones

## Objetivo

Realizar operaciones de modificación de información mediante instrucciones SQL de PostgreSQL, utilizando `INSERT`, `UPDATE`, `DELETE` y transacciones para mantener la consistencia de la base de datos del restaurante.

Las operaciones consideran el modelo original y las nuevas entidades `ADMINISTRADOR`, `MESA` y `RESERVA`.

> **Nota:** los ejemplos utilizan nombres de columnas en minúsculas y con guion bajo. Si el archivo `dominios.md` o el esquema implementado utiliza nombres diferentes, se deben sustituir por los nombres reales. Las tablas nuevas deben existir antes de ejecutar sus operaciones.

## 1. Inserción de registros mediante INSERT SELECT

Se utiliza `INSERT INTO ... SELECT` para insertar información obtenida de otra tabla.

Ejemplo: registrar en la tabla de administradores a un empleado que ya se encuentre registrado en `empleado`.

```sql
INSERT INTO administrador (id_empleado)
SELECT id_empleado
FROM empleado
WHERE id_empleado = (
    SELECT MIN(id_empleado)
    FROM empleado
);
```

**Explicación:** se selecciona un empleado existente y se utiliza su identificador para crear el registro correspondiente en `administrador`. La operación debe realizarse solamente si ese empleado todavía no está registrado como administrador.

## 2. INSERT que resuelve un registro duplicado

PostgreSQL permite utilizar `ON CONFLICT` para evitar que una inserción genere duplicados.

Ejemplo con la tabla de asignaciones:

```sql
INSERT INTO asignacion_chef_platillo (id_empleado, id_platillo)
VALUES (1, 1)
ON CONFLICT (id_empleado, id_platillo)
DO NOTHING;
```

**Explicación:** si la combinación de chef y platillo ya existe, PostgreSQL no inserta otra fila. Para utilizar esta instrucción, la combinación de columnas debe tener una restricción `UNIQUE` o formar parte de la clave primaria.

## 3. UPDATE dependiente de otra tabla

Se utiliza una subconsulta para actualizar un registro tomando como referencia información de otra tabla.

Ejemplo: cambiar el chef responsable de un platillo utilizando el identificador de un chef existente.

```sql
UPDATE platillo
SET id_empleado = (
    SELECT id_empleado
    FROM chef
    WHERE id_empleado = 2
)
WHERE id_platillo = 1;
```

**Explicación:** el platillo seleccionado cambia su chef responsable. La subconsulta obtiene el identificador directamente de `chef`, evitando asignar una referencia inexistente.

## 4. UPDATE utilizando CASE

La instrucción `CASE` permite establecer diferentes valores dependiendo de una condición.

Ejemplo: modificar el estado de las mesas según su identificador.

```sql
UPDATE mesa
SET estado = CASE
    WHEN id_mesa = 1 THEN 'ocupada'
    WHEN id_mesa = 2 THEN 'reservada'
    WHEN id_mesa = 3 THEN 'mantenimiento'
    ELSE estado
END
WHERE id_mesa IN (1, 2, 3);
```

**Explicación:** se actualizan diferentes mesas con distintos estados en una sola instrucción. Los valores utilizados deben coincidir con los permitidos por la restricción `CHECK` de la tabla.

## 5. DELETE utilizando una subconsulta

Se utiliza una subconsulta para seleccionar los registros que cumplen una condición antes de eliminarlos.

Ejemplo: eliminar asignaciones de un chef que ya no se encuentre registrado.

```sql
DELETE FROM asignacion_chef_platillo
WHERE id_empleado NOT IN (
    SELECT id_empleado
    FROM chef
);
```

**Explicación:** se eliminan asignaciones que no tengan un chef correspondiente. En un esquema con claves foráneas correctamente aplicadas, esta situación no debería presentarse; la consulta sirve como ejemplo de eliminación condicionada y como limpieza de datos heredados.

## 6. Borrado lógico

El borrado lógico consiste en marcar un registro como inactivo en lugar de eliminarlo físicamente. Esto permite conservar el historial y evitar problemas con las claves foráneas.

Ejemplo para desactivar un platillo:

```sql
UPDATE platillo
SET disponible = FALSE
WHERE id_platillo = 1;
```

**Explicación:** el platillo deja de aparecer como disponible para nuevos pedidos, pero permanece almacenado para conservar las referencias de pedidos anteriores.

Si el campo real no se llama `disponible`, deberá utilizarse el atributo de estado o disponibilidad definido en `dominios.md`.

## 7. Transacción que modifica al menos dos tablas

Una transacción permite ejecutar varias operaciones como una sola unidad. Si alguna operación falla, se puede cancelar el conjunto de cambios.

Ejemplo: registrar una mesa y una reservación dentro de una misma transacción.

```sql
BEGIN;

INSERT INTO mesa (numero_mesa, capacidad, ubicacion, estado)
VALUES (11, 4, 'Salón principal', 'reservada');

INSERT INTO reserva (
    id_cliente,
    id_mesa,
    fecha_hora,
    numero_personas,
    estado
)
VALUES (
    1,
    (SELECT id_mesa FROM mesa WHERE numero_mesa = 11),
    CURRENT_TIMESTAMP + INTERVAL '1 day',
    2,
    'confirmada'
);

COMMIT;
```

**Explicación:** primero se registra una mesa y después se crea una reservación asociada con ella. Ambas operaciones se confirman juntas. Los campos y estados deben coincidir con la definición implementada de `MESA` y `RESERVA`.

## 8. SAVEPOINT y rollback parcial

Los puntos de restauración permiten deshacer una parte de una transacción sin cancelar todos los cambios anteriores.

```sql
BEGIN;

UPDATE mesa
SET estado = 'ocupada'
WHERE id_mesa = 1;

SAVEPOINT cambio_mesa;

UPDATE mesa
SET estado = 'mantenimiento'
WHERE id_mesa = 2;

ROLLBACK TO SAVEPOINT cambio_mesa;

COMMIT;
```

**Explicación:** el primer cambio se conserva, mientras que el segundo se revierte. El `COMMIT` confirma únicamente los cambios que permanecieron después del punto de restauración.

## 9. Transacción fallida y comprobación

Se debe comprobar qué sucede cuando una operación viola una restricción de clave foránea.

```sql
BEGIN;

INSERT INTO reserva (
    id_cliente,
    id_mesa,
    fecha_hora,
    numero_personas,
    estado
)
VALUES (
    999999,
    NULL,
    CURRENT_TIMESTAMP + INTERVAL '1 day',
    2,
    'pendiente'
);

COMMIT;
```

**Explicación:** si no existe el cliente con identificador `999999`, PostgreSQL debe rechazar la inserción por incumplimiento de la clave foránea. La transacción quedará en estado de error y no podrá confirmarse.

Para cancelar la transacción fallida:

```sql
ROLLBACK;
```

Para comprobar que no se haya insertado el registro:

```sql
SELECT *
FROM reserva
WHERE id_cliente = 999999;
```

**Resultado esperado:** la consulta no debe devolver registros.

## 10. Consideraciones de seguridad

- Realizar un respaldo antes de ejecutar operaciones que modifiquen o eliminen información.
- Utilizar `ROLLBACK` en las pruebas de eliminación y actualización.
- Evitar borrar físicamente pedidos, clientes y platillos relacionados con el historial.
- Utilizar borrado lógico cuando se necesite conservar información histórica.
- Comprobar que los identificadores utilizados existan antes de ejecutar inserciones.
- Ejecutar las transacciones en el orden adecuado para respetar las relaciones entre tablas.

**Conclusión:** las operaciones anteriores permiten modificar la información del restaurante de forma controlada, aprovechar las transacciones de PostgreSQL y conservar la integridad de los datos relacionados con clientes, empleados, mesas, reservaciones y pedidos.
