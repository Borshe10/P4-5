# Ejercicio 2.6 
## Cambio de acción referencial: PEDIDO → MESA

**Integrante responsable:** Eugenio Arredondo Ari Sebastian
### 1. Relación seleccionada

La tabla `PEDIDO` contiene la clave foránea `id_mesa`, que referencia a `MESA(id_mesa)`. Esta relación permite identificar en qué mesa se atiende cada pedido.

### 2. Acción referencial original

- **ON DELETE:** `RESTRICT`
- **ON UPDATE:** `CASCADE`

Con `ON DELETE RESTRICT`, PostgreSQL impide eliminar una mesa cuando existen pedidos asociados. Esto protege el historial de pedidos y evita que queden registros sin una mesa válida.

Con `ON UPDATE CASCADE`, si cambia el identificador de una mesa, el cambio se propaga a los pedidos relacionados.

### 3. Cambio propuesto

Cambiar la acción `ON DELETE RESTRICT` por `ON DELETE SET NULL`, conservando `ON UPDATE CASCADE`.

La columna `PEDIDO.id_mesa` debe permitir valores `NULL` para que esta acción pueda aplicarse. Si todos los pedidos deben estar asociados obligatoriamente a una mesa, esta propuesta no es compatible con la regla del sistema y debe mantenerse `RESTRICT`.

### 4. SQL de referencia

Ajustar el nombre de la restricción al que exista realmente en la base de datos:

```sql
ALTER TABLE pedido
DROP CONSTRAINT IF EXISTS pedido_id_mesa_fkey;

ALTER TABLE pedido
ADD CONSTRAINT pedido_id_mesa_fkey
FOREIGN KEY (id_mesa)
REFERENCES mesa(id_mesa)
ON DELETE SET NULL
ON UPDATE CASCADE;
```

Si la columna todavía está definida como `NOT NULL`, y el diseño permite pedidos sin mesa, se puede modificar así:

```sql
ALTER TABLE pedido
ALTER COLUMN id_mesa DROP NOT NULL;
```

### 5. Prueba del comportamiento

La prueba debe realizarse en una copia de la base de datos o dentro de una transacción que se revierta.

```sql
BEGIN;

-- Consultar una mesa que tenga pedidos asociados.
SELECT m.id_mesa, p.id_pedido
FROM mesa AS m
JOIN pedido AS p ON p.id_mesa = m.id_mesa
LIMIT 5;

-- Sustituir el valor por un id_mesa existente y de prueba.
DELETE FROM mesa
WHERE id_mesa = <ID_MESA_DE_PRUEBA>;

-- Comprobar que los pedidos relacionados conservan su registro
-- y que id_mesa quedó en NULL.
SELECT id_pedido, id_mesa
FROM pedido
WHERE id_mesa IS NULL;

ROLLBACK;
```

### 6. Resultado esperado y análisis

Al eliminar una mesa referenciada, los pedidos deben conservarse y su campo `id_mesa` debe quedar en `NULL`. Así se mantiene el historial de pedidos, aunque se pierde la asociación con la mesa eliminada.

La ventaja es que permite retirar mesas sin borrar pedidos. La desventaja es que algunos pedidos dejan de tener una mesa identificada. Por ello, `SET NULL` solo debe utilizarse si el negocio permite conservar pedidos sin una mesa asociada.
