# Ejercicio 2.6 
## Cambio de acción referencial: ADMINISTRADOR → EMPLEADO

*Integrante responsable:* Alvarez Hernandez Miguel Angel

### 1. Relación seleccionada

La tabla ADMINISTRADOR funciona como subtipo de EMPLEADO. Su atributo id_empleado es simultáneamente clave primaria de ADMINISTRADOR y clave foránea que referencia EMPLEADO(id_empleado).

Esta relación indica que cada administrador corresponde a un empleado registrado.

### 2. Acción referencial original

- *ON DELETE:* CASCADE
- *ON UPDATE:* CASCADE

Con ON DELETE CASCADE, al eliminar un empleado también se elimina automáticamente su registro correspondiente en ADMINISTRADOR.

Con ON UPDATE CASCADE, cualquier cambio en el identificador del empleado se propaga al registro del administrador.

### 3. Cambio propuesto

Cambiar la acción ON DELETE CASCADE por ON DELETE RESTRICT, conservando ON UPDATE CASCADE.

Con RESTRICT, PostgreSQL impedirá eliminar físicamente un empleado mientras exista su registro como administrador. Esto evita que la eliminación de un empleado borre automáticamente información del subtipo.

### 4. SQL de referencia

Ajustar el nombre de la restricción al que exista realmente en la base de datos:

sql
ALTER TABLE administrador
DROP CONSTRAINT IF EXISTS administrador_id_empleado_fkey;

ALTER TABLE administrador
ADD CONSTRAINT administrador_id_empleado_fkey
FOREIGN KEY (id_empleado)
REFERENCES empleado(id_empleado)
ON DELETE RESTRICT
ON UPDATE CASCADE;

### 5. Prueba del comportamiento

La prueba debe realizarse en una copia de la base de datos o dentro de una transacción que se revierta.

sql
BEGIN;

-- Consultar un empleado que también esté registrado como administrador.
SELECT e.id_empleado
FROM empleado AS e
JOIN administrador AS a
  ON a.id_empleado = e.id_empleado
LIMIT 5;

-- Sustituir el valor por un id_empleado existente de prueba.
DELETE FROM empleado
WHERE id_empleado = <ID_EMPLEADO_ADMINISTRADOR>;

-- La eliminación debe ser rechazada por la restricción RESTRICT.

ROLLBACK;

### 6. Resultado esperado y análisis

PostgreSQL debe rechazar el DELETE del empleado mientras exista el registro relacionado en ADMINISTRADOR. El registro del empleado y el del administrador permanecen intactos.

La ventaja es que se evita eliminar accidentalmente información de un administrador al borrar un empleado. La desventaja es que, para retirar a un administrador, primero habría que eliminar o modificar su registro en ADMINISTRADOR; además, deben considerarse las reglas del sistema para conservar el historial laboral.
