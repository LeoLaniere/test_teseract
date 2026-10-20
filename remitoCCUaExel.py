import pytesseract
import cv2
import re
import os
import pandas as pd
from collections import defaultdict, Counter

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Carpetas
carpeta_imagenes = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\imagenes_test"
archivo_excel = r"C:/Users/Usuario/Desktop/Leo/testeTeseract/resultado_validado_con_confianza.xlsx"

# Extensiones válidas
extensiones_validas = (".jpg", ".jpeg", ".png", ".bmp", ".tif")

# Patrones buscados
patrones = {
    "Fecha": r"\b\d{2}/\d{2}/\d{2,4}\b",
    "Remito": r"Remito.{0,20}",
    "Planilla": r"Planilla.{0,9}",
    "Domicilio": r"Domicilio.{0,50}"
}

niveles_alpha = [1.2, 1.5, 1.8, 2.0]
niveles_beta = [10, 20, 30]

# Resultados
resultados = []

for nombre_archivo in os.listdir(carpeta_imagenes):
    if nombre_archivo.lower().endswith(extensiones_validas):
        ruta = os.path.join(carpeta_imagenes, nombre_archivo)
        imagen = cv2.imread(ruta)
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        agrandada = cv2.resize(gris, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        coincidencias = defaultdict(list)

        for alpha in niveles_alpha:
            for beta in niveles_beta:
                ajustada = cv2.convertScaleAbs(agrandada, alpha=alpha, beta=beta)
                _, binarizada = cv2.threshold(ajustada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                texto = pytesseract.image_to_string(binarizada, lang="spa", config="--psm 6")

                for campo, patron in patrones.items():
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        valor = match.group().strip()
                        coincidencias[campo].append(valor)

        resultado_final = {"Archivo": nombre_archivo}

        for campo in ["Fecha", "Remito", "Planilla", "Domicilio"]:
            valores = coincidencias[campo]
            if valores:
                conteo = Counter(valores)
                valor_mas_frecuente, repeticiones = conteo.most_common(1)[0]
                resultado_final[campo] = valor_mas_frecuente
                resultado_final[f"Confianza_{campo}"] = "✔ Validado" if repeticiones > 1 else "⚠ Único"
            else:
                resultado_final[campo] = ""
                resultado_final[f"Confianza_{campo}"] = "✖ No encontrado"

        resultados.append(resultado_final)
        print(f"[✔] {nombre_archivo} procesada")

# Columnas ordenadas
columnas = [
    "Archivo", "Fecha", "Remito", "Planilla", "Domicilio",
    "Confianza_Fecha", "Confianza_Remito", "Confianza_Planilla", "Confianza_Domicilio"
]

df = pd.DataFrame(resultados)
df = df[columnas]
df.to_excel(archivo_excel, index=False)

print(f"\n✅ Excel generado: {archivo_excel}")
