## Comparación estadística contra lo reportado en el artículo 

Al comparar los conteos y agregaciones de la base poblada en nuestro fork contra los resultados publicados en el artículo base (*Seismic-Data-Visualization-System*, Revista AZCATL), se observan las siguientes coincidencias y variaciones:

| Métrica / Indicador | Reportado en el artículo | Obtenido en nuestra carga | Explicación de la diferencia |
| :--- | :--- | :--- | :--- |
| **Fuente sísmica** | Catálogo histórico del SSN (UNAM) | Catálogo público del SSN (UNAM) | Coincide al 100% en la fuente primaria. |
| **Granularidad espacial** | Epicentro (latitud, longitud) cruzado con municipios/entidades INEGI | Epicentro (latitud, longitud) y extracción de estado desde referencia SSN | El artículo realiza un cruce espacial con polígonos geoestadísticos del INEGI; nuestra carga extrae la abreviatura estatal directamente del texto descriptivo del SSN. |
| **Volumen total de eventos** | Corte histórico fijo al momento de publicación del artículo | Corte descargado hasta noviembre de 2026 | Nuestro dataset incluye eventos sísmicos ocurridos con posterioridad a la fecha de cierre del estudio original. |
| **Registros descartados en ETL** | No detalla el porcentaje de magnitudes no calculables | ~1.8% de filas descartadas (`Magnitud = 'no calculable'`) | En sismos muy leves o recientes, el SSN publica inicialmente el texto `'no calculable'` en lugar de un valor numérico; el script los filtra para mantener la integridad numérica de `hechos_sismos.magnitud`. |

---

## Revisión de dominios y prueba de 3 restricciones nuevas


Sobre una copia de prueba , se aplicaron tres nuevas restricciones de dominio y se evaluó si los datos reales del SSN las cumplen:

### Restricción: Rango geográfico de latitud y longitud para la República Mexicana
* **Regla del dominio:** Todo epicentro registrado en el catálogo nacional debe ubicarse dentro o en las inmediaciones del polígono territorial y mar patrimonial de México ($12^\circ \le \text{Latitud} \le 34^\circ$ y $-120^\circ \le \text{Longitud} \le -84^\circ$).
* **Sentencia aplicada en copia:**
  ```sql
  ALTER TABLE dim_ubicacion
      ADD CONSTRAINT chk_ubicacion_coordenadas_mexico
      CHECK (latitud BETWEEN 12.0 AND 34.0 AND longitud BETWEEN -120.0 AND -84.0);
