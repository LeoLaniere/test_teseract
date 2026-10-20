import os
import re

# Carpeta donde están los archivos .txt generados por OCR
carpeta_txt = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\fallidas_debug"

# Valor que queremos encontrar (puede ser número de planilla, remito, fecha, etc.)
valor_buscado = "10281"  # <- Cambiar por lo que quieras buscar

# Cuántos caracteres antes del match querés mostrar
caracteres_contexto = 30

# Procesar todos los .txt
print(f"\n🔍 Buscando el valor '{valor_buscado}' en los archivos...\n")
encontrados = []

for archivo in os.listdir(carpeta_txt):
    if archivo.endswith(".txt"):
        ruta = os.path.join(carpeta_txt, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
            for i, linea in enumerate(lineas):
                if valor_buscado in linea:
                    indice = linea.find(valor_buscado)
                    contexto = linea[max(0, indice - caracteres_contexto):indice + len(valor_buscado)]
                    encontrados.append((archivo, i + 1, contexto.strip()))
                    break  # Solo la primera ocurrencia por archivo

# Mostrar resultados
if encontrados:
    for arch, linea, texto in encontrados:
        print(f"📄 {arch} (línea {linea}): ...{texto}")
else:
    print("❌ No se encontró el valor en ningún archivo.")
