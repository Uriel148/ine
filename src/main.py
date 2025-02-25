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

def limpiar_texto(texto):
    # Eliminar signos de puntuación y caracteres especiales (excepto letras con acentos y números)
    texto_limpio = re.sub(r'[^a-zA-Z0-9\sáéíóúÁÉÍÓÚ]', '', texto)
    
    # Eliminar letras sueltas (palabras de un solo carácter sin acento)
    texto_limpio = re.sub(r'\b[a-zA-Z]\b', '', texto_limpio)
    
    # Eliminar números sueltos (que no estén junto a otro número o letra)
    texto_limpio = re.sub(r'\b[0-9]\b', '', texto_limpio)
    
    # Eliminar espacios extra generados
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    return texto_limpio

def extraer_curp(texto):
    # Buscar la palabra 'curp'
    patron_keyword = re.compile(r'curp', re.IGNORECASE)
    match_keyword = patron_keyword.search(texto)
    if not match_keyword:
        return None  # No se encontró la palabra 'curp'
    
    # Desde la posición en que se encontró la palabra, tomar el resto del texto
    texto_desde_keyword = texto[match_keyword.end():]
    print("texto desde curp",texto_desde_keyword)
    # Buscar la primera secuencia de 18 caracteres alfanuméricos en el resto del texto
    match_curp = re.search(r'([A-Z0-9]{16})', texto_desde_keyword, re.IGNORECASE)
    if match_curp:
        return match_curp.group(1)
    return None

#image = "images/ine_test_1.jpg"
image = "images/ine_test_1.jpg"
text = extract_all_text(image)
print("Text:",text)
text_clean = limpiar_texto(text)
print("Text clean:",text_clean)
curp = extraer_curp(text_clean)
print("Curp:",curp)

#datos = parse_ine_data(text)
#print(datos)




