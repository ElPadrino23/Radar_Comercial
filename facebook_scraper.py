from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os

class FacebookScraper:
    def __init__(self, usar_cookies=True):
        self.cookies_file = 'cookies.pkl'
        self.driver = None
        
        if usar_cookies and os.path.exists(self.cookies_file):
            print("Cargando cookies guardadas...")
            self.iniciar_navegador()
            self.cargar_cookies()
        else:
            print("Abriendo navegador...")
            self.iniciar_navegador()
    
    def iniciar_navegador(self):
        """Abre el navegador"""
        self.driver = webdriver.Chrome()
        time.sleep(2)
    
    def guardar_cookies(self):
        """Guarda las cookies"""
        print("Guardando cookies...")
        cookies = self.driver.get_cookies()
        
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(cookies, f)
        
        print("Cookies guardadas en cookies.pkl")
    
    def cargar_cookies(self):
        """Carga cookies"""
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            print("Cookies cargadas correctamente")
            self.driver.get("https://www.facebook.com/marketplace")
            time.sleep(3)
        except Exception as e:
            print(f"Error cargando cookies: {e}")
    
    def buscar(self, palabra_clave):
        """Busca en Marketplace"""
        print(f"Buscando: {palabra_clave}")
        
        try:
            campo_busqueda = self.driver.find_element(By.XPATH, "//input[@placeholder='Buscar en Marketplace']")
            campo_busqueda.clear()
            campo_busqueda.send_keys(palabra_clave)
            time.sleep(1)
            campo_busqueda.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Scroll para cargar mas items
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        
        except Exception as e:
            print(f"Error en busqueda: {e}")
    
    def extraer_publicaciones(self):
        """Extrae publicaciones usando Selenium"""
        publicaciones = []
        
        try:
            print("Extrayendo items...")
            
            # Busca todos los links en la pagina
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/marketplace/item/')]")
            
            print(f"Encontrados {len(links)} links")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    
                    # Intenta obtener el texto del link
                    texto = link.text.strip()
                    
                    if href and texto and len(texto) > 2:
                        publicacion = {
                            'enlace': href,
                            'nombre_perfil': texto,
                            'fecha': 'No detectada',
                            'lugar': 'No detectado'
                        }
                        publicaciones.append(publicacion)
                
                except:
                    pass
        
        except Exception as e:
            print(f"Error extrayendo: {e}")
        
        return publicaciones
    
    def cerrar(self):
        """Cierra navegador"""
        if self.driver:
            self.guardar_cookies()
            print("Cerrando navegador...")
            self.driver.quit()