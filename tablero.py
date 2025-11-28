import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import chess
import chess.engine
import pygame

#Música del Juego
pygame.init()
pygame.mixer.init()

#Efecto de sonido
sonido_colocar_pieza = pygame.mixer.Sound('Musica/Sonido de colocar pieza.wav')
try:
    ruta_musica = 'Musica/Alma Llanera Instrumental.ogg'
    pygame.mixer.music.load(ruta_musica)

    #Música de fondo loop -1
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.1)
except pygame.error as e:
    print('No se pudo cargar la música')

class InterfazBienvenida:
    def __init__(self, root, callback_iniciar):
        self.root = root
        self.callback_iniciar = callback_iniciar
        self.crear_interfaz()
        root.iconbitmap('icono/white_pawn.ico')
    
    def crear_interfaz(self):
        # Frame principal de bienvenida
        self.frame_bienvenida = tk.Frame(self.root, bg='#1E3A5F')
        self.frame_bienvenida.pack(expand=True, fill='both')
        
        # Título UNEFADREZ con estilo llamativo
        titulo_frame = tk.Frame(self.frame_bienvenida, bg='#1E3A5F')
        titulo_frame.pack(expand=True, pady=50)
        
        lbl_titulo = tk.Label(
            titulo_frame,
            text="UNEFADREZ",
            font=("Arial", 48, "bold"),
            fg="#FFD700",
            bg='#1E3A5F'
        )
        lbl_titulo.pack(pady=20)
        
        lbl_subtitulo = tk.Label(
            titulo_frame,
            text="El Ajedrez de la UNEFA",
            font=("Arial", 20, "italic"),
            fg="white",
            bg='#1E3A5F'
        )
        lbl_subtitulo.pack(pady=10)
        
        # Frame para información adicional
        info_frame = tk.Frame(self.frame_bienvenida, bg='#1E3A5F')
        info_frame.pack(expand=True, pady=30)
        
        # Mensaje de bienvenida
        lbl_bienvenida = tk.Label(
            info_frame,
            text="¡Bienvenido al juego de ajedrez oficial de la UNEFA!",
            font=("Arial", 16),
            fg="white",
            bg='#1E3A5F',
            pady=20
        )
        lbl_bienvenida.pack()
        
        # Características del juego
        caracteristicas = [
            "✓ Tablero interactivo con piezas personalizadas",
            "✓ Reglas oficiales del ajedrez",
            "✓ Sistema de puntuación por capturas",
            "✓ Indicador de jaque al rey",
            "✓ Sistema de promoción de peones",
            "✓ Detección automática de jaque mate",
            "✓ Interfaz intuitiva y fácil de usar"
        ]
        
        for caracteristica in caracteristicas:
            lbl_caract = tk.Label(
                info_frame,
                text=caracteristica,
                font=("Arial", 12),
                fg="#90EE90",
                bg='#1E3A5F',
                pady=5
            )
            lbl_caract.pack()
        
        # Frame para botones
        botones_frame = tk.Frame(self.frame_bienvenida, bg='#1E3A5F')
        botones_frame.pack(expand=True, pady=40)
        
        # Botón para iniciar juego
        btn_iniciar = tk.Button(
            botones_frame,
            text="Iniciar Partida",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self.iniciar_juego
        )
        btn_iniciar.pack(pady=10)
        
        # Botón para salir
        btn_salir = tk.Button(
            botones_frame,
            text="Salir del Juego",
            font=("Arial", 14),
            bg="#f44336",
            fg="white",
            width=15,
            command=self.root.quit
        )
        btn_salir.pack(pady=5)
        
        # Créditos
        lbl_creditos = tk.Label(
            self.frame_bienvenida,
            text="Desarrollado para la UNEFA - 2025",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg='#1E3A5F',
            pady=20
        )
        lbl_creditos.pack(side='bottom')
    
    def iniciar_juego(self):
        # Ocultar interfaz de bienvenida y mostrar el juego
        self.frame_bienvenida.pack_forget()
        self.callback_iniciar()

class SistemaPuntos:
    def __init__(self):
        # Sistema de puntuación estándar del ajedrez
        self.valor_piezas = {
            chess.PAWN: 1,      # Peón: 1 punto
            chess.KNIGHT: 3,    # Caballo: 3 puntos
            chess.BISHOP: 3,    # Alfil: 3 puntos
            chess.ROOK: 5,      # Torre: 5 puntos
            chess.QUEEN: 9,     # Reina: 9 puntos
            chess.KING: 0       # Rey: 0 puntos (no se captura)
        }
        
        # Puntos por movimientos especiales
        self.puntos_especiales = {
            'jaque': 1,         # 1 punto por dar jaque
            'jaque_mate': 10,   # 10 puntos por jaque mate
            'captura_al_paso': 2, # 2 puntos por captura al paso
            'enroque': 2,       # 2 puntos por enroque
            'promocion': 5      # 5 puntos por promoción
        }
        
        # Inicializar puntuaciones
        self.reiniciar_puntos()
    
    def reiniciar_puntos(self):
        """Reinicia todas las puntuaciones a cero"""
        self.puntos_blancas = 0
        self.puntos_negras = 0
        self.capturas_blancas = []  # Lista de piezas capturadas por blancas
        self.capturas_negras = []   # Lista de piezas capturadas por negras
        self.historial_movimientos = []  # Historial de movimientos con puntos
    
    def obtener_valor_pieza(self, pieza):
        """Obtiene el valor en puntos de una pieza"""
        return self.valor_piezas.get(pieza.piece_type, 0)
    
    def registrar_captura(self, pieza_capturada, capturador_blanco):
        """Registra una captura y actualiza los puntos"""
        valor = self.obtener_valor_pieza(pieza_capturada)
        
        if capturador_blanco:
            self.puntos_blancas += valor
            self.capturas_blancas.append(pieza_capturada)
        else:
            self.puntos_negras += valor
            self.capturas_negras.append(pieza_capturada)
        
        return valor
    
    def registrar_movimiento_especial(self, tipo_movimiento, es_blanco):
        """Registra movimientos especiales y asigna puntos"""
        puntos = self.puntos_especiales.get(tipo_movimiento, 0)
        
        if es_blanco:
            self.puntos_blancas += puntos
        else:
            self.puntos_negras += puntos
        
        return puntos
    
    def obtener_resumen_capturas(self, es_blanco):
        """Obtiene un resumen de las piezas capturadas"""
        capturas = self.capturas_blancas if es_blanco else self.capturas_negras
        resumen = {}
        for pieza in capturas:
            tipo = pieza.symbol().upper() if es_blanco else pieza.symbol().lower()
            resumen[tipo] = resumen.get(tipo, 0) + 1
        return resumen
    
    def obtener_ventaja(self):
        """Calcula la ventaja de puntos entre blancas y negras"""
        return self.puntos_blancas - self.puntos_negras

class AjedrezCompleto:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UNEFADREZ - Ajedrez Completo con Sistema de Puntos")
        self.root.geometry("900x800")
        self.root.configure(bg='#2C2C2C')
        
        # Estado para controlar si el juego está activo
        self.juego_activo = False
        
        # Sistema de puntos
        self.sistema_puntos = SistemaPuntos()
        
        # Mostrar interfaz de bienvenida primero
        self.bienvenida = InterfazBienvenida(self.root, self.iniciar_juego_real)
        
        # Inicializar variables del juego (se crearán cuando inicie el juego real)
        self.tablero = None
        self.casillas = None
        self.imagenes = {}
        self.pieza_seleccionada = None
        self.casilla_seleccionada = None
        self.movimientos_validos = []
        self.juego_terminado = False
        
        # Mapeo de piezas de chess a símbolos Unicode
        self.mapeo_piezas = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        
        # Mapeo de tipos de pieza a nombres
        self.nombres_piezas = {
            chess.PAWN: "Peón",
            chess.KNIGHT: "Caballo",
            chess.BISHOP: "Alfil",
            chess.ROOK: "Torre",
            chess.QUEEN: "Reina",
            chess.KING: "Rey"
        }
        
        # Colores para el jaque
        self.color_jaque = "#FF6B6B"  # Rojo claro para indicar jaque
    
    def iniciar_juego_real(self):
        """Inicializa el juego real después de la bienvenida"""
        self.juego_activo = True
        
        # Estado del juego usando python-chess
        self.tablero = chess.Board()
        
        # Reiniciar sistema de puntos
        self.sistema_puntos.reiniciar_puntos()
        
        # Cargar imágenes
        self.cargar_imagenes()
        
        # Crear interfaz del juego
        self.crear_interfaz_juego()
    
    def cargar_imagenes(self):
        """Carga las imágenes de las piezas desde archivos locales"""
        tamaño = (60, 60)  # Tamaño de las imágenes
        
        # Mapeo de piezas a nombres de archivo
        mapeo_imagenes = {
            '♜': 'black_rook.png',
            '♞': 'black_knight.png',
            '♝': 'black_bishop.png',
            '♛': 'black_queen.png',
            '♚': 'black_king.png',
            '♟': 'black_pawn.png',
            '♖': 'white_rook.png',
            '♘': 'white_knight.png',
            '♗': 'white_bishop.png',
            '♕': 'white_queen.png',
            '♔': 'white_king.png',
            '♙': 'white_pawn.png'
        }
        
        # Crear una imagen vacía para casillas vacías
        imagen_vacia = Image.new('RGBA', tamaño, (0, 0, 0, 0))
        self.imagenes[''] = ImageTk.PhotoImage(imagen_vacia)
        
        for pieza, archivo in mapeo_imagenes.items():
            try:
                if os.path.exists(archivo):
                    # Cargar y redimensionar la imagen
                    imagen = Image.open(archivo)
                    imagen = imagen.resize(tamaño, Image.Resampling.LANCZOS)
                    self.imagenes[pieza] = ImageTk.PhotoImage(imagen)
                    print(f"✓ Imagen cargada: {archivo}")
                else:
                    # Si no existe el archivo, crear una imagen con el símbolo
                    print(f"✗ Archivo no encontrado: {archivo} - Creando imagen con texto")
                    # Crear una imagen con el símbolo de la pieza
                    imagen = Image.new('RGBA', tamaño, (0, 0, 0, 0))
                    self.imagenes[pieza] = ImageTk.PhotoImage(imagen)
            except Exception as e:
                print(f"✗ Error cargando {archivo}: {e} - Creando imagen vacía")
                imagen = Image.new('RGBA', tamaño, (0, 0, 0, 0))
                self.imagenes[pieza] = ImageTk.PhotoImage(imagen)
    
    def obtener_pieza_unicode(self, square):
        """Obtiene el símbolo Unicode para una pieza en una casilla"""
        pieza = self.tablero.piece_at(square)
        if pieza:
            return self.mapeo_piezas[pieza.symbol()]
        return ''
    
    def encontrar_rey(self, color):
        """Encuentra la posición del rey del color especificado"""
        for square in chess.SQUARES:
            pieza = self.tablero.piece_at(square)
            if pieza and pieza.piece_type == chess.KING and pieza.color == color:
                return square
        return None
    
    def resaltar_jaque(self):
        """Resalta la casilla del rey si está en jaque"""
        # Primero, limpiar cualquier resaltado anterior de jaque
        for fila in range(8):
            for columna in range(8):
                square = chess.square(columna, 7 - fila)
                color_original = self.color_claro if (fila + columna) % 2 == 0 else self.color_oscuro
                self.casillas[fila][columna].configure(bg=color_original)
        
        # Verificar si el rey actual (el que tiene el turno) está en jaque
        if self.tablero.is_check():
            color_rey = self.tablero.turn
            posicion_rey = self.encontrar_rey(color_rey)
            
            if posicion_rey:
                fila, columna = self.casilla_a_coordenadas(posicion_rey)
                # Resaltar la casilla del rey en color de jaque
                self.casillas[fila][columna].configure(bg=self.color_jaque)
                
                # Mostrar mensaje en la interfaz
                color_texto = "Blanco" if color_rey == chess.WHITE else "Negro"
                self.lbl_estado.configure(text=f"¡Jaque al rey {color_texto}!", fg="#FF4444")
    
    def crear_interfaz_juego(self):
        # Frame principal del juego
        main_frame = tk.Frame(self.root, bg='#2C2C2C')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header con logo UNEFADREZ
        header_frame = tk.Frame(main_frame, bg='#1E3A5F')
        header_frame.pack(fill='x', pady=(0, 20))
        
        lbl_titulo_juego = tk.Label(
            header_frame,
            text="UNEFADREZ",
            font=("Arial", 24, "bold"),
            fg="#FFD700",
            bg='#1E3A5F',
            pady=10
        )
        lbl_titulo_juego.pack()
        
        # Frame para tablero y panel de puntos
        contenido_frame = tk.Frame(main_frame, bg='#2C2C2C')
        contenido_frame.pack(expand=True, fill='both')
        
        # Frame del tablero (izquierda)
        board_frame = tk.Frame(contenido_frame, bg='#2C2C2C')
        board_frame.pack(side='left', expand=True)
        
        # Panel de puntos (derecha)
        self.crear_panel_puntos(contenido_frame)
        
        # Colores del tablero
        self.color_claro = "#F0D9B5"
        self.color_oscuro = "#B58863"
        self.color_seleccionado = "#90EE90"
        self.color_movimiento_valido = "#FFD700"
        
        # Crear tablero
        self.casillas = [[None for _ in range(8)] for _ in range(8)]
        
        for fila in range(8):
            for columna in range(8):
                # Convertir coordenadas a notación chess (0,0) -> a8, (7,7) -> h1
                square = chess.square(columna, 7 - fila)
                pieza_unicode = self.obtener_pieza_unicode(square)
                color = self.color_claro if (fila + columna) % 2 == 0 else self.color_oscuro
                
                btn = tk.Button(
                    board_frame,
                    text="",
                    image=self.imagenes[pieza_unicode],
                    font=("Arial", 20),
                    bg=color,
                    width=60,
                    height=60,
                    relief="solid",
                    borderwidth=2,
                    compound="center",
                    command=lambda f=fila, c=columna: self.manejar_click(f, c)
                )
                btn.grid(row=fila, column=columna, sticky="nsew")
                self.casillas[fila][columna] = btn
                btn.image = self.imagenes[pieza_unicode]
        
        # Resaltar jaque inicial (si aplica)
        self.resaltar_jaque()
        
        # Frame de controles
        control_frame = tk.Frame(main_frame, bg='#2C2C2C')
        control_frame.pack(fill='x', pady=10)
        
        # Etiqueta de turno
        self.lbl_turno = tk.Label(
            control_frame,
            text=f"Turno: {'Blanco' if self.tablero.turn else 'Negro'}",
            font=("Arial", 14, "bold"),
            bg='#2C2C2C',
            fg='white'
        )
        self.lbl_turno.pack(side='left')
        
        # Etiqueta de estado del juego
        self.lbl_estado = tk.Label(
            control_frame,
            text=self.obtener_estado_juego(),
            font=("Arial", 12),
            bg='#2C2C2C',
            fg='yellow'
        )
        self.lbl_estado.pack(side='left', padx=20)
        
        # Frame para botones de control
        botones_control_frame = tk.Frame(control_frame, bg='#2C2C2C')
        botones_control_frame.pack(side='right')
        
        # Botón reiniciar
        btn_reiniciar = tk.Button(
            botones_control_frame,
            text="Reiniciar Juego",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            command=self.reiniciar_juego
        )
        btn_reiniciar.pack(side='left', padx=5)
        
        # Botón volver al menú
        btn_menu = tk.Button(
            botones_control_frame,
            text="Menú Principal",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.volver_al_menu
        )
        btn_menu.pack(side='left', padx=5)
        
        # Configurar grid responsive
        for i in range(8):
            board_frame.grid_rowconfigure(i, weight=1)
            board_frame.grid_columnconfigure(i, weight=1)
    
    def crear_panel_puntos(self, parent):
        """Crea el panel lateral con el sistema de puntos"""
        panel_frame = tk.Frame(parent, bg='#3A3A3A', width=250, relief='raised', borderwidth=2)
        panel_frame.pack(side='right', fill='y', padx=(20, 0))
        panel_frame.pack_propagate(False)
        
        # Título del panel
        lbl_titulo_panel = tk.Label(
            panel_frame,
            text="SISTEMA DE PUNTOS",
            font=("Arial", 16, "bold"),
            fg="#FFD700",
            bg='#3A3A3A',
            pady=15
        )
        lbl_titulo_panel.pack()
        
        # Frame para puntuación de blancas
        frame_blancas = tk.Frame(panel_frame, bg='#4A4A4A', relief='sunken', borderwidth=1)
        frame_blancas.pack(fill='x', padx=10, pady=5)
        
        lbl_blancas = tk.Label(
            frame_blancas,
            text="BLANCAS",
            font=("Arial", 14, "bold"),
            fg="white",
            bg='#4A4A4A'
        )
        lbl_blancas.pack(pady=5)
        
        self.lbl_puntos_blancas = tk.Label(
            frame_blancas,
            text="Puntos: 0",
            font=("Arial", 12, "bold"),
            fg="#90EE90",
            bg='#4A4A4A'
        )
        self.lbl_puntos_blancas.pack(pady=2)
        
        self.lbl_capturas_blancas = tk.Label(
            frame_blancas,
            text="Capturas: Ninguna",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg='#4A4A4A',
            wraplength=200
        )
        self.lbl_capturas_blancas.pack(pady=5)
        
        # Frame para puntuación de negras
        frame_negras = tk.Frame(panel_frame, bg='#4A4A4A', relief='sunken', borderwidth=1)
        frame_negras.pack(fill='x', padx=10, pady=5)
        
        lbl_negras = tk.Label(
            frame_negras,
            text="NEGRAS",
            font=("Arial", 14, "bold"),
            fg="white",
            bg='#4A4A4A'
        )
        lbl_negras.pack(pady=5)
        
        self.lbl_puntos_negras = tk.Label(
            frame_negras,
            text="Puntos: 0",
            font=("Arial", 12, "bold"),
            fg="#90EE90",
            bg='#4A4A4A'
        )
        self.lbl_puntos_negras.pack(pady=2)
        
        self.lbl_capturas_negras = tk.Label(
            frame_negras,
            text="Capturas: Ninguna",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg='#4A4A4A',
            wraplength=200
        )
        self.lbl_capturas_negras.pack(pady=5)
        
        # Ventaja actual
        frame_ventaja = tk.Frame(panel_frame, bg='#5A5A5A', relief='ridge', borderwidth=2)
        frame_ventaja.pack(fill='x', padx=10, pady=10)
        
        self.lbl_ventaja = tk.Label(
            frame_ventaja,
            text="Ventaja: Empate",
            font=("Arial", 12, "bold"),
            fg="#FFD700",
            bg='#5A5A5A',
            pady=8
        )
        self.lbl_ventaja.pack()
        
        # Información de valores
        frame_valores = tk.Frame(panel_frame, bg='#3A3A3A')
        frame_valores.pack(fill='x', padx=10, pady=10)
        
        lbl_valores = tk.Label(
            frame_valores,
            text="Valor de Piezas:\nPeón: 1 | Caballo/Alfil: 3\nTorre: 5 | Reina: 9\n\n¡Jaque resaltado en rojo!",
            font=("Arial", 9),
            fg="#AAAAAA",
            bg='#3A3A3A',
            justify='left'
        )
        lbl_valores.pack()
    
    def actualizar_panel_puntos(self):
        """Actualiza el panel de puntos con la información actual"""
        # Actualizar puntos
        self.lbl_puntos_blancas.config(text=f"Puntos: {self.sistema_puntos.puntos_blancas}")
        self.lbl_puntos_negras.config(text=f"Puntos: {self.sistema_puntos.puntos_negras}")
        
        # Actualizar capturas
        capturas_b = self.sistema_puntos.obtener_resumen_capturas(True)
        capturas_n = self.sistema_puntos.obtener_resumen_capturas(False)
        
        texto_capturas_b = "Capturas: " + (", ".join([f"{cant}x{pieza}" for pieza, cant in capturas_b.items()]) if capturas_b else "Ninguna")
        texto_capturas_n = "Capturas: " + (", ".join([f"{cant}x{pieza}" for pieza, cant in capturas_n.items()]) if capturas_n else "Ninguna")
        
        self.lbl_capturas_blancas.config(text=texto_capturas_b)
        self.lbl_capturas_negras.config(text=texto_capturas_n)
        
        # Actualizar ventaja
        ventaja = self.sistema_puntos.obtener_ventaja()
        if ventaja > 0:
            texto_ventaja = f"Ventaja: Blancas (+{ventaja})"
            color_ventaja = "#90EE90"
        elif ventaja < 0:
            texto_ventaja = f"Ventaja: Negras (+{abs(ventaja)})"
            color_ventaja = "#90EE90"
        else:
            texto_ventaja = "Ventaja: Empate"
            color_ventaja = "#FFD700"
        
        self.lbl_ventaja.config(text=texto_ventaja, fg=color_ventaja)
    
    def volver_al_menu(self):
        """Vuelve a la pantalla de bienvenida"""
        # Limpiar la interfaz actual del juego
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Restablecer estado del juego
        self.juego_activo = False
        self.tablero = None
        self.casillas = None
        self.pieza_seleccionada = None
        self.casilla_seleccionada = None
        self.movimientos_validos = []
        self.juego_terminado = False
        
        # Mostrar interfaz de bienvenida nuevamente
        self.bienvenida = InterfazBienvenida(self.root, self.iniciar_juego_real)
    
    def obtener_estado_juego(self):
        """Obtiene el estado actual del juego"""
        if self.tablero.is_checkmate():
            return "¡Jaque Mate!"
        elif self.tablero.is_stalemate():
            return "Ahogado"
        elif self.tablero.is_insufficient_material():
            return "Material insuficiente"
        elif self.tablero.is_check():
            # El mensaje de jaque se maneja en resaltar_jaque()
            return "Jaque"
        else:
            return "Juego en curso"
    
    def coordenadas_a_casilla(self, fila, columna):
        """Convierte coordenadas de interfaz a notación chess"""
        return chess.square(columna, 7 - fila)
    
    def casilla_a_coordenadas(self, square):
        """Convierte notación chess a coordenadas de interfaz"""
        archivo = chess.square_file(square)
        rango = chess.square_rank(square)
        return (7 - rango, archivo)
    
    def obtener_movimientos_validos(self, square):
        """Obtiene todos los movimientos válidos para una pieza en la posición dada"""
        movimientos = []
        for movimiento in self.tablero.legal_moves:
            if movimiento.from_square == square:
                movimientos.append(movimiento.to_square)
        return movimientos
    
    def mostrar_mensaje_puntos(self, puntos, mensaje, es_blanco):
        """Muestra un mensaje temporal sobre puntos ganados"""
        color = "white" if es_blanco else "black"
        bg_color = "#E8F5E8" if es_blanco else "#F5E8E8"
        
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.configure(bg=bg_color, relief='solid', borderwidth=1)
        
        label = tk.Label(
            popup,
            text=f"+{puntos} pts: {mensaje}",
            font=("Arial", 10, "bold"),
            fg="green" if puntos > 0 else "red",
            bg=bg_color
        )
        label.pack(padx=10, pady=5)
        
        # Posicionar cerca de la pieza movida
        popup.update_idletasks()
        x = self.root.winfo_x() + 400
        y = self.root.winfo_y() + 200
        popup.geometry(f"+{x}+{y}")
        
        # Auto-destruir después de 2 segundos
        popup.after(2000, popup.destroy)
    
    def manejar_promocion(self, movimiento):
        """Maneja la promoción de peón usando la librería chess"""
        if self.tablero.piece_at(movimiento.from_square).piece_type == chess.PAWN:
            fila_final = chess.square_rank(movimiento.to_square)
            if fila_final == 0 or fila_final == 7:
                opciones = ["Reina", "Torre", "Alfil", "Caballo"]
                piezas = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                
                dialogo = tk.Toplevel(self.root)
                dialogo.title("UNEFADREZ - Promoción de Peón")
                dialogo.geometry("350x200")
                dialogo.configure(bg='#2C2C2C')
                dialogo.transient(self.root)
                dialogo.grab_set()
                
                # Centrar diálogo
                dialogo.update_idletasks()
                x = self.root.winfo_x() + (self.root.winfo_width() - dialogo.winfo_width()) // 2
                y = self.root.winfo_y() + (self.root.winfo_height() - dialogo.winfo_height()) // 2
                dialogo.geometry(f"+{x}+{y}")
                
                # Etiqueta
                lbl = tk.Label(
                    dialogo, 
                    text="Elige una pieza para promocionar:", 
                    font=("Arial", 12),
                    bg='#2C2C2C',
                    fg='white'
                )
                lbl.pack(pady=15)
                
                # Frame para botones
                frame_botones = tk.Frame(dialogo, bg='#2C2C2C')
                frame_botones.pack(pady=10)
                
                def seleccionar_promocion(indice):
                    movimiento.promotion = piezas[indice]
                    pieza_promocion = self.nombres_piezas[piezas[indice]]
                    
                    # Registrar puntos por promoción
                    es_blanco = self.tablero.turn
                    puntos = self.sistema_puntos.registrar_movimiento_especial('promocion', es_blanco)
                    self.mostrar_mensaje_puntos(puntos, f"Promoción a {pieza_promocion}", es_blanco)
                    
                    self.tablero.push(movimiento)
                    self.colocar_pieza = sonido_colocar_pieza.play()
                    self.actualizar_tablero()
                    self.actualizar_panel_puntos()
                    dialogo.destroy()
                    self.verificar_fin_del_juego()
                
                # Crear botones para cada opción
                for i, opcion in enumerate(opciones):
                    btn = tk.Button(
                        frame_botones,
                        text=opcion,
                        font=("Arial", 10),
                        bg="#4CAF50",
                        fg="white",
                        command=lambda idx=i: seleccionar_promocion(idx)
                    )
                    btn.pack(side='left', padx=5)
                
                return True
        return False
    
    def limpiar_marcadores(self):
        """Limpia todos los marcadores de movimientos válidos"""
        for fila in range(8):
            for columna in range(8):
                square = chess.square(columna, 7 - fila)
                color_original = self.color_claro if (fila + columna) % 2 == 0 else self.color_oscuro
                self.casillas[fila][columna].configure(bg=color_original)
        
        # Después de limpiar, resaltar el jaque si existe
        self.resaltar_jaque()
    
    def verificar_fin_del_juego(self):
        """Verifica si el juego ha terminado usando chess"""
        if self.tablero.is_game_over():
            self.juego_terminado = True
            
            # Asignar puntos por jaque mate
            if self.tablero.is_checkmate():
                ganador_es_blanco = not self.tablero.turn  # El ganador es el que NO tiene el turno
                puntos = self.sistema_puntos.registrar_movimiento_especial('jaque_mate', ganador_es_blanco)
                self.actualizar_panel_puntos()
            
            self.mostrar_fin_del_juego()
            return True
        return False
    
    def mostrar_fin_del_juego(self):
        """Muestra el mensaje de fin del juego con opción de reiniciar"""
        resultado = self.obtener_estado_juego()
        ganador = "Negro" if self.tablero.turn else "Blanco"
        
        if self.tablero.is_checkmate():
            mensaje = f"¡Jaque Mate!\n\n¡{ganador} gana la partida!\n\nPuntos Finales:\nBlancas: {self.sistema_puntos.puntos_blancas}\nNegras: {self.sistema_puntos.puntos_negras}"
        elif self.tablero.is_stalemate():
            mensaje = f"¡Tablas por ahogado!\n\nPuntos Finales:\nBlancas: {self.sistema_puntos.puntos_blancas}\nNegras: {self.sistema_puntos.puntos_negras}"
        elif self.tablero.is_insufficient_material():
            mensaje = f"¡Tablas por material insuficiente!\n\nPuntos Finales:\nBlancas: {self.sistema_puntos.puntos_blancas}\nNegras: {self.sistema_puntos.puntos_negras}"
        else:
            mensaje = f"¡Juego terminado!\n\nPuntos Finales:\nBlancas: {self.sistema_puntos.puntos_blancas}\nNegras: {self.sistema_puntos.puntos_negras}"
        
        dialogo_fin = tk.Toplevel(self.root)
        dialogo_fin.title("UNEFADREZ - Fin del Juego")
        dialogo_fin.geometry("500x300")
        dialogo_fin.configure(bg='#1E3A5F')
        dialogo_fin.transient(self.root)
        dialogo_fin.grab_set()
        
        # Centrar diálogo
        dialogo_fin.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialogo_fin.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialogo_fin.winfo_height()) // 2
        dialogo_fin.geometry(f"+{x}+{y}")
        
        # Mensaje de fin del juego
        lbl_mensaje = tk.Label(
            dialogo_fin, 
            text=mensaje, 
            font=("Arial", 14, "bold"),
            fg="#FFD700",
            bg='#1E3A5F',
            pady=30,
            justify='center'
        )
        lbl_mensaje.pack()
        
        # Frame para botones
        frame_botones = tk.Frame(dialogo_fin, bg='#1E3A5F')
        frame_botones.pack(pady=20)
        
        # Botón para nueva partida
        btn_nueva_partida = tk.Button(
            frame_botones,
            text="Jugar Otra Partida",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=lambda: [self.reiniciar_juego(), dialogo_fin.destroy()]
        )
        btn_nueva_partida.pack(side='left', padx=10)
        
        # Botón para menú principal
        btn_menu = tk.Button(
            frame_botones,
            text="Menú Principal",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            width=12,
            command=lambda: [self.volver_al_menu(), dialogo_fin.destroy()]
        )
        btn_menu.pack(side='left', padx=10)
        
        # Actualizar etiquetas en la interfaz principal
        self.lbl_turno.configure(text=f"Fin del juego")
        self.lbl_estado.configure(text=resultado)
        
        # Deshabilitar todas las casillas
        for fila in range(8):
            for columna in range(8):
                self.casillas[fila][columna].configure(state='disabled')
    
    def manejar_click(self, fila, columna):
        if not self.juego_activo or self.juego_terminado:
            return
        
        casilla = self.coordenadas_a_casilla(fila, columna)
        pieza = self.tablero.piece_at(casilla)
        
        if self.pieza_seleccionada is None:
            if pieza and ((pieza.color == chess.WHITE and self.tablero.turn == chess.WHITE) or 
                         (pieza.color == chess.BLACK and self.tablero.turn == chess.BLACK)):
                self.pieza_seleccionada = casilla
                self.casilla_seleccionada = (fila, columna)
                self.movimientos_validos = self.obtener_movimientos_validos(casilla)
                
                self.limpiar_marcadores()
                self.casillas[fila][columna].configure(bg=self.color_seleccionado)
                for movimiento in self.movimientos_validos:
                    mov_fila, mov_col = self.casilla_a_coordenadas(movimiento)
                    self.casillas[mov_fila][mov_col].configure(bg=self.color_movimiento_valido)
        else:
            casilla_origen = self.pieza_seleccionada
            pieza_movida = self.tablero.piece_at(casilla_origen)
            es_blanco = pieza_movida.color == chess.WHITE
            
            if casilla in self.movimientos_validos:
                movimiento = chess.Move(casilla_origen, casilla)
                self.colocar_pieza = sonido_colocar_pieza.play()
                
                # Verificar si hay captura
                pieza_capturada = self.tablero.piece_at(casilla)
                if pieza_capturada:
                    # Registrar captura en el sistema de puntos
                    puntos_captura = self.sistema_puntos.registrar_captura(pieza_capturada, es_blanco)
                    tipo_pieza = self.nombres_piezas[pieza_capturada.piece_type]
                    self.mostrar_mensaje_puntos(puntos_captura, f"Captura de {tipo_pieza}", es_blanco)
                
                # Verificar si es jaque
                tablero_temporal = self.tablero.copy()
                tablero_temporal.push(movimiento)
                if tablero_temporal.is_check():
                    puntos_jaque = self.sistema_puntos.registrar_movimiento_especial('jaque', es_blanco)
                    self.mostrar_mensaje_puntos(puntos_jaque, "Jaque al rey", es_blanco)
                
                if self.tablero.piece_at(casilla_origen).piece_type == chess.PAWN:
                    fila_final = chess.square_rank(casilla)
                    if fila_final == 0 or fila_final == 7:
                        if self.manejar_promocion(movimiento):
                            pass
                        else:
                            movimiento.promotion = chess.QUEEN
                            self.tablero.push(movimiento)
                            self.actualizar_tablero()
                    else:
                        self.tablero.push(movimiento)
                        self.actualizar_tablero()
                else:
                    self.tablero.push(movimiento)
                    self.actualizar_tablero()
                
                # Actualizar panel de puntos
                self.actualizar_panel_puntos()
                
                if not self.verificar_fin_del_juego():
                    self.lbl_turno.configure(text=f"Turno: {'Blanco' if self.tablero.turn else 'Negro'}")
                    self.lbl_estado.configure(text=self.obtener_estado_juego())
            
            self.pieza_seleccionada = None
            self.casilla_seleccionada = None
            self.movimientos_validos = []
            self.limpiar_marcadores()
    
    def actualizar_tablero(self):
        """Actualiza toda la interfaz gráfica del tablero"""
        for fila in range(8):
            for columna in range(8):
                square = chess.square(columna, 7 - fila)
                pieza_unicode = self.obtener_pieza_unicode(square)
                color = self.color_claro if (fila + columna) % 2 == 0 else self.color_oscuro
                
                casilla = self.casillas[fila][columna]
                casilla.configure(
                    image=self.imagenes[pieza_unicode],
                    bg=color
                )
                casilla.image = self.imagenes[pieza_unicode]
        
        # Después de actualizar el tablero, verificar y resaltar jaque
        self.resaltar_jaque()
    
    def reiniciar_juego(self):
        """Reinicia el juego al estado inicial"""
        self.tablero = chess.Board()
        self.pieza_seleccionada = None
        self.casilla_seleccionada = None
        self.movimientos_validos = []
        self.juego_terminado = False
        
        # Reiniciar sistema de puntos
        self.sistema_puntos.reiniciar_puntos()
        
        self.lbl_turno.configure(text=f"Turno: {'Blanco' if self.tablero.turn else 'Negro'}")
        self.lbl_estado.configure(text=self.obtener_estado_juego())
        
        for fila in range(8):
            for columna in range(8):
                self.casillas[fila][columna].configure(state='normal')
        
        self.actualizar_tablero()
        self.actualizar_panel_puntos()
    
    def ejecutar(self):
        self.root.mainloop()

# Ejecutar el juego
if __name__ == "__main__":
    juego = AjedrezCompleto()
    juego.ejecutar()