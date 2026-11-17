

import csv
import os
import sys
import time
from pathlib import Path
import psycopg  

DATA_DIR = Path(os.getenv("DATA_DIR", "practica4/datos"))

PLAN_CARGA = [
    (
        "01_empleados.csv",
        "EMPLEADO",
        ["ID_Empleado", "Nombre", "Telefono", "FechaContratacion", "RFC"],
        "(ID_Empleado)",
    ),
    (
        "02_meseros.csv",
        "MESERO",
        ["ID_Empleado", "Turno"],
        "(ID_Empleado)",
    ),
    (
        "03_chefs.csv",
        "CHEF",
        ["ID_Empleado", "Especialidad", "AniosExperiencia"],
        "(ID_Empleado)",
    ),
    (
        "04_clientes.csv",
        "CLIENTE",
        ["ID_Cliente", "Nombre", "Correo", "Calle", "Numero", "Colonia", "Telefono"],
        "(ID_Cliente)",
    ),
    (
        "05_telefonos_cliente.csv",
        "TELEFONO_CLIENTE",
        ["ID_Cliente", "Telefono"],
        "(ID_Cliente, Telefono)",
    ),
    (
        "06_platillos.csv",
        "PLATILLO",
        ["ID_Platillo", "Nombre", "Descripcion", "Precio", "ID_Empleado"],
        "(ID_Platillo)",
    ),
    (
        "07_asignacion_chef_platillo.csv",
        "ASIGNACION_CHEF_PLATILLO",
        ["ID_Empleado", "ID_Platillo", "FechaAsignacion"],
        "(ID_Empleado, ID_Platillo)",
    ),
    (
        "08_pedidos.csv",
        "PEDIDO",
        ["ID_Pedido", "FechaHora", "ID_Cliente", "ID_Mesero", "Total"],
        "(ID_Pedido)",
    ),
    (
        "09_detalle_pedido.csv",
        "DETALLE_PEDIDO",
        ["ID_Pedido", "ID_Platillo", "Cantidad", "PrecioUnitario", "Subtotal"],
        "(ID_Pedido, ID_Platillo)",
    ),
]


def obtener_conexion():
    """Conecta usando exclusivamente variables de entorno estándar de PostgreSQL."""
    requeridas = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    faltantes = [v for v in requeridas if not os.getenv(v)]
    if faltantes:
        raise EnvironmentError(
            f"Faltan variables de entorno obligatorias: {', '.join(faltantes)}"
        )
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.getenv("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def sincronizar_secuencias(cur):
    """Actualiza las secuencias SERIAL después de cargar IDs explícitos."""
    secuencias = [
        ("EMPLEADO", "ID_Empleado"),
        ("CLIENTE", "ID_Cliente"),
        ("PLATILLO", "ID_Platillo"),
        ("PEDIDO", "ID_Pedido"),
    ]
    for tabla, col in secuencias:
        cur.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{tabla}', '{col}'),
                COALESCE((SELECT MAX({col}) FROM {tabla}), 1),
                true
            );
            """
        )


def benchmark_insert_vs_copy(conn, tiempo_copy_detalle: float):
    """
    Mide cuánto tardaría insertar los 1,150 renglones de DETALLE_PEDIDO uno por uno
    con INSERT dentro de una transacción que luego se revierte (SAVEPOINT),
    para reportar la diferencia de rendimiento frente a COPY.
    """
    ruta_csv = DATA_DIR / "09_detalle_pedido.csv"
    with open(ruta_csv, encoding="utf-8") as f:
        filas = list(csv.reader(f))[1:]

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT sp_benchmark;")
            cur.execute("CREATE TEMP TABLE tmp_bench (LIKE DETALLE_PEDIDO) ON COMMIT DROP;")
            t0 = time.perf_counter()
            for r in filas:
                cur.execute(
                    "INSERT INTO tmp_bench VALUES (%s, %s, %s, %s, %s);",
                    r,
                )
            tiempo_insert = time.perf_counter() - t0
            cur.execute("ROLLBACK TO SAVEPOINT sp_benchmark;")

    factor = tiempo_insert / tiempo_copy_detalle if tiempo_copy_detalle > 0 else 0
    print("\n--- BENCHMARK DE RENDIMIENTO (1,150 renglones de DETALLE_PEDIDO) ---")
    print(f"  * Carga masiva con COPY : {tiempo_copy_detalle * 1000:7.2f} ms")
    print(f"  * Carga fila por fila   : {tiempo_insert * 1000:7.2f} ms")
    print(f"  * Mejora de velocidad   : {factor:7.1f}x más rápido con COPY")


def main():
    t_inicio_total = time.perf_counter()
    resumen = []
    tabla_actual = "CONEXIÓN"
    tiempo_copy_detalle = 0.0

    try:
        with obtener_conexion() as conn:
            
            with conn.transaction():
                with conn.cursor() as cur:
                    for archivo, tabla, cols, pk_conflict in PLAN_CARGA:
                        tabla_actual = tabla
                        ruta_csv = DATA_DIR / archivo
                        if not ruta_csv.exists():
                            raise FileNotFoundError(f"No existe el archivo: {ruta_csv}")

                        cols_str = ", ".join(cols)
                        tmp_table = f"tmp_{tabla.lower()}"

                        t0 = time.perf_counter()

                        
                        cur.execute(
                            f"CREATE TEMP TABLE {tmp_table} AS SELECT {cols_str} FROM {tabla} WITH NO DATA;"
                        )


                        
                        copy_sql = f"COPY {tmp_table} ({cols_str}) FROM STDIN WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')"
                        with open(ruta_csv, "r", encoding="utf-8") as f_csv:
                            with cur.copy(copy_sql) as copy:
                                while data := f_csv.read(65536):
                                    copy.write(data)

                        cur.execute(f"SELECT COUNT(*) FROM {tmp_table};")
                        leidos = cur.fetchone()[0]


                        
                        cur.execute(
                            f"""
                            INSERT INTO {tabla} ({cols_str})
                            SELECT {cols_str} FROM {tmp_table}
                            ON CONFLICT {pk_conflict} DO NOTHING;
                            """
                        )
                        insertados = cur.rowcount
                        rechazados_o_existentes = leidos - insertados
                        cur.execute(f"DROP TABLE {tmp_table};")

                        dt = time.perf_counter() - t0
                        if tabla == "DETALLE_PEDIDO":
                            tiempo_copy_detalle = dt

                        resumen.append((tabla, leidos, insertados, rechazados_o_existentes, dt))

                    sincronizar_secuencias(cur)


            
            benchmark_insert_vs_copy(conn, tiempo_copy_detalle)

    except psycopg.Error as e:
        print("\n[ERROR FATAL] La carga fue revertida completamente (ROLLBACK).", file=sys.stderr)
        print(f"  -> Tabla donde ocurrió el fallo : {tabla_actual}", file=sys.stderr)
        print(f"  -> Código SQLSTATE              : {e.sqlstate}", file=sys.stderr)
        print(f"  -> Diagnóstico del gestor       : {e.diag.message_primary}", file=sys.stderr)
        if e.diag.message_detail:
            print(f"  -> Detalle del renglón          : {e.diag.message_detail}", file=sys.stderr)
        if e.diag.constraint_name:
            print(f"  -> Restricción violada          : {e.diag.constraint_name}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Fallo en {tabla_actual}: {e}", file=sys.stderr)
        sys.exit(1)

    duracion_total = (time.perf_counter() - t_inicio_total) * 1000
    print("\n===========================================================================")
    print(f"{'TABLA':<28} | {'CSV':>6} | {'INSERTADOS':>10} | {'OMITIDOS':>8} | {'TIEMPO':>8}")
    print("---------------------------------------------------------------------------")
    for tabla, leidos, ins, rej, dt in resumen:
        print(f"{tabla:<28} | {leidos:>6} | {ins:>10} | {rej:>8} | {dt*1000:>6.1f}ms")
    print("===========================================================================")
    print(f"Carga completada exitosamente en {duracion_total:.2f} ms.")


if __name__ == "__main__":
    main()