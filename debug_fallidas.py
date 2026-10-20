import pytesseract
import cv2
import re
import os
import numpy as np

# Ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Carpetas
carpeta_imagenes = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\imagenes_test _facturas"
carpeta_resultados = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\fallidas_debug"
os.makedirs(carpeta_resultados, exist_ok=True)

# Patrones a buscar por campo
patrones = {
    "Fecha": r"\b\d{2}/\d{2}/\d{2,4}\b",
    "Factura": r"(?i)n\s*[úu]\s*m\s*e\s*r\s*o.{0,50}\d{2,4}[-\s]?\d{5,7}",
    "Planilla": r"(?i)planilla.{0,10}\d{5,10}",
    "Domicilio": r"(?i)d\s*o?\s*m\s*i\s*c\s*i?\s*l?\s*i?\s*o?.{0,40}\(?\d{4}-\d{1,3}\)?[^:\n]{5,80}"
}
campos = set(patrones.keys())
psm_config = "--psm 3"

# Niveles de contraste y brillo
niveles_alpha = [1.2, 1.5, 1.8, 2.0]
niveles_beta  = [10, 20, 30]

# Función para detectar qué campos aparecen en un texto
def detectar_campos_en_texto(texto):
    encontrados = set()
    for campo, patron in patrones.items():
        if re.search(patron, texto, re.IGNORECASE):
            encontrados.add(campo)
    return encontrados

# Procesar imágenes
fallidas = []

for nombre in os.listdir(carpeta_imagenes):
    if not nombre.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif")):
        continue

    ruta = os.path.join(carpeta_imagenes, nombre)
    img = cv2.imread(ruta)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    agrandada = cv2.resize(gris, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    filtros_data = []
    campos_encontrados = set()

    # Función interna para procesar imagen y recolectar datos
    def procesar_filtro(nombre_filtro, imagen_proc):
        texto = pytesseract.image_to_string(imagen_proc, lang="spa", config=psm_config)
        encontrados = detectar_campos_en_texto(texto)
        campos_encontrados.update(encontrados)
        filtros_data.append((nombre_filtro, imagen_proc.copy(), texto))

    # a) normal
    for alpha in niveles_alpha:
        for beta in niveles_beta:
            ajustada = cv2.convertScaleAbs(agrandada, alpha=alpha, beta=beta)
            _, binar = cv2.threshold(ajustada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            procesar_filtro(f"normal_{alpha}_{beta}", binar)

    # b) oscura
    oscurecida = cv2.convertScaleAbs(agrandada, alpha=1.0, beta=-30)
    _, bin_osc = cv2.threshold(oscurecida, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    procesar_filtro("oscura", bin_osc)

    # c) CLAHE + blur
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    igualada = clahe.apply(agrandada)
    suavizada = cv2.GaussianBlur(igualada, (3, 3), 0)
    _, bin_clahe = cv2.threshold(suavizada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    procesar_filtro("clahe", bin_clahe)

    # d) sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(agrandada, -1, kernel)
    _, bin_sharp = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    procesar_filtro("sharpen", bin_sharp)

    # ¿Detectó todos los campos entre todos los filtros?
    if campos_encontrados != campos:
        base = os.path.splitext(nombre)[0]
        for filtro, img, texto in filtros_data:
            cv2.imwrite(os.path.join(carpeta_resultados, f"{base}_{filtro}.png"), img)
            with open(os.path.join(carpeta_resultados, f"{base}_{filtro}.txt"), "w", encoding="utf-8") as f:
                f.write(texto)
        fallidas.append(nombre)

# Reporte
print(f"\n🛑 Total imágenes que NO detectaron todos los campos: {len(fallidas)}")
for archivo in fallidas:
    print(" -", archivo)
