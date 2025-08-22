import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class BaseInterface:

    def __init__(self):
        self.root = tk.Tk()
        self.frame_top = tk.Frame(self.root, bg=self.white)
        self.frame_bottom = tk.Frame(self.root, bg=self.white)
        self.frame_settings = tk.Frame(self.root, bg=self.white)
        self.frame_text = tk.Frame(self.root, bg=self.white)

    def on_button_click(self):
        self.root.destroy()

    white = "#F3F3F3"
    blue = "#0078D7"
    pink = "#FF69B4"
    btn_text_color = "white"

    def initialize(self, name_programm):
        self.root.title(name_programm)
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.root.configure(bg=self.white)
        self.place_frames()
        self.root.mainloop()

    def create_button(self, text_button, button_funk, frame=None, background_color=None):
        background_color = background_color if background_color else self.blue
        frame = frame if frame else self.frame_top
        btn1 = tk.Button(frame, text=text_button, bg=background_color, fg=self.btn_text_color,
                         font=("Segoe UI", 12, "bold"), bd=0,
                         relief="flat", padx=20, pady=10, command=button_funk)
        btn1.pack(side="left", padx=10)

    def show_info(self, text, frame=None):
        frame = frame if frame else self.frame_text

        # Очищаем предыдущие виджеты
        for widget in frame.winfo_children():
            widget.destroy()

        # Если text — список, преобразуем в строку с переносами
        if isinstance(text, (list, tuple)):
            text = "\n".join(str(item) for item in text)

        # Создаём ScrolledText — текстовое поле с вертикальной прокруткой
        text_widget = ScrolledText(frame, width=50, height=10)
        text_widget.pack(fill='both', expand=True, padx=10, pady=5)
        text_widget.insert('1.0', text)
        text_widget.configure(state='disabled')  # делаем поле только для чтения

    def place_frames(self):
        # Конфигурируем 3 колонки: левая и правая «растягиваются» как пустое место
        self.root.grid_columnconfigure(0, weight=1)  # Левая пустая колонка
        self.root.grid_columnconfigure(1, weight=0)  # Средняя колонка с контентом
        self.root.grid_columnconfigure(2, weight=1)  # Правая пустая колонка

        self.frame_top.grid(row=0, column=1)
        self.frame_bottom.grid(row=1, column=1)
        self.frame_settings.grid(row=2, column=1, pady=(10, 20), padx=20)
        self.frame_text.grid(row=3, column=1, pady=(5, 20), padx=20)

        self.frame_bottom.grid_remove()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

    def clear_frames(self):
        for frame in [self.frame_top, self.frame_bottom, self.frame_settings]:
            for widget in frame.winfo_children():
                widget.destroy()

    def invert_frames(self):
        if self.frame_top.winfo_ismapped():
            self.frame_top.grid_remove()  # Скрываем верхний фрейм
            self.frame_bottom.grid()
        else:
            self.frame_bottom.grid_remove()  # Скрываем нижний фрейм
            self.frame_top.grid()