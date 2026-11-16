## Diccionario de Tipos de Dato por Tabla

### Tabla `EMPLEADO`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Empleado` | `SERIAL` (`INTEGER`) | 4 bytes | Identificador autoincremental único suficiente para gestionar la plantilla histórica de personal. |
| `Nombre` | `VARCHAR` | 100 | Almacena el nombre completo del trabajador sin desperdiciar espacio en cadenas de longitud variable. |
| `Telefono` | `dom_telefono` (`CHAR`) | 10 caracteres fijos | Los números telefónicos nacionales tienen exactamente 10 dígitos; la longitud fija optimiza el almacenamiento y valida el formato. |
| `FechaContratacion` | `DATE` | 4 bytes | Registra únicamente el día calendario de ingreso del empleado, sin requerir hora exacta. |
| `RFC` | `CHAR` | 13 caracteres fijos | El Registro Federal de Contribuyentes para personas físicas en México consta estrictamente de 13 caracteres alfanuméricos. |

---

### Tabla `MESERO`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Empleado` | `INTEGER` | 4 bytes | Coincide con el tipo base de `EMPLEADO.ID_Empleado` para implementar la especialización (herencia). |
| `Turno` | `tipo_turno` (`ENUM`) | Catálogo cerrado | Restringe el turno operativo exclusivamente a los valores válidos del negocio (`Matutino`, `Vespertino`, `Mixto`). |

---

### Tabla `CHEF`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Empleado` | `INTEGER` | 4 bytes | Coincide con el tipo base de `EMPLEADO.ID_Empleado` para implementar la especialización. |
| `Especialidad` | `VARCHAR` | 60 | Almacena el área culinaria principal del chef (ej. *Parrilla*, *Repostería*, *Mariscos*) con longitud flexible. |
| `AniosExperiencia` | `SMALLINT` | 2 bytes | Rango de -32,768 a 32,767; más que suficiente para representar años de trayectoria laboral humana sin desperdiciar bytes. |

---

### Tabla `CLIENTE`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Cliente` | `SERIAL` (`INTEGER`) | 4 bytes | Clave subrogada autoincremental capaz de registrar más de 2 mil millones de clientes. |
| `Nombre` | `VARCHAR` | 100 | Nombre completo del cliente con almacenamiento dinámico. |
| `Correo` | `VARCHAR` | 120 | Longitud estándar suficiente para direcciones de correo electrónico y validación sintáctica. |
| `Calle` | `VARCHAR` | 80 | Componente del atributo compuesto *Dirección*; soporta nombres extensos de vialidades. |
| `Numero` | `VARCHAR` | 15 | Admite números exteriores e interiores alfanuméricos (ej. `"104-B"`, `"S/N"`). |
| `Colonia` | `VARCHAR` | 80 | Componente del atributo compuesto *Dirección* que facilita consultas y repartos por zona. |
| `Telefono` | `dom_telefono` (`CHAR`) | 10 caracteres fijos | Teléfono principal de contacto bajo el estándar nacional de 10 dígitos exactos. |

---

### Tabla `TELEFONO_CLIENTE`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Cliente` | `INTEGER` | 4 bytes | Coincide exactamente con el tipo base de `CLIENTE.ID_Cliente`. |
| `Telefono` | `dom_telefono` (`CHAR`) | 10 caracteres fijos | Garantiza que todos los números secundarios cumplan con el mismo formato estricto de 10 dígitos. |

---

### Tabla `PLATILLO`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Platillo` | `SERIAL` (`INTEGER`) | 4 bytes | Identificador único autoincremental para los elementos de la carta. |
| `Nombre` | `VARCHAR` | 80 | Nombre comercial del platillo con longitud variable. |
| `Descripcion` | `TEXT` | Variable | Permite detallar ingredientes, alergenos y preparación sin un límite rígido de caracteres. |
| `Precio` | `dom_moneda` (`NUMERIC`) | (10, 2) | Precisión decimal exacta a dos centavos para evitar errores de redondeo en cobros. |
| `ID_Empleado` | `INTEGER` | 4 bytes | Referencia al chef principal responsable del diseño o supervisión del platillo (`CHEF.ID_Empleado`). |

---

### Tabla `ASIGNACION_CHEF_PLATILLO`

| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Empleado` | `INTEGER` | 4 bytes | Parte de la clave primaria compuesta; referencia a `CHEF.ID_Empleado`. |
| `ID_Platillo` | `INTEGER` | 4 bytes | Parte de la clave primaria compuesta; referencia a `PLATILLO.ID_Platillo`. |
| `FechaAsignacion` | `DATE` | 4 bytes | Atributo de relación que registra el día calendario en que se asignó el platillo al chef. |

---

### Tabla `PEDIDO`


| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Pedido` | `SERIAL` (`INTEGER`) | 4 bytes | Folio único autoincremental de la orden. |
| `FechaHora` | `TIMESTAMP` | 8 bytes | Almacena la fecha y hora exacta (hasta segundos) en que se registró la comanda para control de turnos y tiempos. |
| `ID_Cliente` | `INTEGER` | 4 bytes | Referencia al cliente que realiza el pedido (`CLIENTE.ID_Cliente`). |
| `ID_Mesero` | `INTEGER` | 4 bytes | Referencia al mesero que atendió la mesa (`MESERO.ID_Empleado`). |
| `Total` | `dom_moneda` (`NUMERIC`) | (10, 2) | Monto total de la venta en formato decimal exacto. |

---

### Tabla `DETALLE_PEDIDO`


| Columna | Tipo de dato | Longitud / Precisión | Justificación |
| :--- | :--- | :--- | :--- |
| `ID_Pedido` | `INTEGER` | 4 bytes | Parte de la clave primaria compuesta; referencia a `PEDIDO.ID_Pedido`. |
| `ID_Platillo` | `INTEGER` | 4 bytes | Parte de la clave primaria compuesta; referencia a `PLATILLO.ID_Platillo`. |
| `Cantidad` | `SMALLINT` | 2 bytes | Cantidad de unidades solicitadas de un mismo platillo en la orden; `SMALLINT` cubre con holgura cualquier comanda. |
| `PrecioUnitario` | `dom_moneda` (`NUMERIC`) | (10, 2) | Congela el precio histórico del platillo al momento de la venta con exactitud decimal. |
| `Subtotal` | `dom_moneda` (`NUMERIC`) | (10, 2) | Resultado exacto de `Cantidad * PrecioUnitario` sin imprecisiones de punto flotante. |

