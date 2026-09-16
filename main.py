#!/usr/bin/env python3
"""
AgroControl CBA - Sistema monolítico para gestión de producción, inventario y ventas
Centro de Biotecnología Agropecuaria - SENA
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACIÓN Y RUTAS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARCHIVOS = {
    "productos": DATA_DIR / "productos.json",
    "lotes": DATA_DIR / "lotes.json",
    "movimientos": DATA_DIR / "movimientos.json",
    "ventas": DATA_DIR / "ventas.json",
}

# ============================================================
# PERSISTENCIA JSON
# ============================================================
def cargar_datos(nombre: str) -> list:
    """Carga una colección desde JSON. Si no existe, retorna lista vacía."""
    ruta = ARCHIVOS[nombre]
    if not ruta.exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos if isinstance(datos, list) else []
    except (json.JSONDecodeError, OSError):
        print(f"  [!] Error al leer {ruta.name}. Se inicia con colección vacía.")
        return []


def guardar_datos(nombre: str, datos: list) -> None:
    """Guarda una colección en JSON de forma inmediata."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ruta = ARCHIVOS[nombre]
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def guardar_todo(productos, lotes, movimientos, ventas) -> None:
    """Persiste todas las colecciones."""
    guardar_datos("productos", productos)
    guardar_datos("lotes", lotes)
    guardar_datos("movimientos", movimientos)
    guardar_datos("ventas", ventas)
    print("  [OK] Datos guardados correctamente.")


# ============================================================
# UTILIDADES
# ============================================================
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n  Presione ENTER para continuar...")


def leer_texto(mensaje: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor or not obligatorio:
            return valor
        print("  [!] Este campo es obligatorio.")


def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                print(f"  [!] El valor debe ser >= {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  [!] El valor debe ser <= {maximo}.")
                continue
            return valor
        except ValueError:
            print("  [!] Ingrese un número entero válido.")


def leer_flotante(mensaje: str, minimo: float | None = None) -> float:
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"  [!] El valor debe ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  [!] Ingrese un número válido.")


def fecha_hora_actual() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def generar_id(prefijo: str, coleccion: list, campo: str = "id") -> str:
    """Genera identificadores secuenciales: M0001, V0001, L001, etc."""
    if not coleccion:
        return f"{prefijo}0001" if prefijo in ("M", "V") else f"{prefijo}001"
    numeros = []
    for item in coleccion:
        codigo = item.get(campo, "")
        digitos = "".join(c for c in codigo if c.isdigit())
        if digitos:
            numeros.append(int(digitos))
    siguiente = max(numeros) + 1 if numeros else 1
    if prefijo in ("M", "V"):
        return f"{prefijo}{siguiente:04d}"
    return f"{prefijo}{siguiente:03d}"


# ============================================================
# CÁLCULO DE STOCK (regla de negocio clave)
# ============================================================
def calcular_stock(producto_codigo: str, movimientos: list) -> int:
    """Calcula el stock actual a partir de los movimientos de inventario."""
    stock = 0
    for mov in movimientos:
        if mov["producto_codigo"] == producto_codigo:
            if mov["tipo"] == "ENTRADA":
                stock += mov["cantidad"]
            elif mov["tipo"] == "SALIDA":
                stock -= mov["cantidad"]
    return stock


# ============================================================
# PRODUCTOS
# ============================================================
def buscar_producto(productos: list, codigo: str) -> dict | None:
    codigo = codigo.upper().strip()
    for p in productos:
        if p["codigo"] == codigo:
            return p
    return None


def registrar_producto(productos: list) -> None:
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = leer_texto("  Código (ej: P001): ").upper()
    if buscar_producto(productos, codigo):
        print("  [!] Ya existe un producto con ese código.")
        return
    nombre = leer_texto("  Nombre: ")
    categoria = leer_texto("  Categoría: ")
    unidad = leer_texto("  Unidad (ej: unidad, kg, bulto): ")
    precio = leer_flotante("  Precio de venta: ", minimo=0.01)
    stock_minimo = leer_entero("  Stock mínimo: ", minimo=0)

    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True,
    }
    productos.append(producto)
    guardar_datos("productos", productos)
    print(f"  [OK] Producto {codigo} registrado.")


def listar_productos(productos: list, solo_activos: bool = True) -> None:
    print("\n--- LISTADO DE PRODUCTOS ---")
    filtrados = [p for p in productos if p["activo"]] if solo_activos else productos
    if not filtrados:
        print("  No hay productos registrados.")
        return
    print(f"  {'Código':<8} {'Nombre':<25} {'Categoría':<15} {'Unidad':<10} {'Precio':>10} {'Mín':>5} {'Estado':<10}")
    print("  " + "-" * 90)
    for p in filtrados:
        estado = "ACTIVO" if p["activo"] else "INACTIVO"
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {p['categoria'][:14]:<15} "
              f"{p['unidad'][:9]:<10} {p['precio']:>10.0f} {p['stock_minimo']:>5} {estado:<10}")


def buscar_productos_texto(productos: list) -> None:
    print("\n--- BUSCAR PRODUCTOS ---")
    termino = leer_texto("  Código o parte del nombre: ").lower()
    resultados = [
        p for p in productos
        if termino in p["codigo"].lower() or termino in p["nombre"].lower()
    ]
    if not resultados:
        print("  No se encontraron productos.")
        return
    print(f"  {'Código':<8} {'Nombre':<25} {'Precio':>10} {'Estado':<10}")
    print("  " + "-" * 55)
    for p in resultados:
        estado = "ACTIVO" if p["activo"] else "INACTIVO"
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {p['precio']:>10.0f} {estado:<10}")


def actualizar_producto(productos: list) -> None:
    print("\n--- ACTUALIZAR PRODUCTO ---")
    codigo = leer_texto("  Código del producto: ").upper()
    producto = buscar_producto(productos, codigo)
    if not producto:
        print("  [!] Producto no encontrado.")
        return
    if not producto["activo"]:
        print("  [!] El producto está desactivado. Reactívelo primero si desea editarlo.")
        return
    print(f"  Producto actual: {producto['nombre']} | Precio: {producto['precio']}")
    print("  (Deje en blanco para conservar el valor actual)")
    nombre = input("  Nuevo nombre: ").strip()
    categoria = input("  Nueva categoría: ").strip()
    unidad = input("  Nueva unidad: ").strip()
    precio_str = input("  Nuevo precio: ").strip()
    stock_str = input("  Nuevo stock mínimo: ").strip()

    if nombre:
        producto["nombre"] = nombre
    if categoria:
        producto["categoria"] = categoria
    if unidad:
        producto["unidad"] = unidad
    if precio_str:
        try:
            precio = float(precio_str.replace(",", "."))
            if precio <= 0:
                print("  [!] Precio debe ser > 0. No se actualizó el precio.")
            else:
                producto["precio"] = precio
        except ValueError:
            print("  [!] Precio inválido. No se actualizó.")
    if stock_str:
        try:
            stock = int(stock_str)
            if stock < 0:
                print("  [!] Stock mínimo debe ser >= 0. No se actualizó.")
            else:
                producto["stock_minimo"] = stock
        except ValueError:
            print("  [!] Valor inválido. No se actualizó el stock mínimo.")

    guardar_datos("productos", productos)
    print("  [OK] Producto actualizado.")


def desactivar_producto(productos: list) -> None:
    print("\n--- DESACTIVAR PRODUCTO ---")
    codigo = leer_texto("  Código del producto: ").upper()
    producto = buscar_producto(productos, codigo)
    if not producto:
        print("  [!] Producto no encontrado.")
        return
    if not producto["activo"]:
        print("  [!] El producto ya está desactivado.")
        return
    confirmar = input(f"  ¿Desactivar '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmar == "s":
        producto["activo"] = False
        guardar_datos("productos", productos)
        print("  [OK] Producto desactivado. Se conserva el historial.")
    else:
        print("  Operación cancelada.")


def menu_productos(productos: list) -> None:
    while True:
        print("\n========== GESTIÓN DE PRODUCTOS ==========")
        print("  1. Registrar producto")
        print("  2. Listar productos activos")
        print("  3. Listar todos (activos e inactivos)")
        print("  4. Buscar por código o nombre")
        print("  5. Actualizar producto")
        print("  6. Desactivar producto")
        print("  0. Volver")
        op = input("  Opción: ").strip()
        if op == "1":
            registrar_producto(productos)
        elif op == "2":
            listar_productos(productos, solo_activos=True)
        elif op == "3":
            listar_productos(productos, solo_activos=False)
        elif op == "4":
            buscar_productos_texto(productos)
        elif op == "5":
            actualizar_producto(productos)
        elif op == "6":
            desactivar_producto(productos)
        elif op == "0":
            break
        else:
            print("  [!] Opción no válida.")
        if op != "0":
            pausar()


# ============================================================
# LOTES PRODUCTIVOS
# ============================================================
def buscar_lote(lotes: list, id_lote: str) -> dict | None:
    id_lote = id_lote.upper().strip()
    for l in lotes:
        if l["id_lote"] == id_lote:
            return l
    return None


def registrar_lote(lotes: list, productos: list) -> None:
    print("\n--- REGISTRAR LOTE PRODUCTIVO ---")
    id_lote = generar_id("L", lotes, "id_lote")
    print(f"  ID generado: {id_lote}")
    codigo_prod = leer_texto("  Código del producto asociado: ").upper()
    producto = buscar_producto(productos, codigo_prod)
    if not producto:
        print("  [!] El producto no existe.")
        return
    if not producto["activo"]:
        print("  [!] No se puede asociar a un producto desactivado.")
        return
    fecha = leer_texto("  Fecha de siembra (YYYY-MM-DD): ")
    area = leer_flotante("  Área (m²): ", minimo=0.01)

    lote = {
        "id_lote": id_lote,
        "producto_codigo": codigo_prod,
        "fecha_siembra": fecha,
        "area_m2": area,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION",
    }
    lotes.append(lote)
    guardar_datos("lotes", lotes)
    print(f"  [OK] Lote {id_lote} registrado en producción.")


def listar_lotes(lotes: list, productos: list) -> None:
    print("\n--- LISTADO DE LOTES ---")
    if not lotes:
        print("  No hay lotes registrados.")
        return
    print(f"  {'ID':<8} {'Producto':<10} {'Fecha':<12} {'Área m²':>10} {'Cant.':>8} {'Estado':<15}")
    print("  " + "-" * 70)
    for l in lotes:
        print(f"  {l['id_lote']:<8} {l['producto_codigo']:<10} {l['fecha_siembra']:<12} "
              f"{l['area_m2']:>10.1f} {l['cantidad_producida']:>8} {l['estado']:<15}")


def cambiar_estado_lote(lotes: list) -> None:
    print("\n--- CAMBIAR ESTADO DE LOTE ---")
    id_lote = leer_texto("  ID del lote: ").upper()
    lote = buscar_lote(lotes, id_lote)
    if not lote:
        print("  [!] Lote no encontrado.")
        return
    print(f"  Estado actual: {lote['estado']}")
    print("  Estados posibles: EN_PRODUCCION | COSECHADO | CANCELADO")
    nuevo = leer_texto("  Nuevo estado: ").upper().replace(" ", "_")
    if nuevo not in ("EN_PRODUCCION", "COSECHADO", "CANCELADO"):
        print("  [!] Estado no válido.")
        return
    if lote["estado"] == "COSECHADO" and nuevo != "COSECHADO":
        print("  [!] Un lote cosechado no puede volver a otro estado.")
        return
    lote["estado"] = nuevo
    guardar_datos("lotes", lotes)
    print(f"  [OK] Estado actualizado a {nuevo}.")


def cosechar_lote(lotes: list, productos: list, movimientos: list) -> None:
    print("\n--- COSECHAR LOTE ---")
    id_lote = leer_texto("  ID del lote: ").upper()
    lote = buscar_lote(lotes, id_lote)
    if not lote:
        print("  [!] Lote no encontrado.")
        return
    if lote["estado"] == "COSECHADO":
        print("  [!] Este lote ya fue cosechado. No se puede cosechar dos veces.")
        return
    if lote["estado"] == "CANCELADO":
        print("  [!] No se puede cosechar un lote cancelado.")
        return
    producto = buscar_producto(productos, lote["producto_codigo"])
    if not producto or not producto["activo"]:
        print("  [!] El producto asociado no está disponible.")
        return
    cantidad = leer_entero("  Cantidad producida: ", minimo=1)
    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    # Generar entrada automática de inventario
    id_mov = generar_id("M", movimientos)
    movimiento = {
        "id": id_mov,
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha lote {id_lote}",
        "fecha": fecha_hora_actual(),
    }
    movimientos.append(movimiento)
    guardar_datos("lotes", lotes)
    guardar_datos("movimientos", movimientos)
    print(f"  [OK] Lote {id_lote} cosechado. Entrada de inventario {id_mov} generada (+{cantidad}).")


def menu_lotes(lotes: list, productos: list, movimientos: list) -> None:
    while True:
        print("\n========== GESTIÓN DE LOTES PRODUCTIVOS ==========")
        print("  1. Registrar lote")
        print("  2. Listar lotes")
        print("  3. Cambiar estado de lote")
        print("  4. Cosechar lote (genera entrada de inventario)")
        print("  0. Volver")
        op = input("  Opción: ").strip()
        if op == "1":
            registrar_lote(lotes, productos)
        elif op == "2":
            listar_lotes(lotes, productos)
        elif op == "3":
            cambiar_estado_lote(lotes)
        elif op == "4":
            cosechar_lote(lotes, productos, movimientos)
        elif op == "0":
            break
        else:
            print("  [!] Opción no válida.")
        if op != "0":
            pausar()


# ============================================================
# MOVIMIENTOS DE INVENTARIO
# ============================================================
def registrar_entrada(movimientos: list, productos: list) -> None:
    print("\n--- ENTRADA MANUAL DE INVENTARIO ---")
    codigo = leer_texto("  Código del producto: ").upper()
    producto = buscar_producto(productos, codigo)
    if not producto:
        print("  [!] Producto no encontrado.")
        return
    if not producto["activo"]:
        print("  [!] No se pueden registrar entradas a productos desactivados.")
        return
    cantidad = leer_entero("  Cantidad: ", minimo=1)
    motivo = leer_texto("  Motivo (obligatorio): ")
    id_mov = generar_id("M", movimientos)
    movimiento = {
        "id": id_mov,
        "producto_codigo": codigo,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_hora_actual(),
    }
    movimientos.append(movimiento)
    guardar_datos("movimientos", movimientos)
    print(f"  [OK] Entrada {id_mov} registrada. Stock actual: {calcular_stock(codigo, movimientos)}")


def registrar_salida(movimientos: list, productos: list) -> None:
    print("\n--- SALIDA MANUAL DE INVENTARIO ---")
    codigo = leer_texto("  Código del producto: ").upper()
    producto = buscar_producto(productos, codigo)
    if not producto:
        print("  [!] Producto no encontrado.")
        return
    stock_actual = calcular_stock(codigo, movimientos)
    print(f"  Stock disponible: {stock_actual}")
    cantidad = leer_entero("  Cantidad a salir: ", minimo=1)
    if cantidad > stock_actual:
        print(f"  [!] Stock insuficiente. Disponible: {stock_actual}")
        return
    motivo = leer_texto("  Motivo (obligatorio): ")
    id_mov = generar_id("M", movimientos)
    movimiento = {
        "id": id_mov,
        "producto_codigo": codigo,
        "tipo": "SALIDA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_hora_actual(),
    }
    movimientos.append(movimiento)
    guardar_datos("movimientos", movimientos)
    print(f"  [OK] Salida {id_mov} registrada. Stock actual: {calcular_stock(codigo, movimientos)}")


def listar_movimientos(movimientos: list) -> None:
    print("\n--- HISTORIAL DE MOVIMIENTOS ---")
    if not movimientos:
        print("  No hay movimientos registrados.")
        return
    print(f"  {'ID':<8} {'Producto':<10} {'Tipo':<10} {'Cant.':>6} {'Fecha':<18} Motivo")
    print("  " + "-" * 80)
    for m in movimientos:
        print(f"  {m['id']:<8} {m['producto_codigo']:<10} {m['tipo']:<10} "
              f"{m['cantidad']:>6} {m['fecha']:<18} {m['motivo']}")


def menu_inventario(movimientos: list, productos: list) -> None:
    while True:
        print("\n========== MOVIMIENTOS DE INVENTARIO ==========")
        print("  1. Registrar entrada manual")
        print("  2. Registrar salida manual")
        print("  3. Listar movimientos")
        print("  4. Consultar stock de un producto")
        print("  0. Volver")
        op = input("  Opción: ").strip()
        if op == "1":
            registrar_entrada(movimientos, productos)
        elif op == "2":
            registrar_salida(movimientos, productos)
        elif op == "3":
            listar_movimientos(movimientos)
        elif op == "4":
            codigo = leer_texto("  Código del producto: ").upper()
            stock = calcular_stock(codigo, movimientos)
            print(f"  Stock actual de {codigo}: {stock}")
        elif op == "0":
            break
        else:
            print("  [!] Opción no válida.")
        if op != "0":
            pausar()


# ============================================================
# VENTAS
# ============================================================
def registrar_venta(ventas: list, productos: list, movimientos: list) -> None:
    print("\n--- REGISTRAR VENTA ---")
    items = []
    while True:
        codigo = leer_texto("  Código del producto (o ENTER para finalizar): ", obligatorio=False).upper()
        if not codigo:
            break
        producto = buscar_producto(productos, codigo)
        if not producto:
            print("  [!] Producto no encontrado.")
            continue
        if not producto["activo"]:
            print("  [!] No se puede vender un producto desactivado.")
            continue
        stock = calcular_stock(codigo, movimientos)
        print(f"  Disponible: {stock} | Precio unitario: {producto['precio']}")
        cantidad = leer_entero("  Cantidad: ", minimo=1)
        if cantidad > stock:
            print(f"  [!] Stock insuficiente. Disponible: {stock}")
            continue
        # Verificar que no se haya superado en items previos de esta misma venta
        ya_reservado = sum(i["cantidad"] for i in items if i["codigo"] == codigo)
        if ya_reservado + cantidad > stock:
            print(f"  [!] Stock insuficiente considerando ítems ya agregados. Disponible neto: {stock - ya_reservado}")
            continue
        items.append({
            "codigo": codigo,
            "cantidad": cantidad,
            "precio_unitario": producto["precio"],
        })
        print(f"  [+] Agregado: {cantidad} x {producto['nombre']}")

    if not items:
        print("  [!] La venta debe contener al menos un ítem.")
        return

    # Verificar stock final de todos los ítems antes de confirmar
    for item in items:
        stock = calcular_stock(item["codigo"], movimientos)
        if item["cantidad"] > stock:
            print(f"  [!] Stock insuficiente para {item['codigo']} al confirmar. Operación cancelada.")
            return

    # Crear movimientos de salida y la venta
    total = 0
    for item in items:
        subtotal = item["cantidad"] * item["precio_unitario"]
        total += subtotal
        id_mov = generar_id("M", movimientos)
        movimiento = {
            "id": id_mov,
            "producto_codigo": item["codigo"],
            "tipo": "SALIDA",
            "cantidad": item["cantidad"],
            "motivo": f"Venta",
            "fecha": fecha_hora_actual(),
        }
        movimientos.append(movimiento)

    id_venta = generar_id("V", ventas)
    venta = {
        "id": id_venta,
        "fecha": fecha_hora_actual(),
        "items": items,
        "total": total,
    }
    ventas.append(venta)
    guardar_datos("movimientos", movimientos)
    guardar_datos("ventas", ventas)
    print(f"\n  [OK] Venta {id_venta} registrada. Total: ${total:,.0f}")
    for item in items:
        sub = item["cantidad"] * item["precio_unitario"]
        print(f"      - {item['codigo']}: {item['cantidad']} x ${item['precio_unitario']:,.0f} = ${sub:,.0f}")


def listar_ventas(ventas: list) -> None:
    print("\n--- CONSULTA DE VENTAS ---")
    if not ventas:
        print("  No hay ventas registradas.")
        return
    for v in ventas:
        print(f"\n  Venta {v['id']} | Fecha: {v['fecha']} | Total: ${v['total']:,.0f}")
        for item in v["items"]:
            sub = item["cantidad"] * item["precio_unitario"]
            print(f"      {item['codigo']}: {item['cantidad']} x ${item['precio_unitario']:,.0f} = ${sub:,.0f}")


def menu_ventas_consulta(ventas: list) -> None:
    listar_ventas(ventas)
    pausar()


# ============================================================
# ALERTAS Y REPORTES
# ============================================================
def mostrar_alertas(productos: list, movimientos: list) -> None:
    print("\n--- ALERTAS DE STOCK BAJO ---")
    alertas = []
    for p in productos:
        if not p["activo"]:
            continue
        stock = calcular_stock(p["codigo"], movimientos)
        if stock <= p["stock_minimo"]:
            alertas.append((p, stock))
    if not alertas:
        print("  No hay productos con stock bajo.")
        return
    print(f"  {'Código':<8} {'Nombre':<25} {'Stock':>8} {'Mínimo':>8}")
    print("  " + "-" * 55)
    for p, stock in alertas:
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {stock:>8} {p['stock_minimo']:>8}")


def reporte_existencias(productos: list, movimientos: list) -> None:
    print("\n--- REPORTE DE EXISTENCIAS Y VALOR DE INVENTARIO ---")
    total_valor = 0
    print(f"  {'Código':<8} {'Nombre':<25} {'Stock':>8} {'Precio':>10} {'Valor':>12}")
    print("  " + "-" * 70)
    for p in productos:
        if not p["activo"]:
            continue
        stock = calcular_stock(p["codigo"], movimientos)
        valor = stock * p["precio"]
        total_valor += valor
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {stock:>8} {p['precio']:>10.0f} {valor:>12,.0f}")
    print("  " + "-" * 70)
    print(f"  {'VALOR TOTAL DEL INVENTARIO:':<53} ${total_valor:>12,.0f}")


def reporte_ventas(ventas: list) -> None:
    print("\n--- REPORTE DE VENTAS ---")
    if not ventas:
        print("  No hay ventas registradas.")
        return
    num_ventas = len(ventas)
    unidades = 0
    ingresos = 0
    for v in ventas:
        ingresos += v["total"]
        for item in v["items"]:
            unidades += item["cantidad"]
    print(f"  Número de ventas      : {num_ventas}")
    print(f"  Unidades vendidas     : {unidades}")
    print(f"  Ingresos acumulados   : ${ingresos:,.0f}")


def ranking_productos(ventas: list, productos: list) -> None:
    print("\n--- TOP 3 PRODUCTOS MÁS VENDIDOS (por cantidad) ---")
    contador: dict[str, int] = {}
    for v in ventas:
        for item in v["items"]:
            contador[item["codigo"]] = contador.get(item["codigo"], 0) + item["cantidad"]
    if not contador:
        print("  No hay datos de ventas.")
        return
    ranking = sorted(contador.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"  {'#':<4} {'Código':<8} {'Nombre':<25} {'Cantidad':>10}")
    print("  " + "-" * 50)
    for i, (codigo, cant) in enumerate(ranking, 1):
        prod = buscar_producto(productos, codigo)
        nombre = prod["nombre"] if prod else "Desconocido"
        print(f"  {i:<4} {codigo:<8} {nombre[:24]:<25} {cant:>10}")


def menu_reportes(productos: list, movimientos: list, ventas: list) -> None:
    while True:
        print("\n========== REPORTES ==========")
        print("  1. Existencias y valor de inventario")
        print("  2. Resumen de ventas")
        print("  3. Ranking top 3 productos más vendidos")
        print("  0. Volver")
        op = input("  Opción: ").strip()
        if op == "1":
            reporte_existencias(productos, movimientos)
        elif op == "2":
            reporte_ventas(ventas)
        elif op == "3":
            ranking_productos(ventas, productos)
        elif op == "0":
            break
        else:
            print("  [!] Opción no válida.")
        if op != "0":
            pausar()


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
def mostrar_menu_principal():
    print("\n==================== AGROCONTROL CBA ====================")
    print("  1. Gestión de productos")
    print("  2. Gestión de lotes productivos")
    print("  3. Movimientos de inventario")
    print("  4. Registrar venta")
    print("  5. Consultar ventas")
    print("  6. Alertas de stock")
    print("  7. Reportes")
    print("  8. Guardar datos")
    print("  0. Salir")
    print("=========================================================")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Carga inicial (RF17)
    productos = cargar_datos("productos")
    lotes = cargar_datos("lotes")
    movimientos = cargar_datos("movimientos")
    ventas = cargar_datos("ventas")

    print("=" * 55)
    print("  Bienvenido a AgroControl CBA")
    print("  Sistema monolítico de gestión agropecuaria")
    print("=" * 55)
    print(f"  Productos cargados : {len(productos)}")
    print(f"  Lotes cargados     : {len(lotes)}")
    print(f"  Movimientos        : {len(movimientos)}")
    print(f"  Ventas             : {len(ventas)}")

    while True:
        mostrar_menu_principal()
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            menu_productos(productos)
        elif opcion == "2":
            menu_lotes(lotes, productos, movimientos)
        elif opcion == "3":
            menu_inventario(movimientos, productos)
        elif opcion == "4":
            registrar_venta(ventas, productos, movimientos)
            pausar()
        elif opcion == "5":
            menu_ventas_consulta(ventas)
        elif opcion == "6":
            mostrar_alertas(productos, movimientos)
            pausar()
        elif opcion == "7":
            menu_reportes(productos, movimientos, ventas)
        elif opcion == "8":
            guardar_todo(productos, lotes, movimientos, ventas)
            pausar()
        elif opcion == "0":
            guardar_todo(productos, lotes, movimientos, ventas)
            print("\n  ¡Hasta pronto! Datos guardados.")
            break
        else:
            print("  [!] Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
