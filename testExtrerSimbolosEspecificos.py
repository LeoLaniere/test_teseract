import re
import pytesseract
from pdf2image import convert_from_path
import os
import pandas as pd

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta a Poppler
poppler_path = r"C:\poppler-24.08.0\Library\bin"

# Ruta de entrada y salida
carpeta_pdfs = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\archivos_Prueba"
archivo_salida = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\resultados_ocr.txt"
archivo_excel = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\resultado_datos_filtrados.xlsx"



def extraer_datos(texto):
    datos = {}

    # Número de factura (ej. FACTURA 0123-456)
    factura = re.search(r'\bFactura\s?\d{3,4}-\d{3,6}\b', texto)
    if factura:
        datos["Factura"] = factura.group()

    # Litros (ej. 300, 1.200, etc.)
    litros = re.search(r'\b\d{2,3}[,]\d{1,4}\b', texto)
    if litros:
        datos["Litros"] = litros.group()

    # Fecha (ej. 13/05/2025 o 13-05-25)
    fecha = re.search(r'\b\d{1,2}[/]\d{1,2}[/]\d{2,4}\b', texto)
    if fecha:
        datos["Fecha"] = fecha.group()

    # Importe final (ej. $12.345,67 o 12345.67)
    importe = re.search(r'\b\d{1,2}[.]\d{3}[,]\d{2,4}\b', texto)
    if importe:
        datos["Importe"] = importe.group()

    # Patente argentina (ej. ABC123 o AB 123 CD)
    patente = re.search(r'\b[A-Z]{2}\s?\d{3}\s?[A-Z]{2}\b', texto)
    if patente:
        datos["Patente"] = patente.group()

    return datos

# Lista para guardar los datos de cada archivo
datos_totales = []

# Procesar cada PDF
for nombre in os.listdir(carpeta_pdfs):
    if nombre.lower().endswith(".pdf"):
        ruta_pdf = os.path.join(carpeta_pdfs, nombre)
        try:
            paginas = convert_from_path(ruta_pdf, dpi=300, poppler_path=poppler_path)

            texto_completo = ""
            for imagen in paginas:
                texto_completo += pytesseract.image_to_string(imagen, lang="spa", config="--psm 6") + "\n"

            datos = extraer_datos(texto_completo)
            datos["Archivo"] = nombre  # Agregamos nombre del PDF
            datos_totales.append(datos)

            print(f"[✔] Procesado: {nombre}")
        except Exception as e:
            print(f"[✖] Error con {nombre}: {e}")

# Crear un DataFrame y guardar en Excel
df = pd.DataFrame(datos_totales, columns=["Archivo", "Factura", "Fecha", "Litros", "Importe", "Patente"])
df.to_excel(archivo_excel, index=False)

print(f"\n✅ Datos exportados a: {archivo_excel}")