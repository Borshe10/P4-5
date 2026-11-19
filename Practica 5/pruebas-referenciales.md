# 2.3. Pruebas de integridad referencial

## Objetivo

Comprobar que las claves foráneas de la base de datos del restaurante funcionen correctamente y que las acciones `ON DELETE` y `ON UPDATE` mantengan la integridad de la información.

Las pruebas consideran las tablas originales y las nuevas entidades `ADMINISTRADOR`, `MESA` y `RESERVA`.

## 1. Pruebas de relaciones y acciones referenciales

| No. | Relación | Operación de prueba | Resultado esperado |
|---|---|---|---|
| 1 | MESERO → EMPLEADO | Eliminar un empleado que tenga un registro en MESERO. | El registro correspondiente en MESERO se elimina mediante CASCADE. |
| 2 | CHEF → EMPLEADO | Actualizar el identificador de un empleado que tenga un registro en CHEF. | El identificador también se actualiza en CHEF mediante CASCADE. |
| 3 | ADMINISTRADOR → EMPLEADO | Eliminar un empleado que tenga un registro en ADMINISTRADOR. | El registro dependiente se elimina mediante CASCADE. |
| 4 | TELEFONO_CLIENTE → CLIENTE | Eliminar un cliente que tenga teléfonos registrados. | Los teléfonos asociados se eliminan mediante CASCADE. |
| 5 | PLATILLO → CHEF | Eliminar un chef que tenga platillos asignados como responsable. | La operación se rechaza mediante RESTRICT. |
| 6 | ASIGNACION_CHEF_PLATILLO → CHEF | Eliminar un chef con asignaciones registradas. | Se eliminan sus asignaciones, sin eliminar los platillos. |
| 7 | PEDIDO → CLIENTE | Eliminar un cliente que tenga pedidos registrados. | La operación se rechaza mediante RESTRICT. |
| 8 | PEDIDO → MESERO | Eliminar un mesero que tenga pedidos registrados. | La operación se rechaza mediante RESTRICT. |
| 9 | PEDIDO → MESA | Eliminar una mesa que tenga pedidos históricos. | La operación se rechaza mediante RESTRICT. |
| 10 | DETALLE_PEDIDO → PEDIDO | Eliminar un pedido que tenga detalles. | Los detalles asociados se eliminan mediante CASCADE. |
| 11 | DETALLE_PEDIDO → PLATILLO | Eliminar un platillo que aparezca en detalles de pedidos. | La operación se rechaza mediante RESTRICT. |
| 12 | RESERVA → CLIENTE | Eliminar un cliente que tenga reservaciones. | La operación se rechaza mediante RESTRICT. |
| 13 | RESERVA → MESA | Eliminar una mesa asignada a una reservación. | La reservación permanece y su id_mesa cambia a NULL. |
| 14 | RESERVA → CLIENTE | Actualizar el identificador de un cliente con reservaciones. | La referencia se actualiza mediante CASCADE. |
| 15 | PEDIDO → MESA | Actualizar el identificador de una mesa con pedidos. | La referencia se actualiza mediante CASCADE. |

## 2. Pruebas de rechazo de claves foráneas inexistentes

También se debe comprobar que el sistema no permita insertar registros que hagan referencia a identificadores inexistentes.

| No. | Tabla | Operación | Resultado esperado |
|---|---|---|---|
| 1 | MESERO | Insertar un mesero con un id_empleado inexistente. | Rechazar el INSERT. |
| 2 | CHEF | Insertar un chef con un id_empleado inexistente. | Rechazar el INSERT. |
| 3 | ADMINISTRADOR | Insertar un administrador con un id_empleado inexistente. | Rechazar el INSERT. |
| 4 | TELEFONO_CLIENTE | Insertar un teléfono con un id_cliente inexistente. | Rechazar el INSERT. |
| 5 | ASIGNACION_CHEF_PLATILLO | Insertar una asignación con un chef inexistente. | Rechazar el INSERT. |
| 6 | ASIGNACION_CHEF_PLATILLO | Insertar una asignación con un platillo inexistente. | Rechazar el INSERT. |
| 7 | PEDIDO | Insertar un pedido con un cliente inexistente. | Rechazar el INSERT. |
| 8 | PEDIDO | Insertar un pedido con un mesero inexistente. | Rechazar el INSERT. |
| 9 | PEDIDO | Insertar un pedido con una mesa inexistente. | Rechazar el INSERT. |
| 10 | DETALLE_PEDIDO | Insertar un detalle con un pedido inexistente. | Rechazar el INSERT. |
| 11 | DETALLE_PEDIDO | Insertar un detalle con un platillo inexistente. | Rechazar el INSERT. |
| 12 | RESERVA | Insertar una reserva con un cliente inexistente. | Rechazar el INSERT. |
| 13 | RESERVA | Insertar una reserva con una mesa inexistente. | Rechazar el INSERT. |

## 3. Comprobación de registros huérfanos

Un registro huérfano es aquel que contiene una clave foránea cuyo valor no corresponde con una clave primaria existente.

Las siguientes consultas permiten verificar que no existan registros huérfanos:

```sql
SELECT m.*
FROM mesero m
LEFT JOIN empleado e ON m.id_empleado = e.id_empleado
WHERE e.id_empleado IS NULL;

SELECT c.*
FROM chef c
LEFT JOIN empleado e ON c.id_empleado = e.id_empleado
WHERE e.id_empleado IS NULL;

SELECT a.*
FROM administrador a
LEFT JOIN empleado e ON a.id_empleado = e.id_empleado
WHERE e.id_empleado IS NULL;

SELECT t.*
FROM telefono_cliente t
LEFT JOIN cliente c ON t.id_cliente = c.id_cliente
WHERE c.id_cliente IS NULL;

SELECT p.*
FROM pedido p
LEFT JOIN cliente c ON p.id_cliente = c.id_cliente
WHERE c.id_cliente IS NULL;

SELECT p.*
FROM pedido p
LEFT JOIN mesero m ON p.id_mesero = m.id_empleado
WHERE m.id_empleado IS NULL;

SELECT p.*
FROM pedido p
LEFT JOIN mesa me ON p.id_mesa = me.id_mesa
WHERE me.id_mesa IS NULL;

SELECT d.*
FROM detalle_pedido d
LEFT JOIN pedido p ON d.id_pedido = p.id_pedido
WHERE p.id_pedido IS NULL;

SELECT d.*
FROM detalle_pedido d
LEFT JOIN platillo p ON d.id_platillo = p.id_platillo
WHERE p.id_platillo IS NULL;

SELECT r.*
FROM reserva r
LEFT JOIN cliente c ON r.id_cliente = c.id_cliente
WHERE c.id_cliente IS NULL;

SELECT r.*
FROM reserva r
LEFT JOIN mesa m ON r.id_mesa = m.id_mesa
WHERE r.id_mesa IS NOT NULL
  AND m.id_mesa IS NULL;
```

**Resultado esperado:** todas las consultas deben devolver cero registros. En la última consulta se excluyen las reservas sin mesa asignada, porque `id_mesa` puede ser NULL.

## 4. Comprobación de duplicados en tablas puente

La tabla `ASIGNACION_CHEF_PLATILLO` representa la relación entre chefs y platillos. Se debe verificar que no existan asignaciones repetidas para el mismo par de identificadores.

```sql
SELECT id_empleado, id_platillo, COUNT(*)
FROM asignacion_chef_platillo
GROUP BY id_empleado, id_platillo
HAVING COUNT(*) > 1;
```

**Resultado esperado:** cero registros. La combinación de `id_empleado` e `id_platillo` debe ser única.

## 5. Comprobación de valores nulos indebidos

Las claves foráneas obligatorias no deben contener valores NULL. Se pueden verificar con las siguientes consultas:

```sql
SELECT *
FROM pedido
WHERE id_cliente IS NULL
   OR id_mesero IS NULL
   OR id_mesa IS NULL;

SELECT *
FROM reserva
WHERE id_cliente IS NULL;

SELECT *
FROM detalle_pedido
WHERE id_pedido IS NULL
   OR id_platillo IS NULL;
```

**Resultado esperado:** cero registros. Se permite que `reserva.id_mesa` tenga valores NULL cuando todavía no se haya asignado una mesa.

## 6. Registro de resultados

Para cada prueba realizada se deberá registrar:

- Operación ejecutada.
- Datos utilizados para la prueba.
- Resultado esperado.
- Resultado obtenido en PostgreSQL.
- Mensaje de error, cuando corresponda.
- Regla de integridad que se está comprobando.

Las pruebas de eliminación y actualización deben ejecutarse dentro de transacciones con `ROLLBACK`, para evitar modificar o perder los datos originales.

**Conclusión:** estas pruebas permiten comprobar que las relaciones entre empleados, clientes, platillos, pedidos, mesas y reservaciones se mantengan consistentes, evitando referencias inexistentes y eliminaciones accidentales de información histórica.
