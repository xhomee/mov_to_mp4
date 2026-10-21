import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import platform


class MovToMp4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MOV to MP4 Converter - Без втрати якості")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # Визначаємо операційну систему
        self.is_windows = platform.system() == "Windows"

        # Змінні
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.is_converting = False

        # Встановлюємо стиль для Windows
        self.setup_styles()

        # Створюємо інтерфейс
        self.create_widgets()

        # Перевірка наявності ffmpeg
        self.check_ffmpeg()

    def setup_styles(self):
        """Налаштування стилів для кращого відображення на Windows"""
        style = ttk.Style()

        # Вибираємо тему залежно від ОС
        if self.is_windows:
            try:
                style.theme_use('vista')
            except:
                style.theme_use('default')
        else:
            style.theme_use('clam')

    def create_widgets(self):
        """Створення всіх віджетів інтерфейсу"""
        # Головний контейнер
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        header_frame = tk.Frame(main_container, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame,
                               text="MOV → MP4 Конвертор",
                               font=('Arial', 18, 'bold'),
                               bg='#2c3e50',
                               fg='white')
        title_label.pack(expand=True)

        # Основна область
        content_frame = tk.Frame(main_container, bg='#f0f0f0', padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Секція вибору файлів
        files_frame = tk.LabelFrame(content_frame,
                                    text=" Файли ",
                                    font=('Arial', 10, 'bold'),
                                    bg='#f0f0f0',
                                    padx=15, pady=10)
        files_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        content_frame.grid_columnconfigure(0, weight=1)

        # Вхідний файл
        tk.Label(files_frame, text="Вхідний файл (MOV):",
                 bg='#f0f0f0', font=('Arial', 9)).grid(row=0, column=0,
                                                       sticky=tk.W, pady=5)

        input_frame = tk.Frame(files_frame, bg='#f0f0f0')
        input_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)

        input_entry = tk.Entry(input_frame,
                               textvariable=self.input_file,
                               font=('Arial', 9),
                               width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(input_frame,
                  text="📁 Вибрати",
                  command=self.select_input_file,
                  font=('Arial', 9),
                  bg='#3498db',
                  fg='white',
                  padx=15,
                  cursor='hand2').pack(side=tk.LEFT, padx=(10, 0))

        # Вихідний файл
        tk.Label(files_frame, text="Вихідний файл (MP4):",
                 bg='#f0f0f0', font=('Arial', 9)).grid(row=2, column=0,
                                                       sticky=tk.W, pady=5)

        output_frame = tk.Frame(files_frame, bg='#f0f0f0')
        output_frame.grid(row=3, column=0, sticky='ew')

        output_entry = tk.Entry(output_frame,
                                textvariable=self.output_file,
                                font=('Arial', 9),
                                width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(output_frame,
                  text="💾 Зберегти як",
                  command=self.select_output_file,
                  font=('Arial', 9),
                  bg='#3498db',
                  fg='white',
                  padx=15,
                  cursor='hand2').pack(side=tk.LEFT, padx=(10, 0))

        # Параметри конвертації
        params_frame = tk.LabelFrame(content_frame,
                                     text=" Параметри конвертації ",
                                     font=('Arial', 10, 'bold'),
                                     bg='#f0f0f0',
                                     padx=15, pady=10)
        params_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        self.codec_var = tk.StringVar(value="copy")

        # Радіокнопки для вибору режиму
        tk.Radiobutton(params_frame,
                       text="⚡ Швидке копіювання (без втрат якості, без перекодування)",
                       variable=self.codec_var,
                       value="copy",
                       bg='#f0f0f0',
                       font=('Arial', 9),
                       cursor='hand2').pack(anchor=tk.W, pady=3)

        tk.Radiobutton(params_frame,
                       text="🎬 H.264 (високоякісне перекодування, універсальна сумісність)",
                       variable=self.codec_var,
                       value="h264",
                       bg='#f0f0f0',
                       font=('Arial', 9),
                       cursor='hand2').pack(anchor=tk.W, pady=3)

        tk.Radiobutton(params_frame,
                       text="🎯 H.265/HEVC (найкраще стиснення, менший розмір)",
                       variable=self.codec_var,
                       value="h265",
                       bg='#f0f0f0',
                       font=('Arial', 9),
                       cursor='hand2').pack(anchor=tk.W, pady=3)

        # Прогрес бар
        self.progress = ttk.Progressbar(content_frame,
                                        mode='indeterminate',
                                        length=400)
        self.progress.grid(row=2, column=0, sticky='ew', pady=(0, 10))

        # Статус
        self.status_label = tk.Label(content_frame,
                                     text="✅ Готовий до конвертації",
                                     font=('Arial', 10),
                                     bg='#f0f0f0',
                                     fg='#27ae60')
        self.status_label.grid(row=3, column=0, pady=5)

        # ГОЛОВНА КНОПКА КОНВЕРТАЦІЇ
        self.convert_btn = tk.Button(content_frame,
                                     text="🚀 КОНВЕРТУВАТИ",
                                     command=self.start_conversion,
                                     font=('Arial', 14, 'bold'),
                                     bg='#27ae60',
                                     fg='white',
                                     width=25,
                                     height=2,
                                     cursor='hand2',
                                     relief=tk.RAISED,
                                     bd=3)
        self.convert_btn.grid(row=4, column=0, pady=(10, 0))

        # Ефект наведення для кнопки
        def on_enter(e):
            if not self.is_converting:
                self.convert_btn.config(bg='#229954')

        def on_leave(e):
            if not self.is_converting:
                self.convert_btn.config(bg='#27ae60')

        self.convert_btn.bind('<Enter>', on_enter)
        self.convert_btn.bind('<Leave>', on_leave)

    def check_ffmpeg(self):
        """Перевірка наявності ffmpeg в системі"""
        try:
            # Для Windows додаємо .exe
            ffmpeg_cmd = 'ffmpeg.exe' if self.is_windows else 'ffmpeg'

            # Спробуємо запустити ffmpeg
            startupinfo = None
            if self.is_windows:
                # Приховуємо консольне вікно на Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            subprocess.run([ffmpeg_cmd, '-version'],
                           capture_output=True,
                           check=True,
                           startupinfo=startupinfo)

        except (subprocess.CalledProcessError, FileNotFoundError):
            response = messagebox.askyesno(
                "FFmpeg не знайдено",
                "FFmpeg не знайдено в системі!\n\n"
                "Для роботи програми необхідно встановити FFmpeg.\n\n"
                "Для Windows:\n"
                "1. Завантажте FFmpeg з: ffmpeg.org/download.html\n"
                "2. Розпакуйте архів\n"
                "3. Додайте папку 'bin' до змінної середовища PATH\n"
                "АБО\n"
                "Покладіть ffmpeg.exe в папку з цією програмою\n\n"
                "Бажаєте відкрити сторінку завантаження?"
            )

            if response:
                import webbrowser
                webbrowser.open('https://www.gyan.dev/ffmpeg/builds/')

            self.status_label.config(text="⚠️ FFmpeg не встановлено", fg='#e74c3c')
            self.convert_btn.config(state='disabled', bg='#95a5a6')

    def select_input_file(self):
        """Вибір вхідного MOV файлу"""
        filename = filedialog.askopenfilename(
            title="Виберіть MOV файл",
            filetypes=[
                ("MOV файли", "*.mov"),
                ("Всі відео", "*.mov;*.MOV;*.mp4;*.MP4;*.avi;*.mkv"),
                ("Всі файли", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            # Автоматично пропонуємо ім'я для вихідного файлу
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_converted.mp4")

    def select_output_file(self):
        """Вибір місця збереження MP4 файлу"""
        filename = filedialog.asksaveasfilename(
            title="Зберегти MP4 файл як",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 файли", "*.mp4"),
                ("Всі файли", "*.*")
            ]
        )
        if filename:
            self.output_file.set(filename)

    def start_conversion(self):
        """Початок конвертації"""
        if not self.input_file.get():
            messagebox.showwarning("Увага", "Будь ласка, виберіть вхідний MOV файл!")
            return

        if not self.output_file.get():
            messagebox.showwarning("Увага", "Будь ласка, вкажіть ім'я вихідного файлу!")
            return

        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Помилка", "Вхідний файл не знайдено!")
            return

        # Перевірка, чи не однакові файли
        if self.input_file.get() == self.output_file.get():
            messagebox.showerror("Помилка", "Вхідний та вихідний файли не можуть бути однаковими!")
            return

        # Запускаємо конвертацію в окремому потоці
        self.is_converting = True
        self.convert_btn.config(state='disabled',
                                text="⏳ КОНВЕРТАЦІЯ...",
                                bg='#95a5a6')
        self.progress.start(10)
        self.status_label.config(text="🔄 Йде конвертація...", fg='#3498db')

        thread = threading.Thread(target=self.convert_video)
        thread.daemon = True
        thread.start()

    def convert_video(self):
        """Процес конвертації відео"""
        try:
            input_path = self.input_file.get()
            output_path = self.output_file.get()
            codec = self.codec_var.get()

            # FFmpeg команда для Windows
            ffmpeg_cmd = 'ffmpeg.exe' if self.is_windows else 'ffmpeg'

            # Спробуємо знайти ffmpeg в папці з програмою
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_ffmpeg = os.path.join(script_dir, ffmpeg_cmd)

            if os.path.exists(local_ffmpeg):
                ffmpeg_cmd = local_ffmpeg

            # Формуємо команду ffmpeg
            if codec == "copy":
                # Копіювання без перекодування (найшвидше)
                cmd = [
                    ffmpeg_cmd, '-i', input_path,
                    '-c:v', 'copy',  # Копіюємо відео
                    '-c:a', 'copy',  # Копіюємо аудіо
                    '-movflags', 'faststart',  # Оптимізація для веб
                    '-y',  # Перезаписувати вихідний файл
                    output_path
                ]
            elif codec == "h264":
                # H.264 з високою якістю
                cmd = [
                    ffmpeg_cmd, '-i', input_path,
                    '-c:v', 'libx264',  # H.264 кодек
                    '-preset', 'slow',  # Повільне кодування для кращої якості
                    '-crf', '18',  # Високоякісне кодування (0-51, менше = краще)
                    '-c:a', 'aac',  # AAC аудіо
                    '-b:a', '320k',  # Високий бітрейт аудіо
                    '-movflags', 'faststart',
                    '-y',
                    output_path
                ]
            else:  # h265
                # H.265/HEVC з високою якістю
                cmd = [
                    ffmpeg_cmd, '-i', input_path,
                    '-c:v', 'libx265',  # H.265 кодек
                    '-preset', 'slow',
                    '-crf', '20',  # Трохи вище CRF для H.265
                    '-c:a', 'aac',
                    '-b:a', '320k',
                    '-movflags', 'faststart',
                    '-tag:v', 'hvc1',  # Для кращої сумісності з Apple
                    '-y',
                    output_path
                ]

            # Налаштування для Windows
            startupinfo = None
            if self.is_windows:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # Виконуємо конвертацію
            process = subprocess.run(cmd,
                                     capture_output=True,
                                     text=True,
                                     startupinfo=startupinfo)

            # Перевіряємо результат
            if process.returncode == 0:
                self.root.after(0, self.conversion_success)
            else:
                error_msg = process.stderr if process.stderr else "Невідома помилка"
                self.root.after(0, lambda: self.conversion_error(error_msg))

        except Exception as e:
            self.root.after(0, lambda: self.conversion_error(str(e)))

    def conversion_success(self):
        """Успішне завершення конвертації"""
        self.progress.stop()
        self.is_converting = False
        self.convert_btn.config(state='normal',
                                text="🚀 КОНВЕРТУВАТИ",
                                bg='#27ae60')
        self.status_label.config(text="✅ Конвертацію завершено успішно!",
                                 fg='#27ae60')

        # Показуємо розмір файлів
        try:
            input_size = os.path.getsize(self.input_file.get()) / (1024 * 1024)
            output_size = os.path.getsize(self.output_file.get()) / (1024 * 1024)

            result_msg = f"✅ Конвертацію завершено!\n\n"
            result_msg += f"📁 Вхідний файл: {input_size:.2f} MB\n"
            result_msg += f"📁 Вихідний файл: {output_size:.2f} MB\n"

            if input_size > output_size:
                result_msg += f"📉 Економія: {(input_size - output_size):.2f} MB\n\n"
            else:
                result_msg += f"📈 Збільшення: {(output_size - input_size):.2f} MB\n\n"

            result_msg += f"💾 Збережено:\n{self.output_file.get()}"

            messagebox.showinfo("Успіх", result_msg)
        except:
            messagebox.showinfo("Успіх", "Конвертацію завершено успішно!")

    def conversion_error(self, error_msg):
        """Помилка конвертації"""
        self.progress.stop()
        self.is_converting = False
        self.convert_btn.config(state='normal',
                                text="🚀 КОНВЕРТУВАТИ",
                                bg='#27ae60')
        self.status_label.config(text="❌ Помилка конвертації", fg='#e74c3c')

        # Обрізаємо повідомлення про помилку для Windows
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + "..."

        messagebox.showerror(
            "Помилка",
            f"Помилка при конвертації:\n\n{error_msg}\n\n"
            f"Перевірте:\n"
            f"• Чи встановлено FFmpeg\n"
            f"• Чи правильний формат вхідного файлу\n"
            f"• Чи достатньо місця на диску"
        )


def main():
    root = tk.Tk()

    # Центруємо вікно на екрані
    root.update_idletasks()
    width = 650
    height = 550
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    app = MovToMp4Converter(root)
    root.mainloop()


if __name__ == "__main__":
    main()