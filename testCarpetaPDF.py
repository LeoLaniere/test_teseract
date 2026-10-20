import pytesseract
from pdf2image import convert_from_path
import os

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta a Poppler
poppler_path = r"C:\poppler-24.08.0\Library\bin"

# Ruta de entrada y salida
carpeta_pdfs = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\archivos_Prueba"
archivo_salida = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\resultados_ocr.txt"

# Procesar cada PDF
with open(archivo_salida, "w", encoding="utf-8") as salida:
    for nombre in os.listdir(carpeta_pdfs):
        if nombre.lower().endswith(".pdf"):
            ruta_pdf = os.path.join(carpeta_pdfs, nombre)
            try:
                # Convertir PDF a imágenes (una por página)
                paginas = convert_from_path(ruta_pdf, dpi=300, poppler_path=poppler_path)

                salida.write(f"\n--- {nombre} ---\n")
                for i, imagen in enumerate(paginas):
                    texto = pytesseract.image_to_string(imagen, lang="spa", config="--psm 6")
                    salida.write(f"\n[página {i + 1}]\n{texto.strip()}\n")

                print(f"[✔] Procesado: {nombre}")
            except Exception as e:
                print(f"[✖] Error con {nombre}: {e}")