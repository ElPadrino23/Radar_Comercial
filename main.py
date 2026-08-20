from config_loader import ConfigLoader
from facebook_scraper import FacebookScraper
from datetime import datetime
import os
import csv

def guardar_csv(resultados, palabras_clave, npalabras):
    """Guarda los resultados en CSV"""
    
    if not os.path.exists('results'):
        os.makedirs('results')
    
    ahora = datetime.now()
    mes = ahora.strftime('%B')
    año = ahora.year
    archivo = f"results/resultados_{mes}_{año}.csv"
    
    print(f"Guardando en: {archivo}")
    
    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Enlace', 'Nombre del perfil', 'Fecha de publicacion', 'Lugar'])
        
        for resultado in resultados:
            writer.writerow([
                resultado['enlace'],
                resultado['nombre_perfil'],
                resultado['fecha'],
                resultado['lugar']
            ])
    
    print(f"CSV guardado! Total: {len(resultados)} registros")

def contar_coincidencias(texto, palabras_clave):
    """Cuenta coincidencias"""
    texto_lower = texto.lower()
    contador = 0
    
    for palabra in palabras_clave:
        if palabra.lower() in texto_lower:
            contador += 1
    
    return contador

def main():
    print("=== RADAR COMERCIAL ===")
    print("Sistema de busqueda en Facebook Marketplace")
    print()
    
    print("Cargando configuracion...")
    config = ConfigLoader('setup.txt')
    
    if not config.validar():
        print("Configuracion invalida!")
        return
    
    config.mostrar()
    
    palabras_clave = config.get_palabras_clave()
    npalabras = config.get_npalabras()
    
    # Verifica si hay cookies guardadas
    if os.path.exists('cookies.pkl'):
        print("Se encontraron cookies guardadas")
        print("Continuando con sesion anterior...\n")
        scraper = FacebookScraper(usar_cookies=True)
    else:
        print("\n=== PRIMERA EJECUCION ===")
        print("Abriendo navegador para hacer login...")
        print()
        
        scraper = FacebookScraper(usar_cookies=False)
        
        print("\nAhora en el navegador que se abrio:")
        print("1. Ve a facebook.com")
        print("2. Haz login con tu cuenta")
        print("3. Navega a Marketplace")
        print("4. Vuelve aqui y presiona Enter")
        print()
        
        input(">>> Presiona Enter cuando estes en Marketplace: ")
    
    print("\nIniciando busqueda...\n")
    
    todos_resultados = []
    perfiles_vistos = set()
    
    for palabra in palabras_clave:
        print(f"--- Buscando: {palabra} ---")
        
        scraper.buscar(palabra)
        publicaciones = scraper.extraer_publicaciones()
        
        for pub in publicaciones:
            nombre = pub['nombre_perfil']
            
            if nombre not in perfiles_vistos:
                coincidencias = contar_coincidencias(nombre, palabras_clave)
                
                if coincidencias >= npalabras:
                    todos_resultados.append(pub)
                    perfiles_vistos.add(nombre)
                    print(f"Alerta! Encontrado: {nombre}")
    
    scraper.cerrar()
    
    if todos_resultados:
        guardar_csv(todos_resultados, palabras_clave, npalabras)
    else:
        print("\nNo se encontraron resultados")
    
    print("\n=== BUSQUEDA FINALIZADA ===")

if __name__ == "__main__":
    main()