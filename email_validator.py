import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
from verify_email import verify_email  

# проверка файла
def check_emails(file_path, progress_var, tree):
    try:
        # Чтение файла
        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, on_bad_lines='skip')
            except pd.errors.ParserError:
                df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
        elif file_path.endswith('.txt'):
            df = pd.read_csv(file_path, header=None, names=['email'], on_bad_lines='skip')
        else:
            messagebox.showerror("Ошибка", "Поддерживаются только .csv или .txt файлы")
            return

        if 'email' not in df.columns:
            df['email'] = df.iloc[:, 0]

        total = len(df)
        if total == 0:
            messagebox.showerror("Ошибка", "Файл пуст или нет корректных email")
            return

        # чистим таблицы
        for item in tree.get_children():
            tree.delete(item)

        results = []

        # Проверка email 
        for i, email in enumerate(df['email'], start=1):
            email_str = str(email).strip()
            print(f"Checking: '{email_str}'")  # Отладка

            try:
                is_valid = verify_email(email_str)
                print(f"Result: {is_valid}")  # Отладка
                status = "Valid" if is_valid else "Invalid"
            except Exception as e:
                print(f"Error: {e}")  # Отладка
                status = "Invalid"

            results.append(status)
            tag = "valid" if status == "Valid" else "invalid"
            tree.insert("", "end", values=(email_str, status), tags=(tag,))

            # обновляем прогрессбар
            progress_var.set(int(i / total * 100))
            root.update_idletasks()

        # сейвим результат в CSV через пандас
        df['status'] = results
        output_path = file_path.rsplit('.', 1)[0] + '_checked.csv'
        df.to_csv(output_path, index=False)
        progress_var.set(100)
        messagebox.showinfo("Готово!", f"Проверка завершена!\nРезультат сохранён в:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# выбор файла
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV/TXT files", "*.csv *.txt")])
    if file_path:
        check_emails(file_path, progress_var, tree)  # Без потоков для отладки


# интерфейс 
root = tk.Tk()
root.title("Email Validator")
root.geometry("700x500")
root.resizable(False, False)

label = tk.Label(root, text="Выберите файл с email адресами (.csv или .txt)", font=("Arial", 12))
label.pack(pady=10)

button = tk.Button(root, text="Загрузить файл", command=open_file, font=("Arial", 12), width=25, bg="#4CAF50", fg="white")
button.pack(pady=5)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=650, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

# Таблица для отображения email и статусов
columns = ("email", "status")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.heading("email", text="Email")
tree.heading("status", text="Статус")
tree.column("email", width=450)
tree.column("status", width=100, anchor="center")
tree.pack(pady=10)

# Цветовые теги
tree.tag_configure("valid", background="#d4edda")
tree.tag_configure("invalid", background="#f8d7da")

note = tk.Label(root, text="В файле должна быть хотя бы одна колонка с email", font=("Arial", 9), fg="gray")
note.pack(pady=5)

root.mainloop()
