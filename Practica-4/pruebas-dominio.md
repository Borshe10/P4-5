
---

## Caso 1: 

* **Regla del dominio protegida:** Todo empleado debe tener nombre, teléfono, fecha de contratación y RFC registrados para su expediente.

### Consulta SQL ejecutada
```sql
INSERT INTO EMPLEADO (Nombre, Telefono, FechaContratacion, RFC)
VALUES ('Pedro Ramírez Solís', '5512345678', '2026-10-15', NULL);
```

### Salida del gestor 
```text
ERROR:  null value in column "rfc" of relation "empleado" violates not-null constraint
DETAIL:  Failing row contains (41, Pedro Ramírez Solís, 5512345678, 2026-10-15, null).
```

---

## Caso 2: 

* **Regla del dominio protegida:** Todo pedido nuevo toma la fecha y hora exacta del sistema al abrirse e inicia con total en `$0.00`.

### Consulta SQL ejecutada
```sql
INSERT INTO PEDIDO (ID_Cliente, ID_Mesero)
VALUES (1, 1)
RETURNING ID_Pedido, FechaHora, Total;
```

### Salida del gestor 
```text
 id_pedido |         fechahora          | total
-----------+----------------------------+-------
       401 | 2026-11-16 21:25:10.482911 |  0.00
(1 row)

INSERT 0 1
```

---

## Caso 3: 

* **Regla del dominio protegida:** Dos empleados distintos no pueden compartir el mismo RFC fiscal.

### Consulta SQL ejecutada
```sql
INSERT INTO EMPLEADO (Nombre, Telefono, FechaContratacion, RFC)
SELECT 'Laura Méndez Ortiz', '5598765432', '2026-09-01', RFC
FROM EMPLEADO WHERE ID_Empleado = 1;
```

### Salida del gestor 
```text
ERROR:  duplicate key value violates unique constraint "uq_empleado_rfc"
DETAIL:  Key (rfc)=(HEGC850412A9B) already exists.
```

---

## Caso 4: 

* **Regla del dominio protegida:** Un mismo platillo no debe aparecer duplicado en renglones separados dentro del mismo pedido.

### Consulta SQL ejecutada
```sql
INSERT INTO DETALLE_PEDIDO (ID_Pedido, ID_Platillo, Cantidad, PrecioUnitario, Subtotal)
SELECT ID_Pedido, ID_Platillo, 2, PrecioUnitario, 2 * PrecioUnitario
FROM DETALLE_PEDIDO
LIMIT 1;
```

### Salida del gestor 
```text
ERROR:  duplicate key value violates unique constraint "uq_detalle_pedido_platillo"
DETAIL:  Key (id_pedido, id_platillo)=(1, 45) already exists.
```

---

## Caso 5: 

* **Regla del dominio protegida:** Todo número telefónico debe constar exactamente de 10 dígitos numéricos nacionales.

### Consulta SQL ejecutada
```sql
INSERT INTO CLIENTE (Nombre, Correo, Calle, Numero, Colonia, Telefono)
VALUES ('Sofía Castro', 'sofia.castro.test@gmail.com', 'Calle Durango', '45', 'Roma Norte', '551234AB');
```

### Salida del gestor 
```text
ERROR:  value for domain dom_telefono violates check constraint "dom_telefono_check"
```

---

## Caso 6: 

* **Regla del dominio protegida:** El RFC del empleado debe cumplir con la estructura oficial mexicana de 13 caracteres (4 letras, 6 dígitos de fecha y 3 de homoclave).

### Consulta SQL ejecutada
```sql
INSERT INTO EMPLEADO (Nombre, Telefono, FechaContratacion, RFC)
VALUES ('Jorge Navarro', '5544332211', '2026-05-10', '1234900101ABC');
```

### Salida del gestor 
```text
ERROR:  new row for relation "empleado" violates check constraint "chk_empleado_rfc_formato"
DETAIL:  Failing row contains (42, Jorge Navarro, 5544332211, 2026-05-10, 1234900101ABC).
```

---

## Caso 7: 

* **Regla del dominio protegida:** El correo electrónico del cliente debe contener un usuario, un arroba (`@`) y un dominio válido.

### Consulta SQL ejecutada
```sql
INSERT INTO CLIENTE (Nombre, Correo, Calle, Numero, Colonia, Telefono)
VALUES ('Andrés Morales', 'andres.morales.sin.arroba.com', 'Av. Reforma', '120', 'Juárez', '5566778899');
```

### Salida del gestor 
```text
ERROR:  new row for relation "cliente" violates check constraint "chk_cliente_correo_formato"
DETAIL:  Failing row contains (251, Andrés Morales, andres.morales.sin.arroba.com, Av. Reforma, 120, Juárez, 5566778899).
```

---

## Caso 8: 

* **Regla del dominio protegida:** La especialidad de un chef debe pertenecer a las áreas culinarias autorizadas del restaurante.

### Consulta SQL ejecutada
```sql
WITH nuevo_emp AS (
    INSERT INTO EMPLEADO (Nombre, Telefono, FechaContratacion, RFC)
    VALUES ('Marco Polo Chef', '5511223344', '2026-01-15', 'POMM880315XYZ')
    RETURNING ID_Empleado
)
INSERT INTO CHEF (ID_Empleado, Especialidad, AniosExperiencia)
SELECT ID_Empleado, 'Comida Rápida', 5 FROM nuevo_emp;
```

### Salida del gestor 
```text
ERROR:  new row for relation "chef" violates check constraint "chk_chef_especialidad_valida"
DETAIL:  Failing row contains (43, Comida Rápida, 5).
```

---

## Caso 9: 

* **Regla del dominio protegida:** Ningún empleado puede registrarse con una fecha de contratación futura ni anterior a la fundación del restaurante (`2010-01-01`).

### Consulta SQL ejecutada
```sql
INSERT INTO EMPLEADO (Nombre, Telefono, FechaContratacion, RFC)
VALUES ('Elena Ríos', '5599887766', '2030-01-01', 'RIEL950720H12');
```

### Salida del gestor 
```text
ERROR:  new row for relation "empleado" violates check constraint "chk_empleado_fecha_contratacion"
DETAIL:  Failing row contains (44, Elena Ríos, 5599887766, 2030-01-01, RIEL950720H12).
```

---

## Caso 10: Violación de `CHECK` entre columnas (`chk_detalle_subtotal_exacto`)

* **Regla del dominio protegida:** El subtotal de cada renglón del detalle debe ser exactamente igual a la cantidad multiplicada por el precio unitario.

### Consulta SQL ejecutada
```sql
INSERT INTO DETALLE_PEDIDO (ID_Pedido, ID_Platillo, Cantidad, PrecioUnitario, Subtotal)
VALUES (1, 200, 3, 150.00, 200.00);
```

### Salida del gestor 
```text
ERROR:  new row for relation "detalle_pedido" violates check constraint "chk_detalle_subtotal_exacto"
DETAIL:  Failing row contains (1, 200, 3, 150.00, 200.00).
```
