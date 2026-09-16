# AgroControl CBA

**Sistema monolítico para gestión de producción, inventario y ventas**

Centro de Biotecnología Agropecuaria – CBA  
Servicio Nacional de Aprendizaje – SENA  
Facatativá, Cundinamarca

---

## Descripción

AgroControl CBA es una aplicación de consola desarrollada en Python que centraliza el control de:

- Productos comercializables
- Lotes productivos
- Movimientos de inventario (entradas y salidas)
- Ventas
- Alertas de stock bajo
- Reportes operativos

Toda la información se persiste en archivos JSON locales. El sistema aplica reglas de negocio que evitan inconsistencias (stock negativo, doble cosecha, venta de productos inactivos, etc.).

---

## Tecnologías

- Python 3 (biblioteca estándar)
- JSON para persistencia
- Git / GitHub para control de versiones

**No se utilizan** bases de datos, frameworks web ni librerías externas.

---

## Estructura del proyecto

```
agrocontrol_cba/
├── main.py                 # Punto de entrada único (aplicación monolítica)
├── data/
│   ├── productos.json
│   ├── lotes.json
│   ├── movimientos.json
│   └── ventas.json
├── README.md
└── .gitignore
```

---

## Instrucciones de ejecución

1. Clonar o descargar el repositorio.
2. Abrir una terminal en la carpeta `agrocontrol_cba`.
3. Ejecutar:

```bash
python main.py
```

o

```bash
python3 main.py
```

Al iniciar, si los archivos JSON no existen, se crean colecciones vacías automáticamente.

---

## Menú principal

```
==================== AGROCONTROL CBA ====================
1. Gestión de productos
2. Gestión de lotes productivos
3. Movimientos de inventario
4. Registrar venta
5. Consultar ventas
6. Alertas de stock
7. Reportes
8. Guardar datos
0. Salir
```

---

## Reglas de negocio principales

1. Códigos de producto y lote son únicos y se almacenan en mayúscula.
2. Un producto desactivado conserva su historial, pero no puede usarse en nuevos lotes ni ventas.
3. El stock actual **no se guarda** como campo aislado: se calcula a partir de los movimientos de inventario.
4. Salidas y ventas nunca dejan el stock en valores negativos.
5. Un lote solo puede cosecharse una vez. Al cosecharse genera automáticamente una entrada de inventario.
6. Una venta debe contener al menos un ítem válido.
7. El precio de la venta se toma del precio vigente del producto al momento del registro.
8. Toda operación que modifica datos guarda inmediatamente en JSON.
9. Identificadores secuenciales: M0001, V0001, L001, etc.

---

## Módulos lógicos

| Módulo       | Responsabilidad                                      |
|--------------|------------------------------------------------------|
| Productos    | CRUD lógico + desactivación                          |
| Lotes        | Registro, cambio de estado y cosecha                 |
| Inventario   | Entradas/salidas controladas y cálculo de stock      |
| Ventas       | Registro multi-ítem con descuento de inventario      |
| Alertas      | Productos con stock ≤ stock mínimo                   |
| Reportes     | Existencias, valor de inventario, resumen de ventas y ranking top 3 |
| Persistencia | Carga y guardado automático en JSON                  |

---

## Pruebas mínimas recomendadas

| Código | Caso                    | Resultado esperado                          |
|--------|-------------------------|---------------------------------------------|
| PF001  | Producto duplicado      | Rechaza el segundo registro                 |
| PF002  | Precio inválido         | Solicita valor válido                       |
| PF003  | Cosechar lote inexistente | Informa que no existe                     |
| PF004  | Doble cosecha           | Rechaza la segunda operación                |
| PF005  | Salida excesiva         | Impide la operación                         |
| PF006  | Venta válida            | Crea venta y reduce stock                   |
| PF007  | Venta múltiple          | Calcula subtotales y total                  |
| PF008  | Persistencia            | Datos se conservan al reiniciar             |
| PF009  | Alerta de stock         | Aparece en el reporte de alertas            |

---

## Autores

Aprendices de Técnico en Programación de Software  
Centro de Biotecnología Agropecuaria – SENA

---

## Licencia

Uso educativo – SENA CBA
