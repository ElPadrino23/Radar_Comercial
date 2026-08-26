from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os
import random

class FacebookScraper:
    def __init__(self, usar_cookies=True):
        self.cookies_file = 'cookies.pkl'
        self.driver = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        if usar_cookies and os.path.exists(self.cookies_file):
            print("Cargando cookies guardadas...")
            self.iniciar_navegador()
            self.cargar_cookies()
        else:
            print("Abriendo navegador...")
            self.iniciar_navegador()
    
    def delay_aleatorio(self, minimo=1, maximo=3):
        """Crea delay aleatorio para evitar deteccion"""
        tiempo = random.uniform(minimo, maximo)
        time.sleep(tiempo)
    
    def iniciar_navegador(self):
        """Abre el navegador con opciones anti-deteccion"""
        print("Abriendo navegador con anti-deteccion...")
        
        options = webdriver.ChromeOptions()
        # Usuario agent aleatorio
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'user-agent={user_agent}')
        
        # Otras opciones anti-bot
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.delay_aleatorio(1, 2)
    
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
            self.delay_aleatorio(2, 3)
            
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            print("Cookies cargadas correctamente")
            self.driver.get("https://www.facebook.com/marketplace")
            self.delay_aleatorio(3, 4)
        except Exception as e:
            print(f"Error cargando cookies: {e}")
    
    def buscar(self, palabra_clave):
        """Busca en Marketplace"""
        print(f"Buscando: {palabra_clave}")
        
        try:
            campo_busqueda = self.driver.find_element(By.XPATH, "//input[@placeholder='Buscar en Marketplace']")
            campo_busqueda.clear()
            self.delay_aleatorio(0.5, 1)
            
            campo_busqueda.send_keys(palabra_clave)
            self.delay_aleatorio(1, 2)
            
            campo_busqueda.send_keys(Keys.RETURN)
            self.delay_aleatorio(3, 5)
            
            # Scroll infinito para cargar mas items
            self.scroll_infinito()
        
        except Exception as e:
            print(f"Error en busqueda: {e}")
    
    def scroll_infinito(self):
        """Scroll infinito para cargar todos los items"""
        print("Cargando items con scroll infinito...")
        
        ultima_altura = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        max_scrolls = 10  # Maximo de scrolls
        
        while scrolls < max_scrolls:
            # Scroll hacia abajo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.delay_aleatorio(2, 4)
            
            # Calcula nueva altura y compara
            nueva_altura = self.driver.execute_script("return document.body.scrollHeight")
            
            if nueva_altura == ultima_altura:
                print("Se alcanzó el final de la página")
                break
            
            ultima_altura = nueva_altura
            scrolls += 1
            print(f"Scroll {scrolls}/{max_scrolls}")
    
    def extraer_publicaciones(self):
        """Extrae publicaciones usando Selenium"""
        publicaciones = []
        
        try:
            print("Extrayendo items...")
            self.delay_aleatorio(1, 2)
            
            # Busca todos los links en la pagina
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/marketplace/item/')]")
            
            print(f"Encontrados {len(links)} links")
            
            for i, link in enumerate(links):
                try:
                    href = link.get_attribute('href')
                    texto = link.text.strip()
                    
                    if href and texto and len(texto) > 2:
                        publicacion = {
                            'enlace': href,
                            'nombre_perfil': texto,
                            'fecha': 'No detectada',
                            'lugar': 'No detectado'
                        }
                        publicaciones.append(publicacion)
                    
                    # Delay aleatorio cada 5 items para simular usuario real
                    if (i + 1) % 5 == 0:
                        self.delay_aleatorio(0.5, 1.5)
                
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
            self.delay_aleatorio(1, 2)
            self.driver.quit()
