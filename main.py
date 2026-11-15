# Módulo principal para iniciar la Interfaz Gráfica del Sistema de Control de Abarrotes.

import tkinter as tk
from gui.ventanaPrincipal import VentanaPrincipal

if __name__ == "__main__":
    # Inicialización de la ventana raíz de Tkinter
    raiz = tk.Tk()
    
    # Instanciación de la ventana principal conectada al sistema
    app = VentanaPrincipal(raiz)
    
    # Ejecución del bucle principal de la interfaz gráfica
    raiz.mainloop()
