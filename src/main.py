import cv2
import pytesseract
import re
from dotenv import load_dotenv
import os

load_dotenv("./.env")

def extract_all_text(image_path):
    # Configurar Tesseract (ajusta la ruta según tu sistema)
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")  # Windows

    # Leer imagen y aplicar preprocesamiento
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow("Imagen despues del treshhold", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Extraer TODO el texto con Tesseract
    custom_config = r'--oem 3 --psm 6 -l spa'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    
    return text


def parse_ine_data(text):
    # Normalizar texto: eliminar saltos de línea y espacios múltiples
    text_clean = " ".join(text.replace('\n', ' ').split()).lower()

    # Expresiones regulares flexibles para campos comunes
    patterns = {
        'nombre': r'(nombre|nombre completo)\s*:?\s*([a-záéíóúñ\s]+)\b',
        'curp': r'(curp)\s*:?\s*([a-z0-9]{18})\b',
        'clave_elector': r'(clave de elector|clave)\s*:?\s*([a-z0-9]{18})\b',
        'domicilio': r'(domicilio|dirección)\s*:?\s*([a-z0-9\s,.#-]+)\b',
        'fecha_nacimiento': r'(fecha de nacimiento|nacimiento)\s*:?\s*(\d{2}/\d{2}/\d{4})',
        'vigencia': r'(vigencia|válida hasta)\s*:?\s*(\d{2}/\d{2}/\d{4})',
        'seccion': r'(sección|seccion)\s*:?\s*(\d+)',
        'folio': r'(folio)\s*:?\s*([a-z0-9]+)\b'
    }

    ine_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text_clean, re.IGNORECASE)
        if match:
            ine_data[key] = match.group(2).strip().upper() if key not in ['seccion'] else match.group(2)
        else:
            ine_data[key] = "No detectado"

    return ine_data

image = "images/ine_test_1.jpg"
text = extract_all_text(image)
print(text)

#datos = parse_ine_data(text)
#print(datos)




