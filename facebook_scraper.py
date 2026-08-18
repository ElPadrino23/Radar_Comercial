from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class FacebookScraper:
    def __init__(self, usuario, contraseña):
        self.usuario = usuario
        self.contraseña = contraseña
        self.driver = None
        self.iniciar_navegador()
    
    def iniciar_navegador(self):
        """Abre el navegador"""
        print("Abriendo navegador...")
        self.driver = webdriver.Chrome()
    
    def login(self):
        """Hace login en Facebook"""
        print("Iniciando sesion en Facebook...")
        
        # Abre Facebook
        self.driver.get("https://www.facebook.com/login")
        time.sleep(2)
        
        try:
            # Ingresa usuario
            print("Ingresando usuario...")
            campo_usuario = self.driver.find_element(By.NAME, "email")
            campo_usuario.send_keys(self.usuario)
            time.sleep(1)
            
            # Ingresa contraseña
            print("Ingresando contraseña...")
            campo_contraseña = self.driver.find_element(By.NAME, "pass")
            campo_contraseña.send_keys(self.contraseña)
            time.sleep(1)
            
            # Click en boton login
            print("Haciendo click en Iniciar sesion...")
            boton_login = self.driver.find_element(By.NAME, "login")
            boton_login.click()
            
            # Espera a que aparezca la pantalla de 2FA o que se complete el login
            time.sleep(3)
            
            # Verifica si hay pantalla de 2FA
            try:
                pantalla_2fa = self.driver.find_element(By.XPATH, "//input[@placeholder='Codigo de 6 digitos']")
                print("\n!!! PANTALLA DE 2FA DETECTADA !!!")
                print("Facebook te ha enviado un codigo a tu Mac")
                print("Por favor:")
                print("1. Revisa tu Mac (notificacion o ventana)")
                print("2. Completa el 2FA en el navegador")
                print("3. Presiona Enter aqui cuando termines")
                print()
                
                # Espera a que el usuario presione Enter
                input(">>> Presiona Enter cuando hayas completado el 2FA: ")
                
                # Espera a que se procese el login
                time.sleep(5)
                
            except:
                # No hay pantalla de 2FA, continua normal
                print("No se detecto 2FA, continuando...")
                time.sleep(3)
            
            # Verifica que este logueado (espera a que cargue la pagina principal)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Comprar')]"))
                )
                print("Login exitoso!\n")
                return True
            except:
                # Si no encuentra elemento, pero la URL cambio, tambien esta bien
                if "facebook.com" in self.driver.current_url:
                    print("Login aparentemente exitoso!\n")
                    return True
                else:
                    print("Error: No se logro completar el login")
                    return False
        
        except Exception as e:
            print(f"Error en login: {e}")
            return False
    
    def ir_marketplace(self):
        """Va a Marketplace de Facebook"""
        print("Yendo a Marketplace...")
        self.driver.get("https://www.facebook.com/marketplace/category/2400")
        time.sleep(3)
    
    def buscar(self, palabra_clave):
        """Busca una palabra clave en Marketplace"""
        print(f"Buscando: {palabra_clave}")
        
        try:
            # Busca el campo de busqueda
            campo_busqueda = self.driver.find_element(By.XPATH, "//input[@placeholder='Buscar en Marketplace']")
            campo_busqueda.clear()
            campo_busqueda.send_keys(palabra_clave)
            time.sleep(1)
            
            # Presiona Enter
            campo_busqueda.submit()
            time.sleep(3)
        
        except Exception as e:
            print(f"Error en busqueda: {e}")
    
    def extraer_publicaciones(self):
        """Extrae las publicaciones de la pagina actual"""
        publicaciones = []
        
        try:
            # Obtiene el HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Busca todos los items (esto puede variar segun estructura de FB)
            items = soup.find_all('div', class_='x1iyjqo2')
            
            print(f"Encontrados {len(items)} items")
            
            for item in items:
                try:
                    # Extrae datos basicos
                    enlace = item.find('a')
                    nombre = item.find('span')
                    
                    if enlace and nombre:
                        url = enlace.get('href')
                        nombre_texto = nombre.get_text(strip=True)
                        
                        publicacion = {
                            'enlace': url if url.startswith('http') else f"https://facebook.com{url}",
                            'nombre_perfil': nombre_texto,
                            'fecha': 'No detectada',
                            'lugar': 'No detectado'
                        }
                        
                        publicaciones.append(publicacion)
                
                except Exception as e:
                    print(f"Error extrayendo item: {e}")
        
        except Exception as e:
            print(f"Error extrayendo publicaciones: {e}")
        
        return publicaciones
    
    def cerrar(self):
        """Cierra el navegador"""
        print("Cerrando navegador...")
        self.driver.quit()
