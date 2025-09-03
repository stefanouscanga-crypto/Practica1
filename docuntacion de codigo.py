import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
# Importamos las librerías necesarias
# tkinter -> para la interfaz gráfica
# ttk -> para usar algunos widgets más modernos
# datetime -> para manejar fecha y hora actual

class Nodo:
    """Clase para crear cada nodo de mi lista enlazada de turnos"""
    def __init__(self, paciente, telefono, fecha, hora, especialidad, es_emergencia=False):
        # Constructor del nodo - cada paciente será un nodo en mi lista
        self.paciente = paciente                # Nombre del paciente
        self.telefono = telefono                # Teléfono de contacto
        self.fecha = fecha                      # Fecha del turno
        self.hora = hora                        # Hora del turno
        self.especialidad = especialidad        # Especialidad médica
        self.es_emergencia = es_emergencia      # Boolean: True si es emergencia
        self.hora_registro = datetime.now()     # Momento exacto en que se registró (para calcular tiempo de espera)
        self.siguiente = None                   # Puntero al siguiente nodo (concepto clave de listas enlazadas)

class ListaEnlazadaTurnos:
    """Mi implementación de lista enlazada para gestionar los turnos médicos"""
    # para este tipo de operaciones porque puedo insertar/eliminar en cualquier posición fácilmente
    
    def __init__(self):
        self.cabeza = None      # Primer nodo de la lista (None significa lista vacía)
        self.tamaño = 0         # Contador para saber cuántos pacientes hay
    
    def agregar_turno(self, paciente, telefono, fecha, hora, especialidad, es_emergencia=False):
        """Agregar un nuevo turno, priorizando emergencias al inicio"""
        # Creo un nuevo nodo con los datos del paciente
        nuevo_nodo = Nodo(paciente, telefono, fecha, hora, especialidad, es_emergencia)
        
        if not self.cabeza:
            # Lista vacía - el nuevo nodo se convierte en la cabeza
            self.cabeza = nuevo_nodo
        elif es_emergencia:
            # Si es emergencia, debo ponerlo al principio o después de otras emergencias
            if not self.cabeza.es_emergencia:
                # La cabeza actual no es emergencia, pongo el nuevo nodo al inicio
                nuevo_nodo.siguiente = self.cabeza
                self.cabeza = nuevo_nodo
            else:
                # Ya hay emergencias al inicio, busco dónde insertar este
                # Busco la posición después de todas las emergencias existentes
                actual = self.cabeza
                while actual.siguiente and actual.siguiente.es_emergencia:
                    actual = actual.siguiente
                # Inserto el nuevo nodo después del último nodo de emergencia
                nuevo_nodo.siguiente = actual.siguiente
                actual.siguiente = nuevo_nodo
        else:
            # Turno normal - lo agrego al final de la lista
            actual = self.cabeza
            while actual.siguiente:              # Recorro hasta el último nodo
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo        # Enlazo el último nodo con el nuevo
        
        self.tamaño += 1    # Incremento el contador
    
    def llamar_siguiente(self):
        """Llamar al siguiente paciente (eliminar el primero de la lista)"""
        # En una cola, siempre se atiende al primero (FIFO - First In, First Out)
        if not self.cabeza:
            return None     # Lista vacía
        
        # Guardo referencia al nodo que voy a eliminar
        paciente_llamado = self.cabeza
        # Muevo la cabeza al siguiente nodo
        self.cabeza = self.cabeza.siguiente
        self.tamaño -= 1
        return paciente_llamado
    
    def cancelar_turno(self, nombre_paciente):
        """Cancelar turno por nombre del paciente - eliminar nodo específico"""
        if not self.cabeza:
            return False    # Lista vacía
        
        # Si el nodo a eliminar es el primero (la cabeza)
        if self.cabeza.paciente.lower() == nombre_paciente.lower():
            self.cabeza = self.cabeza.siguiente
            self.tamaño -= 1
            return True
        
        # Si el nodo a eliminar está en otra posición
        # Necesito mantener referencia al nodo anterior para poder "saltear" el nodo a eliminar
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.paciente.lower() == nombre_paciente.lower():
                # Encontré el nodo a eliminar, lo "salteo" en la cadena de enlaces
                actual.siguiente = actual.siguiente.siguiente
                self.tamaño -= 1
                return True
            actual = actual.siguiente
        
        return False    # No se encontró el paciente
    
    def buscar_paciente(self, nombre_paciente):
        """Buscar paciente en la lista y devolver el nodo y su posición"""
        actual = self.cabeza
        posicion = 1
        
        # Recorro toda la lista buscando el paciente
        while actual:
            if actual.paciente.lower() == nombre_paciente.lower():
                return (actual, posicion)       # Retorno tupla: (nodo, posición)
            actual = actual.siguiente
            posicion += 1
        
        return (None, -1)   # No encontrado
    
    def obtener_lista_completa(self):
        """Convertir mi lista enlazada a una lista normal para mostrar en la interfaz"""
        # Esta función recorre toda mi lista enlazada y crea un diccionario con los datos
        # de cada paciente para mostrar en la tabla
        turnos = []
        actual = self.cabeza
        posicion = 1
        
        while actual:
            # Calculo el tiempo que lleva esperando este paciente
            tiempo_espera = datetime.now() - actual.hora_registro
            minutos_espera = int(tiempo_espera.total_seconds() / 60)
            
            # Creo un diccionario con todos los datos para la tabla
            turnos.append({
                'posicion': posicion,
                'paciente': actual.paciente,
                'telefono': actual.telefono,
                'hora': actual.hora,
                'especialidad': actual.especialidad,
                'tipo': 'EMERGENCIA' if actual.es_emergencia else 'NORMAL',
                'tiempo_espera': f"{minutos_espera} min"
            })
            actual = actual.siguiente
            posicion += 1
        
        return turnos
    
    def obtener_estadisticas(self):
        """Calcular estadísticas de la cola para mostrar en el panel"""
        if not self.cabeza:
            return {
                'total': 0,
                'emergencias': 0,
                'normales': 0,
                'tiempo_promedio': 0
            }
        
        # Variables para acumular estadísticas
        total = 0
        emergencias = 0
        tiempo_total = 0
        actual = self.cabeza
        
        # Recorro toda la lista acumulando datos
        while actual:
            total += 1
            if actual.es_emergencia:
                emergencias += 1
            
            # Calculo tiempo de espera y lo acumulo
            tiempo_espera = datetime.now() - actual.hora_registro
            tiempo_total += tiempo_espera.total_seconds() / 60
            actual = actual.siguiente
        
        return {
            'total': total,
            'emergencias': emergencias,
            'normales': total - emergencias,
            'tiempo_promedio': int(tiempo_total / total) if total > 0 else 0
        }

class GestorTurnosApp:
    def __init__(self, root):
        # Constructor principal - aquí inicializo todo
        self.root = root
        self.root.title("Sistema de Turnos Médicos - Cola de Atención")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")
        
        # ¡Esta es mi estructura de datos principal! Una lista enlazada que yo mismo implementé
        self.lista_turnos = ListaEnlazadaTurnos()
        
        # Tiempo estimado por consulta médica (lo investigué y 15 minutos es promedio)
        self.tiempo_por_consulta = 15
        
        self.especialidades = [
            "Medicina General", "Cardiología", "Dermatología", 
            "Neurología", "Pediatría", "Ginecología", "Traumatología"
        ]
        
        self.crear_interfaz()
        self.actualizar_interfaz()      # Llamo esto al final para inicializar la interfaz con datos vacíos
    
    # Funciones de validación - la profesora nos dijo que siempre validemos los datos del usuario
    def validar_solo_letras(self, char):
        """Valida que el carácter ingresado sea una letra, espacio o carácter especial del español"""
        # Esta función se ejecuta cada vez que el usuario presiona una tecla en los campos de nombre
        return (char.isalpha() or 
                char.isspace() or 
                char in "áéíóúüñÁÉÍÓÚÜÑ'-" or 
                char == "")     # char == "" permite borrar caracteres
    
    def validar_solo_numeros(self, char):
        """Valida que el carácter ingresado sea un número"""
        # Para el campo teléfono - solo acepto números
        return char.isdigit() or char == ""
    
    def validar_nombre_completo(self, nombre):
        """Valida que el nombre contenga solo letras y espacios"""
        if not nombre.strip():          # strip() quita espacios al inicio y final
            return False
        
        # Verificar que solo contenga caracteres válidos para nombres
        caracteres_validos = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ áéíóúüñÁÉÍÓÚÜÑ'-")
        return all(char in caracteres_validos for char in nombre)
    
    def validar_telefono_completo(self, telefono):
        """Valida que el teléfono contenga solo números"""
        if not telefono.strip():
            return False
        
        # Verificar que solo contenga números
        return telefono.isdigit()
    
    def crear_interfaz(self):
        # Este método es igual al anterior - crea la estructura visual
        # Barra superior roja
        header_frame = tk.Frame(self.root, bg="#E53E3E", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🏥 SISTEMA DE TURNOS MÉDICOS - COLA DE ATENCIÓN", 
                              font=("Segoe UI", 20, "bold"), fg="white", bg="#E53E3E")
        title_label.pack(expand=True)
        
        # Contenedor principal con tres columnas
        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Las tres columnas principales
        self.frame_registro = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=1)
        self.frame_registro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.frame_lista = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=1)
        self.frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.frame_control = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=1)
        self.frame_control.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.crear_seccion_registro()
        self.crear_seccion_lista()
        self.crear_seccion_control()
    
    def crear_seccion_registro(self):
        # Sección para registrar nuevos pacientes
        header_registro = tk.Frame(self.frame_registro, bg="#f8f9fa", height=60)
        header_registro.pack(fill=tk.X, padx=2, pady=2)
        header_registro.pack_propagate(False)
        
        icon_label = tk.Label(header_registro, text="🏥", font=("Segoe UI", 16), bg="#f8f9fa")
        icon_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        title_label = tk.Label(header_registro, text="REGISTRAR PACIENTE EN COLA", 
                              font=("Segoe UI", 12, "bold"), bg="#f8f9fa", fg="#2d3748")
        title_label.pack(side=tk.LEFT, pady=15)
        
        content_frame = tk.Frame(self.frame_registro, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configurar validaciones en tiempo real
        # register() registra las funciones para que tkinter las pueda usar en validate
        vcmd_letras = (self.root.register(self.validar_solo_letras), '%S')
        vcmd_numeros = (self.root.register(self.validar_solo_numeros), '%S')
        
        # Campo: Nombre del paciente (solo acepta letras)
        tk.Label(content_frame, text="👤 Nombre del Paciente:", 
                font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.entry_paciente = tk.Entry(content_frame, font=("Segoe UI", 10), bg="#f7fafc", 
                                      relief=tk.FLAT, bd=5, validate='key', validatecommand=vcmd_letras)
        self.entry_paciente.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Campo: Teléfono (solo acepta números)
        tk.Label(content_frame, text="📞 Teléfono:", 
                font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.entry_telefono = tk.Entry(content_frame, font=("Segoe UI", 10), bg="#f7fafc", 
                                      relief=tk.FLAT, bd=5, validate='key', validatecommand=vcmd_numeros)
        self.entry_telefono.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Campo: Fecha (pre-llenado con fecha actual)
        tk.Label(content_frame, text="📅 Fecha (DD/MM/AAAA):", 
                font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.entry_fecha = tk.Entry(content_frame, font=("Segoe UI", 10), bg="#f7fafc", 
                                   relief=tk.FLAT, bd=5)
        self.entry_fecha.pack(fill=tk.X, pady=(0, 15), ipady=5)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Campo: Hora (pre-llenado con hora actual)
        tk.Label(content_frame, text="🕐 Hora (HH:MM):", 
                font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.entry_hora = tk.Entry(content_frame, font=("Segoe UI", 10), bg="#f7fafc", 
                                  relief=tk.FLAT, bd=5)
        self.entry_hora.pack(fill=tk.X, pady=(0, 15), ipady=5)
        self.entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        
        # Campo: Especialidad (combobox desplegable)
        tk.Label(content_frame, text="🏥 Especialidad:", 
                font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.combo_especialidad = ttk.Combobox(content_frame, values=self.especialidades, 
                                              font=("Segoe UI", 10), state="readonly")
        self.combo_especialidad.pack(fill=tk.X, pady=(0, 20), ipady=5)
        
        # Checkbox para emergencias
        self.var_emergencia = tk.BooleanVar()
        check_frame = tk.Frame(content_frame, bg="white")
        check_frame.pack(fill=tk.X, pady=(0, 25))
        
        check_emergencia = tk.Checkbutton(check_frame, text="🚨 TURNO DE EMERGENCIA (PRIORIDAD)", 
                                         variable=self.var_emergencia, font=("Segoe UI", 10, "bold"),
                                         bg="white", fg="#E53E3E", selectcolor="white")
        check_emergencia.pack()
        
        # Botones con funcionalidad - ahora les asigno comando a cada uno
        btn_registrar = tk.Button(content_frame, text="➕ REGISTRAR PACIENTE", 
                                 command=self.registrar_paciente,      # ¡Aquí conecto con mi función!
                                 bg="#48BB78", fg="white",
                                 font=("Segoe UI", 11, "bold"), relief=tk.FLAT, 
                                 cursor="hand2", height=2)
        btn_registrar.pack(fill=tk.X, pady=(0, 10))
        
        btn_limpiar = tk.Button(content_frame, text="🗑 LIMPIAR CAMPOS", 
                               command=self.limpiar_campos,           # Función para limpiar formulario
                               bg="#A0AEC0", fg="white",
                               font=("Segoe UI", 11, "bold"), relief=tk.FLAT, 
                               cursor="hand2", height=2)
        btn_limpiar.pack(fill=tk.X, pady=(0, 30))
        
        # Sección consulta tiempo de espera
        consulta_frame = tk.Frame(content_frame, bg="#f8f9fa", relief=tk.FLAT, bd=1)
        consulta_frame.pack(fill=tk.X, pady=(20, 0))
        
        consulta_header = tk.Label(consulta_frame, text="🔍 CONSULTAR TIEMPO DE ESPERA", 
                                  font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#2d3748")
        consulta_header.pack(pady=15)
        
        consulta_content = tk.Frame(consulta_frame, bg="#f8f9fa")
        consulta_content.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(consulta_content, text="Nombre del Paciente:", 
                font=("Segoe UI", 9, "bold"), bg="#f8f9fa", fg="#4a5568").pack(anchor=tk.W, pady=(0, 5))
        self.entry_consultar = tk.Entry(consulta_content, font=("Segoe UI", 10), bg="white", 
                                       relief=tk.FLAT, bd=5, validate='key', validatecommand=vcmd_letras)
        self.entry_consultar.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        btn_consultar = tk.Button(consulta_content, text="⏱ CONSULTAR TIEMPO ESPERA", 
                                 command=self.consultar_tiempo_espera,     # Función para buscar paciente
                                 bg="#4299E1", fg="white",
                                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, 
                                 cursor="hand2", height=1)
        btn_consultar.pack(fill=tk.X)
    
    def crear_seccion_lista(self):
        # Sección que muestra la tabla con todos los pacientes
        header_lista = tk.Frame(self.frame_lista, bg="#f8f9fa", height=60)
        header_lista.pack(fill=tk.X, padx=2, pady=2)
        header_lista.pack_propagate(False)
        
        icon_label = tk.Label(header_lista, text="📋", font=("Segoe UI", 16), bg="#f8f9fa")
        icon_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        title_label = tk.Label(header_lista, text="LISTA DE ESPERA", 
                              font=("Segoe UI", 12, "bold"), bg="#f8f9fa", fg="#2d3748")
        title_label.pack(side=tk.LEFT, pady=15)
        
        # Contenedor de la tabla
        table_frame = tk.Frame(self.frame_lista, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Tabla (Treeview) con columnas definidas
        columns = ("Pos", "Paciente", "Teléfono", "Hora", "Especialidad", "Tipo", "Tiempo Esp.")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        # Configuración del ancho de columnas
        column_config = {
            "Pos": 50,
            "Paciente": 120, 
            "Teléfono": 100,
            "Hora": 80,
            "Especialidad": 120,
            "Tipo": 80,
            "Tiempo Esp.": 90
        }
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=column_config[col], anchor=tk.CENTER, minwidth=50)
        
        # Scrollbars para cuando hay muchos pacientes
        scrollbar_v = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_v.set)
        
        scrollbar_h = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=scrollbar_h.set)
        
        # Posicionamiento con grid (mejor para layouts complejos)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def crear_seccion_control(self):
        # Panel de control con botones y estadísticas
        header_control = tk.Frame(self.frame_control, bg="#f8f9fa", height=60)
        header_control.pack(fill=tk.X, padx=2, pady=2)
        header_control.pack_propagate(False)
        
        icon_label = tk.Label(header_control, text="🎛", font=("Segoe UI", 16), bg="#f8f9fa")
        icon_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        title_label = tk.Label(header_control, text="PANEL DE CONTROL", 
                              font=("Segoe UI", 12, "bold"), bg="#f8f9fa", fg="#2d3748")
        title_label.pack(side=tk.LEFT, pady=15)
        
        control_content = tk.Frame(self.frame_control, bg="white")
        control_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Botones principales con funcionalidad
        btn_llamar = tk.Button(control_content, text="📢 LLAMAR SIGUIENTE PACIENTE", 
                              command=self.llamar_siguiente_paciente,      # ¡Función principal!
                              bg="#E53E3E", fg="white",
                              font=("Segoe UI", 12, "bold"), relief=tk.FLAT, cursor="hand2",
                              height=3)
        btn_llamar.pack(fill=tk.X, pady=(15, 15))
        
        btn_cancelar = tk.Button(control_content, text="❌ CANCELAR TURNO SELECCIONADO", 
                               command=self.cancelar_turno_seleccionado,
                               bg="#ED8936", fg="white",
                               font=("Segoe UI", 11, "bold"), relief=tk.FLAT, cursor="hand2",
                               height=2)
        btn_cancelar.pack(fill=tk.X, pady=(0, 15))
        
        btn_buscar = tk.Button(control_content, text="🔍 BUSCAR TURNOS PACIENTE", 
                              command=self.buscar_paciente_dialog,
                              bg="#805AD5", fg="white",
                              font=("Segoe UI", 11, "bold"), relief=tk.FLAT, cursor="hand2",
                              height=2)
        btn_buscar.pack(fill=tk.X, pady=(0, 30))
        
        # Sección de estadísticas - labels que actualizo dinámicamente
        stats_header = tk.Frame(control_content, bg="#edf2f7")
        stats_header.pack(fill=tk.X, pady=(20, 0))
        
        stats_icon = tk.Label(stats_header, text="📊", font=("Segoe UI", 14), bg="#edf2f7")
        stats_icon.pack(side=tk.LEFT, padx=10, pady=10)
        
        stats_title = tk.Label(stats_header, text="ESTADÍSTICAS DE LA COLA", 
                              font=("Segoe UI", 11, "bold"), bg="#edf2f7", fg="#2d3748")
        stats_title.pack(side=tk.LEFT, pady=10)
        
        self.stats_container = tk.Frame(control_content, bg="#edf2f7", relief=tk.FLAT, bd=1)
        self.stats_container.pack(fill=tk.X, pady=(0, 20))
        
        # Labels de estadísticas - los defino como atributos para poder actualizarlos
        self.label_total = tk.Label(self.stats_container, text="Total en cola: 0", 
                                   font=("Segoe UI", 10, "bold"), bg="#edf2f7", fg="#2d3748")
        self.label_total.pack(pady=8)
        
        self.label_emergencias = tk.Label(self.stats_container, text="🚨 Emergencias: 0", 
                                         font=("Segoe UI", 10, "bold"), bg="#edf2f7", fg="#E53E3E")
        self.label_emergencias.pack(pady=3)
        
        self.label_normales = tk.Label(self.stats_container, text="📋 Turnos normales: 0", 
                                      font=("Segoe UI", 10, "bold"), bg="#edf2f7", fg="#48BB78")
        self.label_normales.pack(pady=3)
        
        self.label_tiempo_prom = tk.Label(self.stats_container, text="⏱ Tiempo prom: 0 min", 
                                         font=("Segoe UI", 10, "bold"), bg="#edf2f7", fg="#ED8936")
        self.label_tiempo_prom.pack(pady=8)
        
        # Sección próximo paciente
        next_header = tk.Frame(control_content, bg="#e6fffa")
        next_header.pack(fill=tk.X, pady=(20, 0))
        
        next_icon = tk.Label(next_header, text="👆", font=("Segoe UI", 14), bg="#e6fffa")
        next_icon.pack(side=tk.LEFT, padx=10, pady=10)
        
        next_title = tk.Label(next_header, text="PRÓXIMO EN ATENCIÓN", 
                             font=("Segoe UI", 11, "bold"), bg="#e6fffa", fg="#2d3748")
        next_title.pack(side=tk.LEFT, pady=10)
        
        self.next_container = tk.Frame(control_content, bg="#e6fffa", relief=tk.FLAT, bd=1)
        self.next_container.pack(fill=tk.X)
        
        self.label_proximo = tk.Label(self.next_container, text="Cola vacía", 
                                     font=("Segoe UI", 10, "bold"), bg="#e6fffa", fg="#38B2AC")
        self.label_proximo.pack(pady=15)
    
    # ¡AQUÍ EMPIEZAN LAS FUNCIONES QUE REALMENTE HACEN QUE TODO FUNCIONE!
    # Esta es la parte que me costó más trabajo implementar
    
    def registrar_paciente(self):
        """Función que se ejecuta cuando presiono el botón 'REGISTRAR PACIENTE'"""
        # Obtengo todos los valores de los campos del formulario
        paciente = self.entry_paciente.get().strip()          # strip() quita espacios extra
        telefono = self.entry_telefono.get().strip()
        fecha = self.entry_fecha.get().strip()
        hora = self.entry_hora.get().strip()
        especialidad = self.combo_especialidad.get()
        es_emergencia = self.var_emergencia.get()             # Boolean del checkbox
        
        # Lista para acumular errores de validación - mejor experiencia de usuario
        errores = []
        
        # Validaciones detalladas - la profesora nos dijo que siempre validemos entrada de usuario
        if not paciente:
            errores.append("• El nombre del paciente es obligatorio")
        elif not self.validar_nombre_completo(paciente):
            errores.append("• El nombre debe contener solo letras y espacios")
        
        if not telefono:
            errores.append("• El teléfono es obligatorio")
        elif not self.validar_telefono_completo(telefono):
            errores.append("• El teléfono debe contener solo números enteros positivos")
        
        if not especialidad:
            errores.append("• Debe seleccionar una especialidad")
        
        # Si hay errores, mostrar mensaje detallado y no continuar
        if errores:
            mensaje_error = "❌ NO SE HA PODIDO REALIZAR EL REGISTRO\n\nMotivo(s):\n" + "\n".join(errores)
            messagebox.showerror("Error en el Registro", mensaje_error)
            return      # Salir de la función sin registrar
        
        # Si llegó hasta aquí, todas las validaciones pasaron
        # Uso mi lista enlazada para agregar el nuevo turno
        self.lista_turnos.agregar_turno(paciente, telefono, fecha, hora, especialidad, es_emergencia)
        
        # Mostrar confirmación al usuario
        tipo = "EMERGENCIA" if es_emergencia else "NORMAL"
        messagebox.showinfo("Turno Registrado", 
                          f"Paciente: {paciente}\nTipo: {tipo}\nEspecialidad: {especialidad}\n\n✅ Turno registrado exitosamente")
        
        # Limpiar campos y actualizar interfaz
        self.limpiar_campos()
        self.actualizar_interfaz()      # Actualizar tabla y estadísticas
    
    def llamar_siguiente_paciente(self):
        """Función principal - llama al siguiente paciente y lo elimina de la cola"""
        # Uso el método de mi lista enlazada para obtener el próximo paciente
        paciente = self.lista_turnos.llamar_siguiente()
        
        if paciente:
            # Si hay paciente, mostrar información y actualizar interfaz
            tipo = "EMERGENCIA" if paciente.es_emergencia else "NORMAL"
            messagebox.showinfo("Llamando Paciente", 
                              f"📢 LLAMANDO A:\n\nPaciente: {paciente.paciente}\nTipo: {tipo}\nEspecialidad: {paciente.especialidad}\nTeléfono: {paciente.telefono}")
            self.actualizar_interfaz()
        else:
            # Cola vacía
            messagebox.showwarning("Cola Vacía", "No hay pacientes en la cola de espera")
    
    def cancelar_turno_seleccionado(self):
        """Cancelar el turno que está seleccionado en la tabla"""
        # Verifico si hay algo seleccionado en la tabla
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Debe seleccionar un turno para cancelar")
            return
        
        # Obtengo los datos del item seleccionado
        item_values = self.tree.item(selected_item[0])['values']
        nombre_paciente = item_values[1]  # La columna 1 es "Paciente"
        
        # Pido confirmación antes de cancelar - es una buena práctica
        respuesta = messagebox.askyesno("Confirmar Cancelación", 
                                      f"¿Está seguro de cancelar el turno de {nombre_paciente}?")
        
        if respuesta:
            # Uso mi lista enlazada para cancelar el turno
            if self.lista_turnos.cancelar_turno(nombre_paciente):
                messagebox.showinfo("Turno Cancelado", f"Turno de {nombre_paciente} cancelado exitosamente")
                self.actualizar_interfaz()
            else:
                messagebox.showerror("Error", "No se pudo cancelar el turno")
    
    def buscar_paciente_dialog(self):
        """Ventana de diálogo para buscar un paciente específico"""
        # simpledialog crea una pequeña ventana para pedir input
        nombre = tk.simpledialog.askstring("Buscar Paciente", "Ingrese el nombre del paciente:")
        
        if nombre:
            # Busco en mi lista enlazada
            paciente, posicion = self.lista_turnos.buscar_paciente(nombre)
            
            if paciente:
                # Calculo estadísticas del paciente encontrado
                tiempo_espera = datetime.now() - paciente.hora_registro
                minutos_espera = int(tiempo_espera.total_seconds() / 60)
                tiempo_estimado = (posicion - 1) * self.tiempo_por_consulta
                
                tipo = "EMERGENCIA" if paciente.es_emergencia else "NORMAL"
                
                messagebox.showinfo("Paciente Encontrado", 
                                  f"Paciente: {paciente.paciente}\nPosición: {posicion}\nTipo: {tipo}\nEspecialidad: {paciente.especialidad}\nTiempo esperando: {minutos_espera} min\nTiempo estimado restante: {tiempo_estimado} min")
            else:
                messagebox.showwarning("No Encontrado", f"No se encontró al paciente {nombre}")
    
    def consultar_tiempo_espera(self):
        """Consultar tiempo de espera desde el formulario de la izquierda"""
        nombre = self.entry_consultar.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "Ingrese el nombre del paciente")
            return
        
        # Misma lógica que buscar_paciente_dialog pero usando el campo del formulario
        paciente, posicion = self.lista_turnos.buscar_paciente(nombre)
        
        if paciente:
            tiempo_espera = datetime.now() - paciente.hora_registro
            minutos_espera = int(tiempo_espera.total_seconds() / 60)
            tiempo_estimado = (posicion - 1) * self.tiempo_por_consulta
            
            messagebox.showinfo("Tiempo de Espera", 
                              f"Paciente: {paciente.paciente}\nPosición en cola: {posicion}\nTiempo esperando: {minutos_espera} min\nTiempo estimado restante: {tiempo_estimado} min")
            
            self.entry_consultar.delete(0, tk.END)      # Limpiar campo después de consultar
        else:
            messagebox.showwarning("No Encontrado", f"No se encontró al paciente {nombre}")
    
    def limpiar_campos(self):
        """Limpiar todos los campos del formulario de registro"""
        self.entry_paciente.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        # Para fecha y hora, los vuelvo a pre-llenar con valores actuales
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, datetime.now().strftime("%H:%M"))
        self.combo_especialidad.set("")                # Limpiar combobox
        self.var_emergencia.set(False)                 # Desmarcar checkbox
    
    def actualizar_interfaz(self):
        """Función súper importante - actualiza toda la interfaz con los datos actuales"""
        # Esta función se llama después de cada operación para refrescar la vista
        
        # 1. Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 2. Llenar tabla con datos actuales de mi lista enlazada
        turnos = self.lista_turnos.obtener_lista_completa()
        for turno in turnos:
            # Configurar colores según tipo de turno para mejor visualización
            tags = ("emergencia",) if turno['tipo'] == "EMERGENCIA" else ("normal",)
            
            self.tree.insert("", "end", values=(
                turno['posicion'],
                turno['paciente'],
                turno['telefono'],
                turno['hora'],
                turno['especialidad'],
                turno['tipo'],
                turno['tiempo_espera']
            ), tags=tags)
        
        # 3. Configurar colores de las filas
        self.tree.tag_configure("emergencia", background="#ffebee", foreground="#d32f2f")
        self.tree.tag_configure("normal", background="#f9f9f9", foreground="#333333")
        
        # 4. Actualizar estadísticas usando mi lista enlazada
        stats = self.lista_turnos.obtener_estadisticas()
        self.label_total.config(text=f"Total en cola: {stats['total']}")
        self.label_emergencias.config(text=f"🚨 Emergencias: {stats['emergencias']}")
        self.label_normales.config(text=f"📋 Turnos normales: {stats['normales']}")
        self.label_tiempo_prom.config(text=f"⏱ Tiempo prom: {stats['tiempo_promedio']} min")
        
        # 5. Actualizar información del próximo paciente
        if self.lista_turnos.cabeza:
            # Si hay pacientes en cola, mostrar el primero
            tipo = "🚨 EMERGENCIA" if self.lista_turnos.cabeza.es_emergencia else "📋 NORMAL"
            texto_proximo = f"{self.lista_turnos.cabeza.paciente}\n{tipo}\n{self.lista_turnos.cabeza.especialidad}"
            self.label_proximo.config(text=texto_proximo, fg="#2d3748")
        else:
            # Cola vacía
            self.label_proximo.config(text="Cola vacía", fg="#38B2AC")

# Punto de entrada del programa
if __name__ == "__main__":
    # Importo simpledialog aquí para evitar problemas de importación circular
    from tkinter import simpledialog
    
    # Creo la ventana principal y la aplicación
    root = tk.Tk()
    app = GestorTurnosApp(root)
    
    # Inicio el loop principal que mantiene la aplicación corriendo
    root.mainloop()

# conclucion final:
# Este ha sido mi proyecto más complejo hasta ahora. Aprendí mucho sobre:
# 1. Estructuras de datos (listas enlazadas) - más eficientes que listas normales para este caso
# 2. Programación orientada a objetos - organizar código en clases
# 3. Interfaces gráficas con tkinter - crear aplicaciones visuales
# 4. Validación de datos - nunca confiar en lo que ingresa el usuario
# 5. Manejo de eventos - conectar botones con funciones
# 6. Gestión de estado - mantener la interfaz actualizada
#
# Lo que más me costó fue entender los punteros en las listas enlazadas
# y cómo manejar la inserción de emergencias en el orden correcto.
# - Guardar datos en archivo para persistencia
# - Agregar base de datos
# - Mejorar validación de fechas y horas
# - Agregar sonidos o notificaciones
# - Historial de pacientes atendidos