

import csv
import os
import random
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path


SEED = 20261105
random.seed(SEED)

OUTPUT_DIR = Path(os.getenv("DATA_DIR", "practica4/datos"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOMBRES = [
    "Carlos", "María", "Juan", "Ana", "Luis", "Sofía", "Miguel", "Valeria", "José", "Fernanda",
    "Diego", "Camila", "Alejandro", "Daniela", "Jorge", "Paula", "Ricardo", "Andrea", "Fernando", "Lucía",
    "Eduardo", "Mariana", "Roberto", "Gabriela", "David", "Ximena", "Arturo", "Natalia", "Héctor", "Elena"
]
APELLIDOS = [
    "Hernández", "García", "Martínez", "López", "González", "Pérez", "Rodríguez", "Sánchez", "Ramírez", "Cruz",
    "Flores", "Gómez", "Morales", "Vázquez", "Jiménez", "Reyes", "Díaz", "Torres", "Gutiérrez", "Ruiz",
    "Mendoza", "Aguilar", "Ortiz", "Moreno", "Castillo", "Romero", "Álvarez", "Méndez", "Chávez", "Rivera"
]
CALLES = [
    "Av. Insurgentes Sur", "Calle Durango", "Av. Reforma", "Calle Colima", "Av. Universidad",
    "Calle Orizaba", "Av. Coyoacán", "Calle Madero", "Av. División del Norte", "Calle Álvaro Obregón",
    "Av. Revolución", "Calle Puebla", "Calz. de Tlalpan", "Calle Hamburgo", "Av. Chapultepec"
]
COLONIAS_CDMX = [
    "Roma Norte", "Condesa", "Del Valle Centro", "Polanco", "Coyoacán Centro",
    "Narvarte Poniente", "Nápoles", "Juárez", "Santa María la Ribera", "San Ángel",
    "Escandón", "Portales Norte", "Anzures", "Lindavista", "Cuauhtémoc"
]
ESPECIALIDADES = [
    "Cocina Mexicana", "Parrilla", "Mariscos", "Repostería",
    "Pastas", "Cocina Internacional", "Entradas y Ensaladas"
]
TURNOS = ["Matutino", "Vespertino", "Mixto"]

PLATILLOS_BASE = [
    "Tacos al Pastor", "Enchiladas Suizas", "Arrachera a la Parrilla", "Aguachile Verde", "Chiles en Nogada",
    "Mole Poblano", "Pozole Rojo", "Ceviche Peruano", "Filete Mignon", "Salmón a las Finas Hierbas",
    "Pasta Alfredo con Camarones", "Lasagna Bolognesa", "Tostadas de Atún", "Sopa Azteca", "Cochinita Pibil",
    "Tampiqueña Tradicional", "Hamburguesa Artesanal", "Rib Eye 400g", "Pulpo a las Brasas", "Flan Napolitano",
    "Pastel de Tres Leches", "Churros con Cajeta", "Ensalada César", "Carpaccio de Res", "Quesadillas de Flor",
    "Sopes de Chorizo", "Barbacoa de Borrego", "Camarones al Mojo de Ajo", "Crema de Elote", "Tiramisú Clásico"
]
VARIANTES = [
    "de la Casa", "Especial", "Tradicional", "al Carbón", "Acompañado con Guarnición",
    "Estilo Gourmet", "Porción Grande", "Receta Secreta", "con Salsa Artesanal", "del Chef"
]


def generar_rfc(nombre: str, ap_paterno: str, ap_materno: str, fecha_nac: date, usados: set) -> str:
    """Genera un RFC de 13 caracteres válido según regex ^[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}$."""
    def limpiar(s: str) -> str:
        s = s.upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
        return re.sub(r"[^A-ZÑ]", "", s)

    p = limpiar(ap_paterno)
    m = limpiar(ap_materno)
    n = limpiar(nombre)
    vocal = next((c for c in p[1:] if c in "AEIOU"), "X")
    base = f"{p[0]}{vocal}{m[0]}{n[0]}{fecha_nac.strftime('%y%m%d')}"
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    while True:
        homo = "".join(random.choices(chars, k=3))
        rfc = base + homo
        if rfc not in usados:
            usados.add(rfc)
            return rfc


def telefono_10(usados: set | None = None) -> str:
    """Genera un teléfono nacional de exactamente 10 dígitos numéricos."""
    while True:
        tel = random.choice(["55", "56", "33", "81"]) + "".join(str(random.randint(0, 9)) for _ in range(8))
        if usados is None or tel not in usados:
            if usados is not None:
                usados.add(tel)
            return tel


def escribir_csv(nombre_archivo: str, encabezados: list[str], filas: list[list]):
    ruta = OUTPUT_DIR / nombre_archivo
    with open(ruta, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(encabezados)
        writer.writerows(filas)
    print(f"  [OK] {nombre_archivo:<32} -> {len(filas):>4} registros")


def main():
    print(f"Generando datasets CSV en: {OUTPUT_DIR.resolve()}\n")
    hoy = date(2026, 11, 1)

  
    empleados = []
    meseros = []
    chefs = []
    rfcs_usados = set()
    fechas_contratacion = {}

    for id_emp in range(1, 41):
        nom = random.choice(NOMBRES)
        ap1 = random.choice(APELLIDOS)
        ap2 = random.choice(APELLIDOS)
        nombre_completo = f"{nom} {ap1} {ap2}"
        tel = telefono_10()
        f_nac = date(random.randint(1975, 2001), random.randint(1, 12), random.randint(1, 28))
        f_cont = date(2015, 1, 1) + timedelta(days=random.randint(0, (hoy - date(2015, 1, 1)).days))
        rfc = generar_rfc(nom, ap1, ap2, f_nac, rfcs_usados)

        empleados.append([id_emp, nombre_completo, tel, f_cont.isoformat(), rfc])
        fechas_contratacion[id_emp] = f_cont

        if id_emp <= 25:
            meseros.append([id_emp, random.choice(TURNOS)])
        else:
            exp = min(random.randint(1, 25), (hoy.year - f_nac.year) - 18)
            chefs.append([id_emp, random.choice(ESPECIALIDADES), max(0, exp)])


    clientes = []
    telefonos_cliente = []
    correos_usados = set()

    for id_cli in range(1, 251):
        nom = random.choice(NOMBRES)
        ap1 = random.choice(APELLIDOS)
        ap2 = random.choice(APELLIDOS)
        nombre_completo = f"{nom} {ap1} {ap2}"

        base_mail = f"{nom.lower()}.{ap1.lower()}{id_cli}".replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        dominio = random.choice(["gmail.com", "hotmail.com", "outlook.com", "ipn.mx", "yahoo.com.mx"])
        correo = f"{base_mail}@{dominio}"
        correos_usados.add(correo)

        calle = random.choice(CALLES)
        numero = f"{random.randint(10, 999)}" + random.choice(["", "", "-A", "-B", " Int. 3"])
        colonia = random.choice(COLONIAS_CDMX)
        tel_principal = telefono_10()

        clientes.append([id_cli, nombre_completo, correo, calle, numero, colonia, tel_principal])

        tels_este_cliente = {tel_principal}
        telefonos_cliente.append([id_cli, tel_principal])
        if random.random() < 0.24:  # ~60 clientes con segundo teléfono
            tel_extra = telefono_10(tels_este_cliente)
            telefonos_cliente.append([id_cli, tel_extra])


    platillos = []
    asignaciones = []
    nombres_platillo_usados = set()
    precios_platillo = {}
    chef_ids = [c[0] for c in chefs]

    for id_plat in range(1, 211):
        while True:
            nombre_plat = f"{random.choice(PLATILLOS_BASE)} {random.choice(VARIANTES)}"
            if nombre_plat not in nombres_platillo_usados:
                nombres_platillo_usados.add(nombre_plat)
                break

        desc = f"Preparación artesanal de {nombre_plat.lower()} con ingredientes frescos seleccionados diariamente."
        precio = Decimal(random.randint(65, 680)) + Decimal(random.choice(["0.00", "0.50", "0.90"]))
        chef_resp = random.choice(chef_ids)

        platillos.append([id_plat, nombre_plat, desc, f"{precio:.2f}", chef_resp])
        precios_platillo[id_plat] = precio


        chefs_asignados = {chef_resp}
        if random.random() < 0.52:
            chefs_asignados.add(random.choice(chef_ids))

        for c_id in chefs_asignados:
            f_min = fechas_contratacion[c_id]
            f_asig = f_min + timedelta(days=random.randint(0, (hoy - f_min).days))
            asignaciones.append([c_id, id_plat, f_asig.isoformat()])


    pedidos = []
    detalles = []
    mesero_ids = [m[0] for m in meseros]

    for id_ped in range(1, 401):
        id_cli = random.randint(1, 250)
        id_mes = random.choice(mesero_ids)
        dias_atras = random.randint(1, 365)
        hora = random.randint(13, 21)
        minuto = random.randint(0, 59)
        segundo = random.randint(0, 59)
        fh = datetime(2026, 11, 1, hora, minuto, segundo) - timedelta(days=dias_atras)

        num_renglones = random.randint(2, 4)
        platillos_orden = random.sample(range(1, 211), k=num_renglones)
        total_pedido = Decimal("0.00")

        for id_plat in platillos_orden:
            cant = random.randint(1, 5)
            p_unit = precios_platillo[id_plat]
            sub = (p_unit * cant).quantize(Decimal("0.01"))
            total_pedido += sub
            detalles.append([id_ped, id_plat, cant, f"{p_unit:.2f}", f"{sub:.2f}"])

        pedidos.append([id_ped, fh.strftime("%Y-%m-%d %H:%M:%S"), id_cli, id_mes, f"{total_pedido:.2f}"])

    escribir_csv("01_empleados.csv", ["id_empleado", "nombre", "telefono", "fecha_contratacion", "rfc"], empleados)
    escribir_csv("02_meseros.csv", ["id_empleado", "turno"], meseros)
    escribir_csv("03_chefs.csv", ["id_empleado", "especialidad", "anios_experiencia"], chefs)
    escribir_csv("04_clientes.csv", ["id_cliente", "nombre", "correo", "calle", "numero", "colonia", "telefono"], clientes)
    escribir_csv("05_telefonos_cliente.csv", ["id_cliente", "telefono"], telefonos_cliente)
    escribir_csv("06_platillos.csv", ["id_platillo", "nombre", "descripcion", "precio", "id_empleado"], platillos)
    escribir_csv("07_asignacion_chef_platillo.csv", ["id_empleado", "id_platillo", "fecha_asignacion"], asignaciones)
    escribir_csv("08_pedidos.csv", ["id_pedido", "fecha_hora", "id_cliente", "id_mesero", "total"], pedidos)
    escribir_csv("09_detalle_pedido.csv", ["id_pedido", "id_platillo", "cantidad", "precio_unitario", "subtotal"], detalles)
    print("\nGeneración finalizada con éxito.")


if __name__ == "__main__":
    main()