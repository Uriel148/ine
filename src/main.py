import cv2
import pytesseract
import re
from dotenv import load_dotenv
import os

load_dotenv("./.env")

def recortar_credencial(imagen_path, salida_path):
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aplicar un desenfoque para reducir ruido
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    
    # Aplicar umbralización para detectar los bordes
    _, umbral = cv2.threshold(desenfoque, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Encontrar los contornos
    contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Encontrar el contorno más grande (suponiendo que es la credencial)
    contorno_principal = max(contornos, key=cv2.contourArea)
    
    # Obtener la caja delimitadora de la credencial
    x, y, w, h = cv2.boundingRect(contorno_principal)
    
    # Recortar la credencial
    credencial_recortada = imagen[y:y+h, x:x+w]
    
    # Guardar la imagen recortada
    cv2.imwrite(salida_path, credencial_recortada)

def extract_all_text(image_path):
    # Configurar Tesseract (ajusta la ruta según tu sistema)
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")  # Windows

    # Leer imagen y aplicar preprocesamiento
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #cv2.imshow("Imagen despues del treshhold", thresh)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    # Extraer todo el texto con Tesseract
    custom_config = r'--oem 3 --psm 6 -l spa'
    text = pytesseract.image_to_string(gray, config=custom_config)
    
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
    
    if match_keyword:
        # Desde la posición en que se encontró la palabra, tomar el resto del texto
        texto_desde_keyword = texto[match_keyword.end():]
        print("Texto desde 'curp':", texto_desde_keyword)
        # Buscar la primera secuencia de 18 caracteres alfanuméricos en el resto del texto
        match_curp = re.search(r'([A-Z0-9]{18})', texto_desde_keyword, re.IGNORECASE)
        if match_curp:
            return match_curp.group(1)
    
    # Si no se encontró 'curp', buscar la última secuencia de 18 caracteres alfanuméricos en todo el texto
    matches = re.findall(r'([A-Z0-9]{18})', texto, re.IGNORECASE)
    if matches:
        return matches[-1]  # Tomar la última coincidencia
    
    return None

def corregir_fecha_curp(curp):
    
    correcciones = {'O': '0', 'I': '1', 'L': '1', 'Z': '2', 'A': '4', 'S': '5', 'B': '8'}
    
    if len(curp) != 18:
        return None  # No es una CURP válida

    # Separar la CURP en partes
    parte_fija = curp[:4]  # Letras iniciales
    fecha_nacimiento = curp[4:10]  # AAMMDD (donde debe haber solo números)
    resto = curp[10:]  # Sexo, estado, consonantes internas, etc.

    # Corregir caracteres en la fecha de nacimiento
    fecha_corregida = ''.join(correcciones.get(c, c) for c in fecha_nacimiento)

    # Asegurar que la fecha ahora contenga solo números
    if not fecha_corregida.isdigit():
        return None  # Si aún hay letras, la CURP es inválida

    # Unir las partes corregidas y devolver la CURP válida
    return parte_fija + fecha_corregida + resto

def obtener_datos_curp(curp):

    if len(curp) != 18:
        return "CURP inválida, debe tener 18 caracteres."

    # Extraer la fecha de nacimiento
    anio_int = int(curp[4:6])  
    anio = curp[4:6]
    mes = curp[6:8]
    dia = curp[8:10]

    # Determinar siglo de nacimiento (asumiendo CURP moderna)
    siglo = "19" if anio_int >= 30 else "20"
    fecha_nacimiento = f"{dia}/{mes}/{siglo}{anio}"

    # Extraer el sexo
    sexo = "Hombre" if curp[10] == "H" else "Mujer"

    # Catálogo de estados según el código en la CURP
    estados = {
        "AS": "Aguascalientes", "BC": "Baja California", "BS": "Baja California Sur",
        "CC": "Campeche", "CL": "Coahuila", "CM": "Colima", "CS": "Chiapas",
        "CH": "Chihuahua", "DF": "Ciudad de México", "DG": "Durango",
        "GT": "Guanajuato", "GR": "Guerrero", "HG": "Hidalgo", "JC": "Jalisco",
        "MC": "México", "MN": "Michoacán", "MS": "Morelos", "NT": "Nayarit",
        "NL": "Nuevo León", "OC": "Oaxaca", "PL": "Puebla", "QT": "Querétaro",
        "QR": "Quintana Roo", "SP": "San Luis Potosí", "SL": "Sinaloa",
        "SR": "Sonora", "TC": "Tabasco", "TS": "Tamaulipas", "TL": "Tlaxcala",
        "VZ": "Veracruz", "YN": "Yucatán", "ZS": "Zacatecas",
        "NE": "Extranjero"
    }
    
    # Obtener el estado de nacimiento
    estado = estados.get(curp[11:13], "Desconocido")

    # Retornar los datos en un diccionario
    return {
        "fecha_nacimiento": fecha_nacimiento,
        "sexo": sexo,
        "estado": estado
    }


#image = "images/ine_test_1.jpg"
#image = "images/ine_uriel.jpg"
image = "images/img_4.jpg"

text = extract_all_text(image)
print("Text:",text)
text_clean = limpiar_texto(text)
print("Text clean:",text_clean)
curp = extraer_curp(text_clean)
curp = corregir_fecha_curp(curp)
print(curp)
datos_curp = obtener_datos_curp(curp)
print("datos_curp",datos_curp)
#datos = parse_ine_data(text)
#print(datos)

