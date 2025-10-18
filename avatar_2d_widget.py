# ui/avatar_2d_widget.py
"""
Avatar 2D féminin personnalisable avec vêtements et expressions
"""
import tkinter as tk
from tkinter import Canvas, ttk
import math


class Avatar2DWidget:
    """Avatar 2D féminin avec expressions et customisation"""
    
    def __init__(self, parent, size=200):
        self.size = size
        self.canvas = Canvas(
            parent, 
            width=size, 
            height=size,
            bg='#2b2b2b',
            highlightthickness=0
        )
        
        self.center_x = size // 2
        self.center_y = size // 2
        
        # États
        self.current_expression = "neutral"
        self.current_outfit = "casual"
        self.is_speaking = False
        self.is_thinking = False
        self.animation_frame = 0
        
        # Éléments du personnage
        self.elements = {}
        
        # Couleurs personnalisables
        self.skin_color = "#FFD1A8"
        self.hair_color = "#4A2C2A"
        self.eye_color = "#2E7D32"
        
        self.draw_avatar()
        
    def draw_avatar(self):
        """Dessine le personnage complet"""
        # Ordre de dessin : arrière-plan -> corps -> vêtements -> visage -> cheveux
        self._draw_body()
        self._draw_outfit(self.current_outfit)
        self._draw_face()
        self._draw_hair()
        
    def _draw_body(self):
        """Dessine le corps de base"""
        # Cou
        self.elements['neck'] = self.canvas.create_rectangle(
            self.center_x - 10, 85, self.center_x + 10, 100,
            fill=self.skin_color,
            outline=''
        )
        
        # Épaules
        self.elements['shoulders'] = self.canvas.create_oval(
            self.center_x - 35, 90, self.center_x + 35, 110,
            fill=self.skin_color,
            outline=''
        )
        
        # Buste (forme de base)
        self.elements['torso'] = self.canvas.create_polygon(
            self.center_x - 30, 105,
            self.center_x + 30, 105,
            self.center_x + 25, 160,
            self.center_x - 25, 160,
            fill=self.skin_color,
            outline='',
            smooth=True
        )
        
    def _draw_outfit(self, outfit_type="casual"):
        """Dessine les vêtements"""
        # Effacer les vêtements existants
        for key in list(self.elements.keys()):
            if key.startswith('outfit_'):
                self.canvas.delete(self.elements[key])
                del self.elements[key]
        
        if outfit_type == "casual":
            # T-shirt décontracté
            self.elements['outfit_top'] = self.canvas.create_polygon(
                self.center_x - 32, 100,
                self.center_x + 32, 100,
                self.center_x + 28, 165,
                self.center_x - 28, 165,
                fill='#FF6B9D',
                outline='#D81B60',
                width=2,
                smooth=True
            )
            
            # Manches courtes
            self.elements['outfit_sleeve_l'] = self.canvas.create_oval(
                self.center_x - 50, 95, self.center_x - 25, 120,
                fill='#FF6B9D',
                outline='#D81B60',
                width=2
            )
            
            self.elements['outfit_sleeve_r'] = self.canvas.create_oval(
                self.center_x + 25, 95, self.center_x + 50, 120,
                fill='#FF6B9D',
                outline='#D81B60',
                width=2
            )
            
            # Détails (cœur sur le t-shirt)
            self.elements['outfit_detail'] = self.canvas.create_text(
                self.center_x, 130,
                text="♥",
                fill='white',
                font=('Arial', 16, 'bold')
            )
            
        elif outfit_type == "formal":
            # Chemise formelle
            self.elements['outfit_top'] = self.canvas.create_polygon(
                self.center_x - 32, 100,
                self.center_x + 32, 100,
                self.center_x + 28, 165,
                self.center_x - 28, 165,
                fill='white',
                outline='#455A64',
                width=2,
                smooth=True
            )
            
            # Veste
            self.elements['outfit_jacket'] = self.canvas.create_polygon(
                self.center_x - 35, 105,
                self.center_x + 35, 105,
                self.center_x + 30, 170,
                self.center_x - 30, 170,
                fill='#263238',
                outline='#000000',
                width=1,
                smooth=True
            )
            
            # Revers
            self.elements['outfit_lapel_l'] = self.canvas.create_polygon(
                self.center_x - 10, 105,
                self.center_x - 35, 105,
                self.center_x - 20, 130,
                fill='#37474F',
                outline=''
            )
            
            self.elements['outfit_lapel_r'] = self.canvas.create_polygon(
                self.center_x + 10, 105,
                self.center_x + 35, 105,
                self.center_x + 20, 130,
                fill='#37474F',
                outline=''
            )
            
        elif outfit_type == "sporty":
            # Débardeur sportif
            self.elements['outfit_top'] = self.canvas.create_polygon(
                self.center_x - 28, 100,
                self.center_x + 28, 100,
                self.center_x + 25, 150,
                self.center_x - 25, 150,
                fill='#00BCD4',
                outline='#0097A7',
                width=2,
                smooth=True
            )
            
            # Bretelles
            self.elements['outfit_strap_l'] = self.canvas.create_rectangle(
                self.center_x - 22, 100, self.center_x - 16, 105,
                fill='#00BCD4',
                outline='#0097A7',
                width=1
            )
            
            self.elements['outfit_strap_r'] = self.canvas.create_rectangle(
                self.center_x + 16, 100, self.center_x + 22, 105,
                fill='#00BCD4',
                outline='#0097A7',
                width=1
            )
            
        elif outfit_type == "minimal":
            # Version minimale (sous-vêtements)
            self.elements['outfit_top'] = self.canvas.create_oval(
                self.center_x - 25, 100, self.center_x + 25, 140,
                fill='#E1BEE7',
                outline='#9C27B0',
                width=2
            )
    
    def _draw_face(self):
        """Dessine le visage"""
        # Tête (ovale)
        self.elements['head'] = self.canvas.create_oval(
            self.center_x - 30, 20, self.center_x + 30, 90,
            fill=self.skin_color,
            outline='#D4A574',
            width=2
        )
        
        # Yeux
        self.elements['eye_l'] = self.canvas.create_oval(
            self.center_x - 18, 45, self.center_x - 8, 52,
            fill='white',
            outline='#5D4037',
            width=2
        )
        
        self.elements['eye_r'] = self.canvas.create_oval(
            self.center_x + 8, 45, self.center_x + 18, 52,
            fill='white',
            outline='#5D4037',
            width=2
        )
        
        # Pupilles
        self.elements['pupil_l'] = self.canvas.create_oval(
            self.center_x - 15, 47, self.center_x - 11, 51,
            fill=self.eye_color,
            outline=''
        )
        
        self.elements['pupil_r'] = self.canvas.create_oval(
            self.center_x + 11, 47, self.center_x + 15, 51,
            fill=self.eye_color,
            outline=''
        )
        
        # Cils
        self.elements['lash_l'] = self.canvas.create_line(
            self.center_x - 18, 45, self.center_x - 20, 42,
            fill='#5D4037',
            width=2
        )
        
        self.elements['lash_r'] = self.canvas.create_line(
            self.center_x + 18, 45, self.center_x + 20, 42,
            fill='#5D4037',
            width=2
        )
        
        # Sourcils
        self.elements['eyebrow_l'] = self.canvas.create_arc(
            self.center_x - 20, 35, self.center_x - 6, 43,
            start=0, extent=180,
            style=tk.ARC,
            outline='#5D4037',
            width=2
        )
        
        self.elements['eyebrow_r'] = self.canvas.create_arc(
            self.center_x + 6, 35, self.center_x + 20, 43,
            start=0, extent=180,
            style=tk.ARC,
            outline='#5D4037',
            width=2
        )
        
        # Nez (subtil)
        self.elements['nose'] = self.canvas.create_line(
            self.center_x, 55, self.center_x + 2, 62,
            fill='#D4A574',
            width=2,
            smooth=True
        )
        
        # Bouche
        self.elements['mouth'] = self.canvas.create_arc(
            self.center_x - 10, 65, self.center_x + 10, 75,
            start=0, extent=-180,
            style=tk.ARC,
            outline='#D81B60',
            width=2
        )
        
        # Joues (blush)
        self.elements['blush_l'] = self.canvas.create_oval(
            self.center_x - 28, 58, self.center_x - 20, 64,
            fill='#FFCDD2',
            outline=''
        )
        
        self.elements['blush_r'] = self.canvas.create_oval(
            self.center_x + 20, 58, self.center_x + 28, 64,
            fill='#FFCDD2',
            outline=''
        )
    
    def _draw_hair(self):
        """Dessine les cheveux"""
        # Frange
        self.elements['hair_bangs'] = self.canvas.create_arc(
            self.center_x - 35, 15, self.center_x + 35, 50,
            start=0, extent=180,
            fill=self.hair_color,
            outline='#3E2723',
            width=2
        )
        
        # Côtés
        self.elements['hair_side_l'] = self.canvas.create_arc(
            self.center_x - 40, 30, self.center_x - 15, 95,
            start=90, extent=90,
            fill=self.hair_color,
            outline='#3E2723',
            width=2,
            style=tk.CHORD
        )
        
        self.elements['hair_side_r'] = self.canvas.create_arc(
            self.center_x + 15, 30, self.center_x + 40, 95,
            start=0, extent=90,
            fill=self.hair_color,
            outline='#3E2723',
            width=2,
            style=tk.CHORD
        )
        
        # Arrière (queue de cheval optionnelle)
        if hasattr(self, 'show_ponytail') and self.show_ponytail:
            self.elements['ponytail'] = self.canvas.create_oval(
                self.center_x + 25, 50, self.center_x + 45, 80,
                fill=self.hair_color,
                outline='#3E2723',
                width=2
            )
    
    def set_expression(self, expression: str):
        """Change l'expression du visage"""
        self.current_expression = expression
        
        if expression == "happy":
            self._expression_happy()
        elif expression == "sad":
            self._expression_sad()
        elif expression == "surprised":
            self._expression_surprised()
        elif expression == "thinking":
            self._expression_thinking()
        elif expression == "wink":
            self._expression_wink()
        elif expression == "love":
            self._expression_love()
        else:
            self._expression_neutral()
    
    def _expression_neutral(self):
        """Expression neutre"""
        # Yeux normaux
        self.canvas.coords(self.elements['eye_l'], 
            self.center_x - 18, 45, self.center_x - 8, 52)
        self.canvas.coords(self.elements['eye_r'], 
            self.center_x + 8, 45, self.center_x + 18, 52)
        
        # Bouche neutre
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 10, 65, self.center_x + 10, 75)
        self.canvas.itemconfig(self.elements['mouth'], 
            start=0, extent=-180, style=tk.ARC)
    
    def _expression_happy(self):
        """Expression joyeuse"""
        # Yeux souriants (fermés partiellement)
        self.canvas.coords(self.elements['eye_l'], 
            self.center_x - 18, 47, self.center_x - 8, 51)
        self.canvas.coords(self.elements['eye_r'], 
            self.center_x + 8, 47, self.center_x + 18, 51)
        
        # Grand sourire
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 12, 64, self.center_x + 12, 78)
        self.canvas.itemconfig(self.elements['mouth'], 
            start=0, extent=-180, style=tk.ARC, width=3)
    
    def _expression_love(self):
        """Expression amoureuse (yeux en cœur)"""
        # Remplacer les yeux par des cœurs
        self.canvas.itemconfig(self.elements['eye_l'], state='hidden')
        self.canvas.itemconfig(self.elements['eye_r'], state='hidden')
        self.canvas.itemconfig(self.elements['pupil_l'], state='hidden')
        self.canvas.itemconfig(self.elements['pupil_r'], state='hidden')
        
        if 'heart_l' not in self.elements:
            self.elements['heart_l'] = self.canvas.create_text(
                self.center_x - 13, 48,
                text="♥",
                fill='#E91E63',
                font=('Arial', 12, 'bold')
            )
            self.elements['heart_r'] = self.canvas.create_text(
                self.center_x + 13, 48,
                text="♥",
                fill='#E91E63',
                font=('Arial', 12, 'bold')
            )
        else:
            self.canvas.itemconfig(self.elements['heart_l'], state='normal')
            self.canvas.itemconfig(self.elements['heart_r'], state='normal')
        
        # Sourire doux
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 10, 66, self.center_x + 10, 76)
    
    def _expression_wink(self):
        """Clin d'œil"""
        # Œil gauche fermé
        self.canvas.coords(self.elements['eye_l'], 
            self.center_x - 18, 48, self.center_x - 8, 50)
        
        # Œil droit normal
        self.canvas.coords(self.elements['eye_r'], 
            self.center_x + 8, 45, self.center_x + 18, 52)
        
        # Sourire espiègle
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 10, 65, self.center_x + 10, 76)
    
    def _expression_surprised(self):
        """Expression surprise"""
        # Grands yeux
        self.canvas.coords(self.elements['eye_l'], 
            self.center_x - 19, 43, self.center_x - 7, 54)
        self.canvas.coords(self.elements['eye_r'], 
            self.center_x + 7, 43, self.center_x + 19, 54)
        
        # Bouche en O
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 6, 68, self.center_x + 6, 76)
        self.canvas.itemconfig(self.elements['mouth'], 
            start=0, extent=360, style=tk.CHORD, fill='#FFEBEE')
    
    def _expression_thinking(self):
        """Expression pensive"""
        # Yeux vers le haut
        self.canvas.coords(self.elements['pupil_l'], 
            self.center_x - 15, 45, self.center_x - 11, 49)
        self.canvas.coords(self.elements['pupil_r'], 
            self.center_x + 11, 45, self.center_x + 15, 49)
        
        # Petite bouche
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 8, 67, self.center_x + 8, 73)
    
    def _expression_sad(self):
        """Expression triste"""
        # Sourcils tristes
        self.canvas.coords(self.elements['eyebrow_l'],
            self.center_x - 22, 37, self.center_x - 6, 40)
        self.canvas.coords(self.elements['eyebrow_r'],
            self.center_x + 6, 40, self.center_x + 22, 37)
        
        # Bouche triste (arc inversé)
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 10, 75, self.center_x + 10, 68)
    
    def change_outfit(self, outfit: str):
        """Change la tenue"""
        self.current_outfit = outfit
        self._draw_outfit(outfit)
    
    def change_hair_color(self, color: str):
        """Change la couleur des cheveux"""
        self.hair_color = color
        for key in ['hair_bangs', 'hair_side_l', 'hair_side_r', 'ponytail']:
            if key in self.elements:
                self.canvas.itemconfig(self.elements[key], fill=color)
    
    def change_eye_color(self, color: str):
        """Change la couleur des yeux"""
        self.eye_color = color
        self.canvas.itemconfig(self.elements['pupil_l'], fill=color)
        self.canvas.itemconfig(self.elements['pupil_r'], fill=color)
    
    def animate_speaking(self):
        """Animation de parole"""
        if not self.is_speaking:
            return
            
        self.animation_frame += 1
        
        # Bouche qui bouge
        offset = math.sin(self.animation_frame * 0.3) * 2
        self.canvas.coords(self.elements['mouth'],
            self.center_x - 10,
            65 + offset,
            self.center_x + 10,
            75 - offset
        )
        
        self.canvas.after(100, self.animate_speaking)
    
    def start_speaking(self):
        """Démarre l'animation de parole"""
        self.is_speaking = True
        self.animate_speaking()
    
    def stop_speaking(self):
        """Arrête l'animation de parole"""
        self.is_speaking = False
        self.set_expression("neutral")
    
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)


# Panneau de customisation
class AvatarCustomizationPanel:
    """Panneau pour personnaliser l'avatar"""
    
    def __init__(self, parent, avatar_widget):
        self.avatar = avatar_widget
        self.panel = ttk.LabelFrame(parent, text="Personnalisation Avatar", padding=10)
        
        # Tenues
        ttk.Label(self.panel, text="Tenue:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        outfit_frame = ttk.Frame(self.panel)
        outfit_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(outfit_frame, text="👕 Casual", 
                   command=lambda: self.avatar.change_outfit("casual")).pack(side=tk.LEFT, padx=2)
        ttk.Button(outfit_frame, text="👔 Formel", 
                   command=lambda: self.avatar.change_outfit("formal")).pack(side=tk.LEFT, padx=2)
        ttk.Button(outfit_frame, text="🏃 Sport", 
                   command=lambda: self.avatar.change_outfit("sporty")).pack(side=tk.LEFT, padx=2)
        ttk.Button(outfit_frame, text="👙 Minimal", 
                   command=lambda: self.avatar.change_outfit("minimal")).pack(side=tk.LEFT, padx=2)
        
        # Expressions
        ttk.Label(self.panel, text="Expression:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        expr_frame = ttk.Frame(self.panel)
        expr_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(expr_frame, text="😊 Joyeux", 
                   command=lambda: self.avatar.set_expression("happy")).pack(side=tk.LEFT, padx=2)
        ttk.Button(expr_frame, text="😍 Amour", 
                   command=lambda: self.avatar.set_expression("love")).pack(side=tk.LEFT, padx=2)
        ttk.Button(expr_frame, text="😉 Clin d'œil", 
                   command=lambda: self.avatar.set_expression("wink")).pack(side=tk.LEFT, padx=2)
        ttk.Button(expr_frame, text="😮 Surpris", 
                   command=lambda: self.avatar.set_expression("surprised")).pack(side=tk.LEFT, padx=2)
        
        # Couleurs cheveux
        ttk.Label(self.panel, text="Cheveux:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        hair_frame = ttk.Frame(self.panel)
        hair_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        hair_colors = [
            ("Brun", "#4A2C2A"),
            ("Blond", "#F4D03F"),
            ("Noir", "#1C1C1C"),
            ("Roux", "#C86428"),
            ("Rose", "#FF6B9D")
        ]
        
        for name, color in hair_colors:
            btn = tk.Button(hair_frame, text="  ", bg=color, width=2,
                           command=lambda c=color: self.avatar.change_hair_color(c))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Couleurs yeux
        ttk.Label(self.panel, text="Yeux:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        eye_frame = ttk.Frame(self.panel)
        eye_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        eye_colors = [
            ("Vert", "#2E7D32"),
            ("Bleu", "#1976D2"),
            ("Marron", "#5D4037"),
            ("Gris", "#607D8B"),
            ("Violet", "#7B1FA2")
        ]
        
        for name, color in eye_colors:
            btn = tk.Button(eye_frame, text="  ", bg=color, width=2,
                           command=lambda c=color: self.avatar.change_eye_color(c))
            btn.pack(side=tk.LEFT, padx=2)
    
    def pack(self, **kwargs):
        self.panel.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.panel.grid(**kwargs)
