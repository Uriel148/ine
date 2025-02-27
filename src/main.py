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
    
    # Definir nuevo tamaño (1280x720)
    nuevo_tamano = (1280, 720)

    # Redimensionar la imagen
    imagen_redimensionada = cv2.resize(img, nuevo_tamano, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(imagen_redimensionada, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow("Imagen despues del treshhold", gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
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
    correcciones = {'O': '0', 'I': '1', 'L': '1', 'Z': '2', 'A': '4', 'S': '5', 'B': '8'}
    if curp == None:
        return None
    if len(curp) != 18:
        return None  # No es una CURP válida

    # Separar la CURP en partes
    parte_fija = curp[:4]  # Letras iniciales
    fecha_nacimiento = curp[4:10]  # AAMMDD (donde debe haber solo números)
    resto = curp[10:16]  # Sexo, estado, consonantes internas, etc.
    ultimos_dos = curp[16:]
    # Corregir caracteres en la fecha de nacimiento
    fecha_corregida = ''.join(correcciones.get(c, c) for c in fecha_nacimiento)
    ultimos_dos_corregido = ultimos_dos.replace('O', '0')
    # Asegurar que la fecha ahora contenga solo números
    if not fecha_corregida.isdigit():
        return None  # Si aún hay letras, la CURP es inválida

    # Unir las partes corregidas y devolver la CURP válida
    return parte_fija + fecha_corregida + resto + ultimos_dos_corregido

def obtener_datos_curp(curp):
    
    if curp == None:
        return None
    
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
image = "images/img_1.jpg"

text = extract_all_text(image)
#text = extract_id_card_fields(image)
print("Text:",text)

text_clean = limpiar_texto(text)
print("Text clean:",text_clean)
curp = extraer_curp(text_clean)
curp = corregir_fecha_curp(curp)
print(curp)
datos_curp = obtener_datos_curp(curp)
print("datos_curp",datos_curp)


