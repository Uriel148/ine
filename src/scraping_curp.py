from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def curp_scraping(curp):
    
    datos_completos = {}
    
    # Inicializar el WebDriver para Edge
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)

    # URL de la página de consulta
    url = "https://www.gob.mx/curp/"
    driver.get(url)

    # Espera explícita para esperar a que los elementos se carguen (hasta 10 segundos)
    wait = WebDriverWait(driver, 10)

    try:
        # Esperar a que el campo de entrada esté presente y capturarlo
        input_curp = wait.until(EC.presence_of_element_located((By.ID, "curpinput")))
        input_curp.clear()
        input_curp.send_keys(curp)

        # Encontrar y hacer clic en el botón de consulta
        consultar_btn = wait.until(EC.element_to_be_clickable((By.ID, "searchButton")))
        consultar_btn.click()
            
        # Esperar a que se muestren los resultados
        #resultado = wait.until(EC.presence_of_element_located((By.ID, "resultado")))
        tablas = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
        
        for tabla in tablas:
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) == 2:  # Asegurar que hay clave y valor
                    clave = celdas[0].text.strip().replace(":", "")  # Quitar los ":"
                    valor = celdas[1].text.strip()
                    datos_completos[clave] = valor
        """
        # Recorrer todas las tablas y extraer su contenido
        for i, tabla in enumerate(tablas, start=1):
            print(f"Contenido de la Tabla {i}:")
            print(tabla.text)
            print("-" * 40)"""

    except Exception as e:
        print(f"Ocurrió un error al procesar la CURP {curp}: {e}")
        driver.get(url)  # Volver a la página principal en caso de error

    # Cerrar el navegador
    driver.quit()
    
    return datos_completos

curp = input("Introduzca la CURP: ")
datos = curp_scraping(curp)
datos["Localidad"] = input("Introduzca la Localidad: ")
print(datos)