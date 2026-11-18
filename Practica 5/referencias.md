El modelo de datos del restaurante contempla las siguientes entidades:

- empleado
- mesero
- chef
- administrador
- cliente
- mesa
- reserva
- pedido
- platillo
- detalle_pedido
- platillo_chef

Las relaciones entre las tablas se establecen mediante claves primarias (PK) y claves foráneas (FK).

### Relaciones referenciales propuestas

| Tabla | Campo FK | Tabla referenciada | Campo referenciado |
|---|---|---|---|
| mesero | id_empleado | empleado | id_empleado |
| chef | id_empleado | empleado | id_empleado |
| administrador | id_empleado | empleado | id_empleado |
| pedido | id_cliente | cliente | id_cliente |
| pedido | id_mesero | mesero | id_empleado |
| pedido | id_mesa | mesa | id_mesa |
| reserva | id_cliente | cliente | id_cliente |
| reserva | id_mesa | mesa | id_mesa |
| detalle_pedido | id_pedido | pedido | id_pedido |
| detalle_pedido | id_platillo | platillo | id_platillo |
| platillo_chef | id_chef | chef | id_empleado |
| platillo_chef | id_platillo | platillo | id_platillo |
