
import csv
import io
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
import psycopg

CSV_SSN = Path(os.getenv("SSN_CSV_PATH", "practica4/proyecto-asignado/datos/SSNMX_catalogo.csv"))


def obtener_conexion():
    requeridas = ["PGHOST", "PGDATABASE_SISMOS", "PGUSER", "PGPASSWORD"]
    faltantes = [v for v in requeridas if not os.getenv(v)]
    if faltantes:
        raise EnvironmentError(f"Faltan variables de entorno: {', '.join(faltantes)}")
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.getenv("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE_SISMOS"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def extraer_estado(referencia: str) -> str:
    """Extrae la clave de entidad federativa al final de 'Referencia de localizacion' (ej. '15 km al SUR de PINOTEPA NACIONAL, OAX')."""
    if not referencia:
        return "NO ESPECIFICADO"
    match = re.search(r",\s*([A-ZÑ]{2,5})\s*$", referencia.strip().upper())
    return match.group(1) if match else "OTRO"


def clasificar_magnitud(mag: float) -> str:
    if mag < 3.0:
        return "Micro"
    if mag < 4.0:
        return "Menor"
    if mag < 5.0:
        return "Ligero"
    if mag < 6.0:
        return "Moderado"
    if mag < 7.0:
        return "Fuerte"
    return "Mayor / Gran Sismo"


def limpiar_y_parsear_ssn(ruta: Path) -> list[dict]:
    """Filtra líneas de encabezado/pie del SSN y descarta registros sin magnitud numérica ('no calculable')."""
    registros = []
    with open(ruta, mode="r", encoding="latin-1", errors="replace") as f:
        lineas_validas = [
            linea for linea in f
            if re.match(r"^\d{4}-\d{2}-\d{2},", linea.strip())
        ]

    reader = csv.reader(lineas_validas)
    for row in reader:
        if len(row) < 7:
            continue
        fecha_str, hora_str, mag_str, lat_str, lon_str, prof_str, ref = row[:7]
        try:
            mag = float(mag_str)
            lat = float(lat_str)
            lon = float(lon_str)
            prof = float(prof_str)
            dt = datetime.strptime(f"{fecha_str.strip()} {hora_str.strip()}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Descarta sismos con magnitud 'no calculable' o coordenadas malformadas
            continue

        registros.append({
            "fecha": dt.date().isoformat(),
            "hora": dt.time().isoformat(),
            "anio": dt.year,
            "mes": dt.month,
            "dia": dt.day,
            "latitud": lat,
            "longitud": lon,
            "profundidad": prof,
            "referencia": ref.strip(),
            "estado": extraer_estado(ref),
            "magnitud": mag,
            "categoria_mag": clasificar_magnitud(mag),
        })
    return registros


def main():
    t0 = time.perf_counter()
    if not CSV_SSN.exists():
        print(f"[ERROR] No se encontró el catálogo del SSN en: {CSV_SSN}", file=sys.stderr)
        sys.exit(1)

    filas = limpiar_y_parsear_ssn(CSV_SSN)
    if not filas:
        print("[ERROR] No se extrajeron registros válidos del CSV del SSN.", file=sys.stderr)
        sys.exit(1)

    try:
        with obtener_conexion() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    # 1. Staging temporal cargado masivamente con COPY
                    cur.execute("""
                        CREATE TEMP TABLE tmp_ssn (
                            fecha DATE,
                            hora TIME,
                            anio INT,
                            mes INT,
                            dia INT,
                            latitud NUMERIC(9,6),
                            longitud NUMERIC(9,6),
                            profundidad NUMERIC(7,2),
                            referencia TEXT,
                            estado VARCHAR(20),
                            magnitud NUMERIC(4,2),
                            categoria_mag VARCHAR(30)
                        ) ON COMMIT DROP;
                    """)

                    buffer = io.StringIO()
                    writer = csv.writer(buffer)
                    for r in filas:
                        writer.writerow([
                            r["fecha"], r["hora"], r["anio"], r["mes"], r["dia"],
                            r["latitud"], r["longitud"], r["profundidad"],
                            r["referencia"], r["estado"], r["magnitud"], r["categoria_mag"]
                        ])
                    buffer.seek(0)

                    with cur.copy("COPY tmp_ssn FROM STDIN WITH (FORMAT csv)") as copy:
                        copy.write(buffer.read())

                    # 2. Poblar Dimensiones (Orden topológico: primero dimensiones)
                    cur.execute("""
                        INSERT INTO dim_tiempo (fecha, anio, mes, dia)
                        SELECT DISTINCT fecha, anio, mes, dia FROM tmp_ssn
                        ON CONFLICT (fecha) DO NOTHING;
                    """)
                    ins_tiempo = cur.rowcount

                    cur.execute("""
                        INSERT INTO dim_ubicacion (estado, referencia, latitud, longitud)
                        SELECT DISTINCT estado, referencia, latitud, longitud FROM tmp_ssn
                        ON CONFLICT (latitud, longitud, referencia) DO NOTHING;
                    """)
                    ins_ubicacion = cur.rowcount

                    # 3. Poblar Tabla de Hechos referenciando dimensiones
                    cur.execute("""
                        INSERT INTO hechos_sismos (id_tiempo, id_ubicacion, hora, magnitud, profundidad, categoria_magnitud)
                        SELECT t.id_tiempo, u.id_ubicacion, s.hora, s.magnitud, s.profundidad, s.categoria_mag
                        FROM tmp_ssn s
                        JOIN dim_tiempo t ON t.fecha = s.fecha
                        JOIN dim_ubicacion u ON u.latitud = s.latitud
                                            AND u.longitud = s.longitud
                                            AND u.referencia = s.referencia
                        ON CONFLICT DO NOTHING;
                    """)
                    ins_hechos = cur.rowcount

    except psycopg.Error as e:
        print(f"\n[ROLLBACK] Error de PostgreSQL al cargar Sismos: {e.diag.message_primary}", file=sys.stderr)
        if e.diag.message_detail:
            print(f"Detalle: {e.diag.message_detail}", file=sys.stderr)
        sys.exit(1)

    dt_ms = (time.perf_counter() - t0) * 1000
    print("\n=== RESUMEN DE CARGA: PROYECTO ASIGNADO (SISMOS SSN) ===")
    print(f"  Registros válidos leídos del SSN : {len(filas)}")
    print(f"  Insertados en dim_tiempo         : {ins_tiempo}")
    print(f"  Insertados en dim_ubicacion      : {ins_ubicacion}")
    print(f"  Insertados en hechos_sismos      : {ins_hechos}")
    print(f"  Tiempo total (COPY + JOINs)      : {dt_ms:.2f} ms")


if __name__ == "__main__":
    main()