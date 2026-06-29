import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageDraw
import cv2
import numpy as np
import svgwrite


class ImageProcessor:
    def __init__(self,root):
        self.root = root
        self.root.title("Инструмент для обработки изображений")
        self.root.geometry('1200x800')
        self.original_image = None  # Исходное изображение
        self.processed_image = None  # Обработанное изображение
        self.setup_ui()  # Настройка интерфейса

    def setup_ui(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левый фрейм для исходного изображения
        self.left_frame = ttk.LabelFrame(main_frame, text="Исходное изображение")
        self.left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Правый фрейм для обработанного изображения
        self.right_frame = ttk.LabelFrame(main_frame, text="Обработанное изображение")
        self.right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление")
        control_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Настройка весов grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Метки для изображений
        self.original_label = ttk.Label(self.left_frame, text="Изображение не загружено")
        self.original_label.pack(padx=10, pady=10)

        self.processed_label = ttk.Label(self.right_frame, text="Здесь появится обработанное изображение")
        self.processed_label.pack(padx=10, pady=10)

        # Кнопки управления
        self.create_buttons(control_frame)

        # Преобразование цветового пространства
        self.create_color_space_widgets(control_frame)

        # Коррекция контраста
        self.create_contrast_widgets(control_frame)

        # Векторизация
        self.create_vectorization_widgets(control_frame)

    def create_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Загрузить изображение", command = self.load_image).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame, text="Сохранить результат", command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сбросить изменения", command=self.reset_image).pack(side=tk.LEFT, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.processed_image = self.original_image.copy()
                self.display_images()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")

    def save_image(self):
        if not self.processed_image:
            messagebox.showerror("Ошибка", f"Нет изображения")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("JPEG файлы", "*.jpg"), ("Все файлы", "*.*")]
        )

        if file_path:
            try:
                self.processed_image.save(file_path)

            except Exception as e:
                messagebox.showerror("Ошибка",f"Не удалось сохранить файл {e}")

    def reset_image(self):
        if self.original_image:
            self.processed_image = self.original_image.copy()
            self.display_images()
        else:
            messagebox.showerror("Ошибка",f"Нет изображения")

    def display_images(self):
        if self.original_image:
            orig_display = self.original_image.copy()
            orig_display.thumbnail((600, 600))
            orig_photo = ImageTk.PhotoImage(orig_display)
            self.original_label.config(image = orig_photo)
            self.original_label.image=orig_photo

        if self.processed_image:
            proc_display = self.processed_image.copy()
            proc_display.thumbnail((600, 600))
            proc_photo = ImageTk.PhotoImage(proc_display)
            self.processed_label.config(image=proc_photo)
            self.processed_label.image = proc_photo

    def create_color_space_widgets(self,parent):
        """Виджеты для преобразования цветовых пространств"""
        color_frame = ttk.LabelFrame(parent, text="Преобразование цветового пространства")
        color_frame.pack(fill=tk.X, padx=5, pady=5)

        self.color_var = tk.StringVar()

        color_combo = ttk.Combobox(color_frame,textvariable = self.color_var,
                                   values =["RGB", "HSV", "LAB", "CMYK", "Негатив"])

        color_combo.set("RGB")
        color_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(color_frame, text="Применить",command=self.convert_color_space).pack(side=tk.LEFT, padx=5)

    def create_contrast_widgets(self,parent):
        contrast_frame = ttk.LabelFrame(parent, text="Коррекция контраста и яркости")
        contrast_frame.pack(fill=tk.X, padx=5, pady=5)

        # Слайдер для контраста
        ttk.Label(contrast_frame, text="Контраст:").pack(side=tk.LEFT, padx=5)
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = ttk.Scale(contrast_frame, from_=0.1, to=3.0,
                                   variable=self.contrast_var, orient=tk.HORIZONTAL)
        contrast_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Слайдер для яркости
        ttk.Label(contrast_frame, text="Яркость:").pack(side=tk.LEFT, padx=5)
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = ttk.Scale(contrast_frame, from_=0.1, to=3.0,
                                     variable=self.brightness_var, orient=tk.HORIZONTAL)
        brightness_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(contrast_frame, text="Применить коррекцию", command=self.adjust_contrast_brightness).pack(
            side=tk.LEFT, padx=5)

    def create_vectorization_widgets(self,parent):
        vectorization_frame = ttk.LabelFrame(parent, text ="Векторизация изображения")
        vectorization_frame.pack(fill=tk.X, padx=5,pady=5)

        ttk.Button(vectorization_frame, text="Векторизовать в SVG",command=self.vectorize_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(vectorization_frame, text="Обнаружение краев", command=self.edge_detection).pack(side=tk.LEFT, padx=5)
        ttk.Button(vectorization_frame, text="Упрощенная векторизация", command=self.simple_vectorization).pack(side=tk.LEFT, padx=5)

    def convert_color_space(self):
        if not self.original_image:
            messagebox.showerror("Ошибка", "Нет изображения")
            return

        color_space = self.color_var.get()
        rgb_image = self.original_image.convert("RGB")
        rgb_array = np.array(rgb_image)

        try:
            if color_space == "HSV":
                # Преобразование RGB → HSV и визуализация каналов
                hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)

                # Создаем визуализацию HSV каналов
                # H (оттенок) - нормализуем для отображения (0-180 -> 0-255)
                h_visualized = (hsv_array[:, :, 0].astype(np.float32) * 255 / 180).astype(np.uint8)
                # S (насыщенность) - как есть
                s_visualized = hsv_array[:, :, 1]
                # V (яркость) - как есть
                v_visualized = hsv_array[:, :, 2]

                # Комбинируем для наглядного отображения
                hsv_visualized = np.stack([h_visualized, s_visualized, v_visualized], axis=2)
                self.processed_image = Image.fromarray(hsv_visualized)

            elif color_space == "LAB":
                # Преобразование RGB → LAB
                lab_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2LAB)

                # Нормализуем каждый канал для отображения
                l_channel = lab_array[:, :, 0]  # L: 0-255
                a_channel = cv2.normalize(lab_array[:, :, 1], None, 0, 255, cv2.NORM_MINMAX)  # A: нормализуем
                b_channel = cv2.normalize(lab_array[:, :, 2], None, 0, 255, cv2.NORM_MINMAX)  # B: нормализуем

                lab_visualized = np.stack([l_channel, a_channel.astype(np.uint8), b_channel.astype(np.uint8)], axis=2)
                self.processed_image = Image.fromarray(lab_visualized)

            elif color_space == "CMYK":
                # Визуализация CMYK через разделение каналов
                rgb_float = rgb_array.astype(np.float32) / 255.0

                # Расчет CMYK компонентов
                k = 1 - np.max(rgb_float, axis=2)
                c = (1 - rgb_float[:, :, 0] - k) / (1 - k + 1e-6)
                m = (1 - rgb_float[:, :, 1] - k) / (1 - k + 1e-6)
                y = (1 - rgb_float[:, :, 2] - k) / (1 - k + 1e-6)

                # Визуализация каждого канала CMYK как grayscale
                c_visualized = (c * 255).astype(np.uint8)
                m_visualized = (m * 255).astype(np.uint8)
                y_visualized = (y * 255).astype(np.uint8)
                k_visualized = (k * 255).astype(np.uint8)

                # Создаем комбинированное изображение CMYK (4 канала -> 3 канала RGB)
                # Размещаем каналы в RGB: C -> Red, M -> Green, Y -> Blue, K игнорируем для визуализации
                cmy_visualized = np.stack([c_visualized, m_visualized, y_visualized], axis=2)
                self.processed_image = Image.fromarray(cmy_visualized)

            elif color_space == "Негатив":
                # Простое инвертирование
                inverted_array = 255 - rgb_array
                self.processed_image = Image.fromarray(inverted_array)

            else:  # RGB
                self.processed_image = rgb_image.copy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка преобразования цветового пространства: {e}")
            self.processed_image = rgb_image.copy()

        self.display_images()

    def adjust_contrast_brightness(self):
        if not self.processed_image:
            messagebox.showerror("Ошибка", f"Нет изображения")
            return
        contrast_factor = self.contrast_var.get()
        brightness_factor = self.brightness_var.get()

        # Применение контраста
        contrast_enhancer = ImageEnhance.Contrast(self.original_image)
        temp_image = contrast_enhancer.enhance(contrast_factor)

        # Применение яркости
        brightness_enhancer = ImageEnhance.Brightness(temp_image)
        self.processed_image = brightness_enhancer.enhance(brightness_factor)

        self.display_images()

    def vectorize_image(self):
        if not self.processed_image:
            messagebox.showerror("Ошибка", f"Нет изображения")
            return
        file_path = filedialog.asksaveasfilename(
            title="Сохранить SVG файл",
            defaultextension=".svg",
            filetypes=[("SVG файлы", "*.svg"), ("Все файлы", "*.*")]
        )

        if file_path:
            try:
                self.create_svg_from_image(self.original_image, file_path)
            except Exception as e:
                messagebox.showerror("Ошибка!",f"{e}")

    def edge_detection(self):
        if not self.processed_image:
            messagebox.showerror("Ошибка", f"Нет изображения")
            return
        # Конвертация в оттенки серого для обнаружения краёв
        gray_image = self.original_image.convert("L")
        img_array = np.array(gray_image)

        # Применение детектора краёв Canny
        edges = cv2.Canny(img_array, 100, 200)

        self.processed_image = Image.fromarray(edges)
        self.display_images()

    def simple_vectorization(self):
        """Упрощённая векторизация для предпросмотра"""
        if not self.processed_image:
            messagebox.showerror("Ошибка", f"Нет изображения")
            return

        try:
            # Упрощённая векторная репрезентация
            small_image = self.original_image.copy()
            small_image.thumbnail((100, 100))  # Уменьшаем для скорости
            img_array = np.array(small_image.convert("RGB"))
            height, width = img_array.shape[:2]

            # Создаём упрощённое векторное представление
            result = Image.new("RGB", self.original_image.size, "white")
            draw = ImageDraw.Draw(result)

            # Рисуем круги в местах значимых пикселей
            step = 1
            for y in range(0, height, step):
                for x in range(0, width, step):
                    if y < height and x < width:
                        r, g, b = img_array[y, x]
                        # Рисуем круг только для достаточно тёмных пикселей
                        if r + g + b < 600:  # Пороговое значение
                            scale = self.original_image.width / width
                            draw.ellipse([
                                x * scale - 3, y * scale - 3,
                                x * scale + 3, y * scale + 3
                            ], fill=(r, g, b))

            self.processed_image = result
            self.display_images()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка упрощённой векторизации: {e}")

    def create_svg_from_image(self, image, output_path):
        image = image.convert("RGB")
        # Уменьшаем размер для производительности
        small_image = image.copy()
        small_image.thumbnail((200, 200))
        img_array = np.array(small_image)
        height, width = img_array.shape[:2]

        # Масштаб для оригинального размера
        scale_x = image.width / width
        scale_y = image.height / height

        dwg = svgwrite.Drawing(output_path, size=(image.width, image.height))

        # Фон
        dwg.add(dwg.rect(insert=(0, 0), size=(image.width, image.height), fill='white'))

        # Добавляем элементы векторной графики
        step = 2  # Шаг дискретизации
        for y in range(0, height, step):
            for x in range(0, width, step):
                if y < height and x < width:
                    r, g, b = img_array[y, x]
                    color = f'rgb({r},{g},{b})'
                    # Пропускаем очень светлые пиксели
                    if r + g + b < 750:  # Порог для исключения фона
                        dwg.add(dwg.circle(
                            center=(x * scale_x, y * scale_y),
                            r=2 * min(scale_x, scale_y),
                            fill=color
                        ))

        dwg.save()
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()


