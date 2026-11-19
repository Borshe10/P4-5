# Pruebas de Control de Acceso y Matriz de Permisos

---

## Pruebas de control de acceso y revocación

### A. Pruebas con `usr_consulta_restaurante` 

* **Operación permitida :**

```sql
SET ROLE usr_consulta_restaurante;
SELECT ID_Platillo, Nombre, Precio FROM PLATILLO LIMIT 2;
```

**Salida del gestor:**

```text
 id_platillo |          nombre           | precio
-------------+---------------------------+--------
           1 | Tacos al Pastor Especial  | 145.00
           2 | Enchiladas Suizas Casera  | 168.50
(2 rows)
```

* **Operación negada :**

```sql
INSERT INTO PLATILLO (Nombre, Descripcion, Precio, ID_Empleado)
VALUES ('Platillo No Autorizado', 'Intento de inserción', 99.00, 26);
```

**Mensaje del gestor:**

```text
ERROR:  permission denied for table platillo
```

---

### Pruebas con `usr_app_restaurante`

* **Operación permitida :**

```sql
RESET ROLE;
SET ROLE usr_app_restaurante;
UPDATE PLATILLO SET Precio = Precio WHERE ID_Platillo = 1;
```

**Salida del gestor:**

```text
UPDATE 1
```

* **Operación negada:**

```sql
DELETE FROM PEDIDO WHERE ID_Pedido = 1;
```

**Mensaje del gestor:**

```text
ERROR:  permission denied for table pedido
```

---

### Pruebas con `usr_admin_restaurante`

* **Operación permitida :**

```sql
RESET ROLE;
SET ROLE usr_admin_restaurante;
COMMENT ON TABLE PEDIDO IS 'Registro histórico de comandas del restaurante';
```

**Salida del gestor:**

```text
COMMENT
```

* **Operación negada:**

```sql
CREATE USER intruso WITH SUPERUSER;
```

**Mensaje del gestor:**

```text
ERROR:  permission denied to create role
DETAIL:  Only roles with the CREATEROLE attribute may create roles.
```

---

### Demostración de revocación de privilegios

Se retira el permiso de `UPDATE` sobre la tabla `PLATILLO` al rol `rol_app_restaurante` para impedir que la aplicación modifique precios del menú sin autorización administrativa:

```sql
RESET ROLE;
REVOKE UPDATE ON PLATILLO FROM rol_app_restaurante;
```

**Salida del gestor:**

```text
REVOKE
```

Al intentar nuevamente actualizar un precio con el usuario de la aplicación:

```sql
SET ROLE usr_app_restaurante;
UPDATE PLATILLO SET Precio = 180.00 WHERE ID_Platillo = 1;
```

**Mensaje del gestor tras el `REVOKE`:**

```text
ERROR:  permission denied for table platillo
```



---

## Matriz de permisos por rol y tabla

| Tabla / Objeto | `rol_admin_restaurante` | `rol_app_restaurante` | `rol_consulta_restaurante` |
| :--- | :---: | :---: | :---: |
| **`EMPLEADO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`MESERO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`CHEF`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`CLIENTE`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`TELEFONO_CLIENTE`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE, DELETE` | `SELECT` |
| **`PLATILLO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT` *(y `UPDATE` revocable)* | `SELECT` |
| **`ASIGNACION_CHEF_PLATILLO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`PEDIDO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **`DETALLE_PEDIDO`** | `SELECT, INSERT, UPDATE, DELETE` + DDL | `SELECT, INSERT, UPDATE` | `SELECT` |
| **Secuencias (`*_seq`)** | `ALL PRIVILEGES` | `USAGE, SELECT` | *Sin acceso* |
| **Base de datos (`CREATE TEMP`)** | `CONNECT, CREATE, TEMPORARY` | `CONNECT, TEMPORARY` | `CONNECT` |