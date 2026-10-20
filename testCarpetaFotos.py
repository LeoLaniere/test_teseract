import pytesseract
import cv2
import os

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta a la carpeta de imágenes
carpeta_imagenes = r"G:\Unidades compartidas\Transporte\.Gastos y Remitos RDN DDN\2025\5. Mayo\Pendiente\Alejandro Barrios"  # Cambiar por tu ruta real
archivo_salida = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\resultados_ocr.txt"

# Extensiones válidas
extensiones = (".png", ".jpg", ".jpeg", ".bmp", ".tif")

# Función para mejorar la imagen
def preprocesar_imagen(ruta):
    imagen = cv2.imread(ruta)
    # Aumentar tamaño (para que Tesseract vea mejor)
    imagen = cv2.resize(imagen, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    # Suavizado leve
    suavizada = cv2.GaussianBlur(gris, (5, 5), 0)
    return suavizada

# Procesamiento por lote
with open(archivo_salida, "w", encoding="utf-8") as salida:
    for nombre in os.listdir(carpeta_imagenes):
        if nombre.lower().endswith(extensiones):
            ruta = os.path.join(carpeta_imagenes, nombre)
            try:
                imagen = preprocesar_imagen(ruta)
                texto = pytesseract.image_to_string(imagen, lang="spa")

                salida.write(f"\n--- {nombre} ---\n")
                salida.write(texto.strip() + "\n")
                print(f"[✔] Procesado: {nombre}")
            except Exception as e:
                print(f"[✖] Error con {nombre}: {e}")
