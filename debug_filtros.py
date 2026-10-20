import pytesseract
import cv2
import re
import os
import numpy as np

# 1. Configuración de Tesseract y rutas
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
carpeta_imagenes = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\Facturas"
salida_txt = r"C:\Users\Usuario\Desktop\Leo\testeTeseract\filter_hits.txt"
os.makedirs(os.path.dirname(salida_txt), exist_ok=True)

# 2. Patrones de Planilla (7 dígitos) y Remito (3–6 dígitos)
patron_planilla = re.compile(r"(?i)p[l1i]a?[nr][il1]?[a-z]{0,3}\s{0,3}(\d{7})")
patron_remito   = re.compile(r"(?i)remi?to.{0,20}(\d{3,6})")

# 3. Configuración de OCR y filtros
psm_config    = "--psm 3"
niveles_alpha = [1.2, 1.5, 1.8, 2.0]
niveles_beta  = [10, 20, 30]

def apply_filters(img):
    """
    Aplica distintos filtros y devuelve un dict:
      clave = nombre del filtro
      valor = imagen procesada (binaria)
    """
    filters = {}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    agr = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # a) Contraste/Brillo
    for a in niveles_alpha:
        for b in niveles_beta:
            adj = cv2.convertScaleAbs(agr, alpha=a, beta=b)
            _, binr = cv2.threshold(adj, 0, 255,
                                    cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            filters[f"normal_{a}_{b}"] = binr

    # b) Oscurecer fotos muy claras
    osc = cv2.convertScaleAbs(agr, alpha=1.0, beta=-30)
    _, bin_osc = cv2.threshold(osc, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    filters["oscura"] = bin_osc

    # c) CLAHE + GaussianBlur
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl    = clahe.apply(agr)
    blur  = cv2.GaussianBlur(cl, (3,3), 0)
    _, bin_cl = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    filters["clahe"] = bin_cl

    # d) Sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv2.filter2D(agr, -1, kernel)
    _, bin_sh = cv2.threshold(sharp, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    filters["sharpen"] = bin_sh

    # e) Gamma correction (oscurecer zonas blancas)
    inv_gamma = 1/0.5
    table = (np.array([((i/255.0)**inv_gamma)*255 for i in range(256)])
             .astype("uint8"))
    gamma_img = cv2.LUT(agr, table)
    _, bin_g = cv2.threshold(gamma_img, 0, 255,
                             cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    filters["gamma0.5"] = bin_g

    # f) Dilation (engruesa caracteres finos)
    _, base_bin = cv2.threshold(agr, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel_d = np.ones((2,2), np.uint8)
    dil      = cv2.dilate(base_bin, kernel_d, iterations=1)
    filters["dilate"] = dil

    return filters

# 4. Recorrer imágenes y anotar qué filtros matchean
with open(salida_txt, "w", encoding="utf-8") as out:
    for fname in os.listdir(carpeta_imagenes):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif")):
            continue

        path = os.path.join(carpeta_imagenes, fname)
        img  = cv2.imread(path)
        hits = []

        for filter_name, proc_img in apply_filters(img).items():
            txt = pytesseract.image_to_string(proc_img, lang="spa", config=psm_config)
            if patron_planilla.search(txt) or patron_remito.search(txt):
                hits.append(filter_name)

        if hits:
            out.write(f"{fname}: {', '.join(hits)}\n")

print(f"\n✅ Reporte de filtros generado en:\n   {salida_txt}")
