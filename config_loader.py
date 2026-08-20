class ConfigLoader:
    def __init__(self, archivo='setup.txt'):
        self.archivo = archivo
        self.datos = {}
        self.leer_archivo()
    
    def leer_archivo(self):
        """Lee el setup.txt y guarda los datos"""
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    
                    # Ignora comentarios y lineas vacias
                    if not linea or linea.startswith('#'):
                        continue
                    
                    # Separa por igual
                    if '=' in linea:
                        clave, valor = linea.split('=', 1)
                        self.datos[clave.strip()] = valor.strip()
        
        except FileNotFoundError:
            print(f"Error: No encontre el archivo {self.archivo}")
            exit()
    
    def get_palabras_clave(self):
        """Retorna las palabras clave como lista"""
        palabras = self.datos.get('PalabrasClave', '')
        return [p.strip() for p in palabras.split(',') if p.strip()]
    
    def get_npalabras(self):
        """Retorna el numero de palabras requeridas"""
        try:
            return int(self.datos.get('NPalabras', 1))
        except:
            return 1
    
    def get_usuario(self):
        """Retorna el usuario"""
        return self.datos.get('Usuario', '')
    
    def get_contraseña(self):
        """Retorna la contraseña"""
        return self.datos.get('Contraseña', '')
    
    def validar(self):
        """Valida que todos los datos esten presentes"""
        if not self.get_palabras_clave():
            print("Error: PalabrasClave esta vacia")
            return False
        
        if not self.get_usuario():
            print("Error: Usuario esta vacio")
            return False
        
        if not self.get_contraseña():
            print("Error: Contraseña esta vacia")
            return False
        
        return True
    
    def mostrar(self):
        """Muestra la configuracion"""
        print("\n=== CONFIGURACION CARGADA ===")
        print(f"Palabras clave: {', '.join(self.get_palabras_clave())}")
        print(f"Coincidencias requeridas: {self.get_npalabras()}")
        print(f"Usuario: {self.get_usuario()}")
        print(f"Contraseña: {'*' * len(self.get_contraseña())}")
        print("=" * 30)
        print()