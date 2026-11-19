# 2.5. Integridad referencial del almacén de datos

## Objetivo

Analizar la integridad referencial del almacén de datos correspondiente al proyecto asignado **Sistema de Visualización de Datos Sísmicos de México**, identificando la tabla de hechos, sus dimensiones y las relaciones necesarias para mantener la consistencia de la información.

## 1. Descripción del proyecto

El proyecto trabaja con información de eventos sísmicos en México y permite relacionar sus características con información geográfica, temporal y económica.

La información se utiliza para realizar consultas y visualizaciones que permitan analizar la distribución de los sismos, sus magnitudes, profundidades y relación con las entidades federativas.

El repositorio del proyecto contiene estructuras relacionadas con las siguientes dimensiones:

| Tabla | Información almacenada |
|---|---|
| dim_sismos | Magnitud, latitud, longitud, profundidad y referencia de localización del evento sísmico. |
| dim_tiempo | Hora UTC, fecha, año, mes, día y trimestre. |
| dim_zonas | Entidad, nombre de entidad y datos de población. |
| dim_economia | Producción bruta total, insumos utilizados, consumo intermedio, valor agregado, formación de capital y activos fijos adquiridos. |

## 2. Tabla de hechos

La tabla de hechos representa los eventos sísmicos que se analizarán en el almacén de datos.

Para organizar las relaciones se propone una tabla denominada `hecho_sismos`, que almacene las referencias a las dimensiones y las medidas necesarias para el análisis.

| Campo | Descripción |
|---|---|
| id_hecho | Identificador único del registro de hecho. |
| id_sismo | Referencia al evento sísmico. |
| id_tiempo | Referencia a la dimensión temporal. |
| id_zonas | Referencia a la dimensión geográfica. |
| id_economia | Referencia a la dimensión económica, cuando exista correspondencia. |

La granularidad propuesta es **un registro por evento sísmico asociado con una fecha, una zona geográfica y, cuando corresponda, una referencia económica**.

La tabla se considera una propuesta de organización analítica. Antes de implementarla debe comprobarse si el repositorio ya cuenta con una tabla equivalente y si las relaciones entre las dimensiones están definidas de otra manera.

## 3. Dimensiones y claves primarias

Las dimensiones identificadas utilizan los siguientes identificadores:

| Dimensión | Clave primaria | Atributos principales |
|---|---|---|
| dim_sismos | id_sismo | magnitud, latitud, longitud, profundidad, referencia_de_localizacion, estado, nombre_estado |
| dim_tiempo | id_tiempo | hora_utc, fecha, anio, mes, dia, trimestre |
| dim_zonas | id_zonas | entidad, nom_ent, pobtot, pobfem, pobmas |
| dim_economia | id_economia | nombre_entidad, entidad, produccion_bruta_total, insumos_utilizados, consumo_intermedio, valor_agregado, formacion_capital, activos_fijos_adquiridos |

Estas claves permiten identificar de manera única cada registro y establecer relaciones con la tabla de hechos.

## 4. Relaciones y claves foráneas propuestas

| Tabla dependiente | Columna FK | Tabla referenciada | Columna PK |
|---|---|---|---|
| hecho_sismos | id_sismo | dim_sismos | id_sismo |
| hecho_sismos | id_tiempo | dim_tiempo | id_tiempo |
| hecho_sismos | id_zonas | dim_zonas | id_zonas |
| hecho_sismos | id_economia | dim_economia | id_economia |

Las claves foráneas permiten que cada registro de hechos se relacione únicamente con dimensiones existentes.

La referencia económica puede permitir NULL cuando no exista información económica aplicable al evento o cuando no se haya establecido una correspondencia territorial válida.

## 5. Comprobación de registros huérfanos

Para comprobar que las referencias de la tabla de hechos correspondan con registros existentes, se proponen las siguientes consultas:

```sql
SELECT h.*
FROM hecho_sismos h
LEFT JOIN dim_sismos s ON h.id_sismo = s.id_sismo
WHERE s.id_sismo IS NULL;

SELECT h.*
FROM hecho_sismos h
LEFT JOIN dim_tiempo t ON h.id_tiempo = t.id_tiempo
WHERE t.id_tiempo IS NULL;

SELECT h.*
FROM hecho_sismos h
LEFT JOIN dim_zonas z ON h.id_zonas = z.id_zonas
WHERE z.id_zonas IS NULL;

SELECT h.*
FROM hecho_sismos h
LEFT JOIN dim_economia e ON h.id_economia = e.id_economia
WHERE h.id_economia IS NOT NULL
  AND e.id_economia IS NULL;
```

**Resultado esperado:** todas las consultas deben devolver cero registros. La última consulta permite que `id_economia` sea NULL, pero no admite identificadores económicos inexistentes.

## 6. Acciones referenciales recomendadas

Para el almacén de datos se recomienda:

| Relación | ON DELETE | ON UPDATE | Justificación |
|---|---|---|---|
| hecho_sismos → dim_sismos | RESTRICT | CASCADE | Evita eliminar eventos sísmicos que ya estén relacionados con registros analíticos. |
| hecho_sismos → dim_tiempo | RESTRICT | CASCADE | Conserva las referencias temporales utilizadas en los análisis. |
| hecho_sismos → dim_zonas | RESTRICT | CASCADE | Protege la información geográfica relacionada con los hechos. |
| hecho_sismos → dim_economia | SET NULL | CASCADE | Permite conservar el evento si se elimina una referencia económica. |

En un almacén de datos se debe priorizar la conservación de los registros históricos. Por ello, no se recomienda eliminar en cascada los registros de hechos cuando se elimina una dimensión.

## 7. Comprobación de integridad de las dimensiones

Además de verificar las claves foráneas, se deben comprobar los siguientes aspectos:

- Que cada dimensión tenga una clave primaria definida.
- Que no existan identificadores duplicados.
- Que los campos utilizados como claves foráneas tengan tipos de datos compatibles.
- Que los valores obligatorios no contengan NULL.
- Que las dimensiones se carguen antes que los registros de hechos.
- Que las correspondencias geográficas y temporales sean válidas.

## 8. Orden recomendado de carga

La carga de información debe respetar el siguiente orden:

1. Cargar la dimensión temporal `dim_tiempo`.
2. Cargar la dimensión geográfica `dim_zonas`.
3. Cargar la dimensión económica `dim_economia`.
4. Cargar la dimensión de eventos `dim_sismos`.
5. Cargar los registros de la tabla de hechos `hecho_sismos`.

Este orden permite que las referencias de la tabla de hechos apunten a registros previamente existentes.

## 9. Riesgos cuando no existen claves foráneas

Si las relaciones no cuentan con restricciones de integridad referencial, pueden presentarse los siguientes problemas:

- Registros de hechos que hagan referencia a dimensiones inexistentes.
- Diferencias entre los identificadores geográficos y los nombres de entidades.
- Eventos sísmicos asociados con fechas incorrectas.
- Dificultades para realizar consultas y generar visualizaciones confiables.
- Duplicación o pérdida de información durante la carga de datos.

Si el esquema existente no utiliza claves foráneas, se deben justificar las razones técnicas y documentar cómo se garantiza la integridad mediante procesos de validación y limpieza.

**Conclusión:** la integridad referencial es necesaria para asegurar que los eventos sísmicos puedan relacionarse correctamente con su información temporal, geográfica y económica. La tabla de hechos propuesta permite organizar estas relaciones y facilitar las consultas analíticas del proyecto.

**Nota:** `hecho_sismos` es una propuesta de organización. Se debe comparar con el esquema real del repositorio antes de crearla o agregar restricciones, para evitar duplicar una tabla de hechos que ya exista.
