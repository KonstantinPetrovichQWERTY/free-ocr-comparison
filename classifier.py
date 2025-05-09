import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class OCRValidator:
    def __init__(self, root, json_path):
        self.root = root
        self.root.title("OCR Validator")
        
        # Загрузка данных
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.image_files = list(self.data.keys())
        self.total_items = len(self.image_files)
        
        # Инициализация переменных
        self.current_index = 0
        self.correct = 0
        self.incorrect = 0
        self.results = {}  # Для хранения результатов проверки
        
        # Создание интерфейса
        self.create_widgets()
        self.show_current_item()
        
    def create_widgets(self):
        # Фрейм для изображения
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(pady=10)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()
        
        # Фрейм для текста OCR
        self.text_frame = ttk.Frame(self.root)
        self.text_frame.pack(pady=10)
        
        self.ocr_label = ttk.Label(self.text_frame, text="OCR Text:", font=('Arial', 12))
        self.ocr_label.pack()
        
        self.ocr_text = tk.Text(self.text_frame, height=3, width=50, wrap=tk.WORD, font=('Arial', 12))
        self.ocr_text.pack()
        self.ocr_text.config(state=tk.DISABLED)
        
        # Фрейм для навигации
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(pady=10)
        
        self.prev_btn = ttk.Button(self.nav_frame, text="← Неверно", command=self.mark_incorrect)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(self.nav_frame, text="Верно →", command=self.mark_correct)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для статистики
        self.stats_frame = ttk.Frame(self.root)
        self.stats_frame.pack(pady=10)
        
        self.stats_label = ttk.Label(self.stats_frame, text="", font=('Arial', 12))
        self.stats_label.pack()
        
        # Фрейм для диапазона
        self.range_frame = ttk.Frame(self.root)
        self.range_frame.pack(pady=10)
        
        ttk.Label(self.range_frame, text="Диапазон:").pack(side=tk.LEFT)
        
        self.start_entry = ttk.Entry(self.range_frame, width=5)
        self.start_entry.pack(side=tk.LEFT)
        ttk.Label(self.range_frame, text="до").pack(side=tk.LEFT)
        
        self.end_entry = ttk.Entry(self.range_frame, width=5)
        self.end_entry.pack(side=tk.LEFT)
        
        self.apply_range_btn = ttk.Button(self.range_frame, text="Применить", command=self.apply_range)
        self.apply_range_btn.pack(side=tk.LEFT, padx=5)
        
        # Привязка клавиш
        self.root.bind('<Left>', lambda e: self.mark_incorrect())
        self.root.bind('<Right>', lambda e: self.mark_correct())
        
    def show_current_item(self):
        if not self.image_files:
            return
            
        current_file = self.image_files[self.current_index]
        
        # Показ изображения
        try:
            img = Image.open("cropped_images/" + current_file)
            img.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            self.image_label.config(text=f"Ошибка загрузки изображения: {e}")
        
        # Показ текста OCR
        self.ocr_text.config(state=tk.NORMAL)
        self.ocr_text.delete(1.0, tk.END)
        self.ocr_text.insert(tk.END, self.data[current_file])
        self.ocr_text.config(state=tk.DISABLED)
        
        # Обновление статистики
        self.update_stats()
        
        # Обновление заголовка окна
        self.root.title(f"OCR Validator - {self.current_index + 1}/{self.total_items}")
        
    def mark_correct(self):
        if not self.image_files:
            return
            
        current_file = self.image_files[self.current_index]
        self.results[current_file] = "correct"
        self.correct += 1
        self.next_item()
        
    def mark_incorrect(self):
        if not self.image_files:
            return
            
        current_file = self.image_files[self.current_index]
        self.results[current_file] = "incorrect"
        self.incorrect += 1
        self.next_item()
        
    def next_item(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_current_item()
        else:
            messagebox.showinfo("Завершено", "Проверка всех элементов завершена!")
            self.save_results()
            
    def update_stats(self):
        self.stats_label.config(text=f"Верно: {self.correct} | Неверно: {self.incorrect}")
        
    def apply_range(self):
        try:
            start = int(self.start_entry.get()) - 1
            end = int(self.end_entry.get()) - 1
            
            if start < 0 or end >= len(self.image_files) or start > end:
                messagebox.showerror("Ошибка", "Некорректный диапазон")
                return
                
            self.image_files = self.image_files[start:end+1]
            self.total_items = len(self.image_files)
            self.current_index = 0
            self.correct = 0
            self.incorrect = 0
            self.results = {}
            self.show_current_item()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные номера")
            
    def save_results(self):
        # Вы можете добавить здесь сохранение результатов в файл
        print("Результаты проверки:")
        print(f"Всего: {self.correct + self.incorrect}")
        print(f"Верно: {self.correct}")
        print(f"Неверно: {self.incorrect}")
        print("\nДетали:")
        for file, result in self.results.items():
            print(f"{file}: {result}")

def main():
    root = tk.Tk()
    
    json_path = "yandex_ocr_data.json"
    
    if not os.path.exists(json_path):
        messagebox.showerror("Ошибка", f"Файл {json_path} не найден!")
        return
        
    app = OCRValidator(root, json_path)
    root.mainloop()

if __name__ == "__main__":
    main()
