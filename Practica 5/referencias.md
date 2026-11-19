# 2.1 y 2.2. Referencias y acciones referenciales

## 2.1. Referencias entre tablas

Las claves foráneas permiten relacionar las tablas de la base de datos y mantener la integridad referencial. Cada referencia establece qué registro de otra tabla debe existir para que una operación sea válida.

El modelo conserva las tablas originales del proyecto y añade las entidades `ADMINISTRADOR`, `MESA` y `RESERVA` para ampliar las funciones del restaurante.

### A) Relaciones del modelo original

| Tabla dependiente | Columna FK | Tabla referenciada | Columna PK | Nulabilidad |
|---|---|---|---|---|
| MESERO | id_empleado | EMPLEADO | id_empleado | NOT NULL |
| CHEF | id_empleado | EMPLEADO | id_empleado | NOT NULL |
| CLIENTE | — | — | — | No aplica |
| TELEFONO_CLIENTE | id_cliente | CLIENTE | id_cliente | NOT NULL |
| PLATILLO | id_empleado | CHEF | id_empleado | NOT NULL |
| ASIGNACION_CHEF_PLATILLO | id_empleado | CHEF | id_empleado | NOT NULL |
| ASIGNACION_CHEF_PLATILLO | id_platillo | PLATILLO | id_platillo | NOT NULL |
| PEDIDO | id_cliente | CLIENTE | id_cliente | NOT NULL |
| PEDIDO | id_mesero | MESERO | id_empleado | NOT NULL |
| DETALLE_PEDIDO | id_pedido | PEDIDO | id_pedido | NOT NULL |
| DETALLE_PEDIDO | id_platillo | PLATILLO | id_platillo | NOT NULL |

**Observación:** `PLATILLO.id_empleado` representa al chef responsable del platillo, mientras que `ASIGNACION_CHEF_PLATILLO` permite registrar la asignación de varios chefs a distintos platillos.

### B) Relaciones añadidas al modelo

| Tabla dependiente | Columna FK | Tabla referenciada | Columna PK | Nulabilidad |
|---|---|---|---|---|
| ADMINISTRADOR | id_empleado | EMPLEADO | id_empleado | NOT NULL |
| MESA | — | — | — | No aplica |
| RESERVA | id_cliente | CLIENTE | id_cliente | NOT NULL |
| RESERVA | id_mesa | MESA | id_mesa | NULL permitido |
| PEDIDO | id_mesa | MESA | id_mesa | NOT NULL |

**Justificación de las nuevas relaciones:**

- **ADMINISTRADOR–EMPLEADO:** el administrador es un subtipo de empleado. Su identificador también debe existir en `EMPLEADO`.
- **RESERVA–CLIENTE:** toda reservación debe pertenecer a un cliente registrado.
- **RESERVA–MESA:** una reserva puede registrarse antes de asignar una mesa, por lo que `id_mesa` permite valores NULL.
- **PEDIDO–MESA:** cada pedido para consumo dentro del restaurante debe asociarse con una mesa. Esta referencia permite consultar los pedidos y las cuentas correspondientes a cada mesa.

La columna `PEDIDO.id_mesa` y las tablas `ADMINISTRADOR`, `MESA` y `RESERVA` deberán incorporarse mediante una modificación del esquema original.

## 2.2. Acciones referenciales ON DELETE y ON UPDATE

Las acciones referenciales determinan qué sucede con los registros dependientes cuando se elimina o modifica la clave primaria de un registro referenciado.

Se proponen las siguientes acciones para conservar la integridad de la información y evitar que se pierdan registros importantes del restaurante.

### A) Acciones ON DELETE

| Relación | Acción ON DELETE | Justificación |
|---|---|---|
| MESERO → EMPLEADO | CASCADE | Si se elimina un empleado, también se elimina su registro específico como mesero. |
| CHEF → EMPLEADO | CASCADE | El registro de chef depende directamente de la existencia del empleado. |
| ADMINISTRADOR → EMPLEADO | CASCADE | El registro de administrador debe desaparecer si se elimina su empleado correspondiente. |
| TELEFONO_CLIENTE → CLIENTE | CASCADE | Si se elimina un cliente, sus teléfonos asociados dejan de tener utilidad. |
| PLATILLO → CHEF | RESTRICT | No se debe eliminar un chef que todavía tenga platillos asociados. |
| ASIGNACION_CHEF_PLATILLO → CHEF | CASCADE | Al eliminar un chef, se eliminan sus asignaciones, sin borrar los platillos. |
| ASIGNACION_CHEF_PLATILLO → PLATILLO | CASCADE | Al eliminar un platillo, se eliminan sus registros de asignación. |
| PEDIDO → CLIENTE | RESTRICT | No se debe eliminar un cliente que tenga pedidos registrados, para conservar el historial de ventas. |
| PEDIDO → MESERO | RESTRICT | No se debe eliminar un mesero que tenga pedidos asociados. |
| PEDIDO → MESA | RESTRICT | No se debe eliminar una mesa que tenga pedidos históricos relacionados. |
| DETALLE_PEDIDO → PEDIDO | CASCADE | Si se elimina un pedido, sus detalles dejan de existir como registros independientes. |
| DETALLE_PEDIDO → PLATILLO | RESTRICT | No se debe eliminar un platillo que forme parte de pedidos históricos. |
| RESERVA → CLIENTE | RESTRICT | No se debe eliminar un cliente que tenga reservaciones registradas. |
| RESERVA → MESA | SET NULL | Si se elimina una mesa, la reservación permanece registrada, pero pierde su asignación de mesa. |

### B) Acciones ON UPDATE

Se propone utilizar `ON UPDATE CASCADE` en todas las relaciones de claves foráneas.

Esta acción permite que, si cambia el identificador de un registro principal, el nuevo valor se actualice automáticamente en las tablas dependientes.

| Relación | Acción ON UPDATE | Justificación |
|---|---|---|
| MESERO → EMPLEADO | CASCADE | Mantiene actualizado el identificador del mesero. |
| CHEF → EMPLEADO | CASCADE | Evita que el subtipo conserve una referencia anterior. |
| ADMINISTRADOR → EMPLEADO | CASCADE | Mantiene la relación con el empleado correspondiente. |
| TELEFONO_CLIENTE → CLIENTE | CASCADE | Actualiza la referencia del cliente en sus teléfonos. |
| PLATILLO → CHEF | CASCADE | Conserva la referencia al chef responsable. |
| ASIGNACION_CHEF_PLATILLO → CHEF | CASCADE | Actualiza las asignaciones cuando cambia el identificador del chef. |
| ASIGNACION_CHEF_PLATILLO → PLATILLO | CASCADE | Mantiene la relación con el platillo correspondiente. |
| PEDIDO → CLIENTE | CASCADE | Actualiza la referencia del cliente en sus pedidos. |
| PEDIDO → MESERO | CASCADE | Conserva la relación entre pedidos y meseros. |
| PEDIDO → MESA | CASCADE | Actualiza la mesa relacionada con el pedido. |
| DETALLE_PEDIDO → PEDIDO | CASCADE | Mantiene los detalles asociados al pedido correcto. |
| DETALLE_PEDIDO → PLATILLO | CASCADE | Actualiza la referencia del platillo en el detalle. |
| RESERVA → CLIENTE | CASCADE | Mantiene la referencia del cliente en sus reservaciones. |
| RESERVA → MESA | CASCADE | Actualiza la mesa asignada a una reservación. |

### C) Consideraciones sobre las acciones referenciales

1. **Conservación del historial:** las relaciones de pedidos con clientes, meseros, mesas y platillos utilizan `RESTRICT` para evitar eliminar información que pueda ser necesaria para consultar ventas anteriores.

2. **Eliminación de registros dependientes:** se utiliza `CASCADE` en tablas que dependen directamente de otra entidad y cuyos registros no tienen sentido de manera independiente, como los detalles de un pedido, los teléfonos de un cliente y las asignaciones de chefs.

3. **Reservaciones sin mesa asignada:** se utiliza `SET NULL` en la relación entre `RESERVA` y `MESA`, porque una reservación debe poder conservarse aunque la mesa asignada sea eliminada.

4. **Actualización de identificadores:** se establece `CASCADE` en las referencias para mantener la consistencia cuando se modifique una clave primaria. En la operación normal, los identificadores deberían permanecer estables.

5. **Borrado de empleados:** aunque se establezca `CASCADE` en las relaciones de especialización, no se recomienda eliminar empleados que tengan actividad histórica. En esos casos es preferible conservarlos mediante un estado de baja o inactividad.

6. **Borrado de platillos:** se recomienda desactivar los platillos que ya no se ofrecen en lugar de eliminarlos físicamente, especialmente si aparecen en pedidos anteriores.

**Nota de implementación:** las acciones indicadas representan la configuración propuesta para las restricciones de clave foránea. Las tablas y columnas nuevas deberán crearse antes de aplicar las referencias correspondientes. Si el esquema original utiliza nombres de columnas diferentes, deberán ajustarse las sentencias SQL para coincidir con los nombres reales.
