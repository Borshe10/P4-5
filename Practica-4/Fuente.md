# Fuente de Datos del Proyecto Propio: Sistema de Gestión para Restaurante

## 1. Búsqueda previa de conjuntos de datos publicados y justificación

### Portales consultados y términos de búsqueda

| Portal / Repositorio | Términos de búsqueda utilizados | Resultados encontrados y motivo de descarte |
| :--- | :--- | :--- |
| **Datos Abiertos de la Ciudad de México** (`datos.cdmx.gob.mx`) | `"restaurantes"`, `"establecimientos mercantiles"`, `"ventas alimentos"`, `"comandas"` | Solo ofrece directorios administrativos de establecimientos (razón social, alcaldía y giro), sin información operativa interna de pedidos, platillos ni personal. |
| **INEGI — DENUE** (`inegi.org.mx/app/mapa/denue/`) | `"servicios de preparación de alimentos y bebidas"`, `"restaurantes con servicio de meseros"` | Contiene ubicación geográfica y tamaño del establecimiento, pero carece de transacciones, menús, precios unitarios o asignaciones de cocina. |


### Conclusión y justificación de datos sintéticos
Se concluye que **no existe un conjunto de datos público que cubra la integridad relacional y operativa de este dominio**, ya que los registros internos de recursos humanos (RFC, fechas de contratación, turnos), asignación culinaria (`ASIGNACION_CHEF_PLATILLO`) y comandas detalladas (`PEDIDO` + `DETALLE_PEDIDO`) constituyen información privada de cada negocio.

Por ello, se desarrolló un **script generador determinista en Python** (usando la biblioteca `Faker` con localización `es_MX` y catálogos reales de gastronomía mexicana y colonias de la Ciudad de México) que produce datos sintéticos estadísticamente variados y 100% compatibles con las restricciones de dominio definidas en `001-dominios.sql`. **Todos los datos cargados en las tablas son sintéticos.**

---

## 2. Referencia de las fuentes de apoyo utilizadas (APA 7.ª edición)

Para dar realismo geográfico y gastronómico a los registros generados, se tomaron como referencia catálogos abiertos para nombres de vialidades, colonias y platillos típicos:

* Correos de México. (2026). *Catálogo Nacional de Códigos Postales (Asentamientos y Colonias de la Ciudad de México)* [Conjunto de datos]. Gobierno de México. https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
  * **Licencia y uso:** Libre Uso MX (Datos Abiertos del Gobierno de México). Permite copiar, distribuir, adaptar y utilizar los nombres de colonias para poblar los atributos de dirección de clientes.
* Biblioteca `Faker` Contributors. (2026). *Faker: Python package that generates fake data (Locale `es_MX`)* (Versión 30.8.0) [Software]. GitHub. https://github.com/joke2k/faker
  * **Licencia y uso:** Licencia MIT. Permite la generación libre de nombres, correos electrónicos, teléfonos a 10 dígitos y fechas coherentes para entornos de prueba académicos.

---

## 3. Especificaciones del conjunto de datos generado

* **Formato:** Archivos planos separados por comas (`.csv`) codificados en `UTF-8` sin BOM, almacenados en `practica4/datos/` para su ingesta masiva mediante `COPY`.
* **Tamaño aproximado:** ~185 KB en total entre los 9 archivos CSV.
* **Volumen de registros por tabla** (superando el mínimo requerido de 200 renglones en tablas principales):

| Archivo CSV | Tabla destino | Cantidad de registros | 
| :--- | :--- | :---: | 
| `01_empleados.csv` | `EMPLEADO` | 40 | 
| `02_meseros.csv` | `MESERO` | 25 | 
| `03_chefs.csv` | `CHEF` | 15 | 
| `04_clientes.csv` | `CLIENTE` | 250 | 
| `05_telefonos_cliente.csv` | `TELEFONO_CLIENTE` | 310 | 
| `06_platillos.csv` | `PLATILLO` | 210 | 
| `07_asignacion_chef_platillo.csv` | `ASIGNACION_CHEF_PLATILLO` | 320 |
| `08_pedidos.csv` | `PEDIDO` | 400 | 
| `09_detalle_pedido.csv` | `DETALLE_PEDIDO` | 1,150 | 

---
