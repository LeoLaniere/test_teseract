import pytesseract
import cv2
import re
import os
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Carpetas
carpeta_imagenes = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\Facturas"
archivo_excel = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\resultado_validado_facturas.xlsx"

# Configuración
extensiones_validas = (".jpg", ".jpeg", ".png", ".bmp", ".tif")
patrones = {
    "Fecha": [r"\b\d{2}/\d{2}/\d{2,4}\b"],
    "Factura": [
        r"(?i)(?=\S*[numr])[\S]{3,20}\s*(\d{3,4}\s*[-–]?\s*\d{5,8})"
    ],
    "Planilla": [r"(?i)p[l1i]a?[nr][il1]?[a-z]{0,3}\s{0,3}(\d{7})"],
    "Domicilio": [
        r"(?i)d\s*o?\s*m\s*i\s*c\s*i?\s*l?\s*i?\s*o?.{0,40}(\(?\d{4}-\d{1,3}\)?[^:\n]{5,80})"
    ]
}

psm_config = "--psm 3"
resultados = []

for nombre in os.listdir(carpeta_imagenes):
    if not nombre.lower().endswith(extensiones_validas):
        continue

    ruta = os.path.join(carpeta_imagenes, nombre)
    img = cv2.imread(ruta)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    agr = cv2.resize(gris, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    coincidencias = defaultdict(list)
    fuentes = defaultdict(list)
    stop_ocr = False

    # a) normal_1.2_10
    if not stop_ocr:
        normal = cv2.convertScaleAbs(agr, alpha=1.2, beta=10)
        _, bin_normal = cv2.threshold(normal, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        nombre_filtro_actual = "normal_1.2_10"
        texto = pytesseract.image_to_string(bin_normal, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break
        if all(len(coincidencias[campo]) >= 2 for campo in patrones):
            stop_ocr = True

    # b) oscura
    if not stop_ocr:
        osc = cv2.convertScaleAbs(agr, alpha=1.0, beta=-30)
        _, bin_osc = cv2.threshold(osc, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        nombre_filtro_actual = "oscura"
        texto = pytesseract.image_to_string(bin_osc, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break
        if all(coincidencias[campo] for campo in patrones):
            stop_ocr = True

    # c) clahe
    if not stop_ocr:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        eq = clahe.apply(agr)
        blur = cv2.GaussianBlur(eq, (3, 3), 0)
        _, bin_clahe = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        nombre_filtro_actual = "clahe"
        texto = pytesseract.image_to_string(bin_clahe, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break
        if all(coincidencias[campo] for campo in patrones):
            stop_ocr = True

    # d) sharpen
    if not stop_ocr:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharp = cv2.filter2D(agr, -1, kernel)
        _, bin_sharp = cv2.threshold(sharp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        nombre_filtro_actual = "sharpen"
        texto = pytesseract.image_to_string(bin_sharp, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break

    # e) gamma0.5
    if not stop_ocr:
        inv_gamma = 1 / 0.5
        table = (np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8"))
        gamma = cv2.LUT(agr, table)
        _, bin_gamma = cv2.threshold(gamma, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        nombre_filtro_actual = "gamma0.5"
        texto = pytesseract.image_to_string(bin_gamma, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break

    # f) dilate
    if not stop_ocr:
        _, bin_dilate = cv2.threshold(agr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        dil = cv2.dilate(bin_dilate, np.ones((2, 2), np.uint8), iterations=1)
        nombre_filtro_actual = "dilate"
        texto = pytesseract.image_to_string(dil, lang="spa", config=psm_config)
        for campo, lista_patrones in patrones.items():
            if not coincidencias[campo]:
                for patron in lista_patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group(1) if match.lastindex else match.group().strip()
                        coincidencias[campo].append(valor)
                        fuentes[campo].append(nombre_filtro_actual)
                        break

    # Consolidar resultados
    fila = {"Archivo": nombre}
    for campo in ["Fecha", "Factura", "Planilla", "Domicilio"]:
        valores = coincidencias[campo]
        origenes = fuentes[campo]
        if valores:
            conteo = Counter(valores)
            valor_final, repeticiones = conteo.most_common(1)[0]
            idx = valores.index(valor_final)
            origen = origenes[idx]
            fila[campo] = valor_final
            fila[f"Confianza_{campo}"] = "✔ Validado" if repeticiones > 1 else "⚠ Único"
            fila[f"Origen_{campo}"] = origen
        else:
            fila[campo] = ""
            fila[f"Confianza_{campo}"] = "✖ No encontrado"
            fila[f"Origen_{campo}"] = "-"

    resultados.append(fila)

# Exportar Excel
columnas = [
    "Archivo", "Fecha", "Factura", "Planilla", "Domicilio",
    "Confianza_Fecha", "Confianza_Factura", "Confianza_Planilla", "Confianza_Domicilio",
    "Origen_Fecha", "Origen_Factura", "Origen_Planilla", "Origen_Domicilio"
]
df = pd.DataFrame(resultados)
df = df[columnas]
df.to_excel(archivo_excel, index=False)

print(f"\n✅ Excel generado: {archivo_excel}")
