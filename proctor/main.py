from tkinter import messagebox, END
import customtkinter
import tkinter as Tk
import sqlite3
import json
import shutil
import pandas as pd
import os
import subprocess
import datetime as dt
import cv2
import sys

# assets
from assets.components.asset import Asset
from assets.components.text import Text
from assets.components.attributes import Attributes

# initialize classes
asset = Asset()
text = Text()
attributes = Attributes()

# constant paths
CONFIG = './assets/config'
DB = './assets/db'
ASSETS = './assets'

# global variables
cap = cv2.VideoCapture(0)


class Controller(Tk.Tk):
    def __init__(self, *args, **kwargs):  # * and ** as param validation
        Tk.Tk.__init__(self, *args, **kwargs)
        # canvas architecture
        container = Tk.Frame(self)
        container.pack(side='bottom', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=5)
        container.grid_columnconfigure(0, weight=5)

        self.frames = {}  # array frames

        # iterate over classes and store on dictionary
        for page in (Front, SignUp, SignIn, Section, Grades):
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky='nsew')

            self.show_frame(Front)

    def show_frame(self, next_frame):
        frame = self.frames[next_frame]
        frame.tkraise()  # holds frames in place


class Front(Tk.Frame):
    def __init__(self, parent, controller):
        Tk.Frame.__init__(self, parent, width=100, height=100)
        LEFT_BANNER_WIDTH = 40

        # left section
        description = Tk.Label(
            self,
            text=text.front_description_1,
            justify='left',
            bg=asset.bg_color,
            fg=asset.font_color,
            font=asset.font,
            width=LEFT_BANNER_WIDTH
        )
        description.grid(row=0, column=0, padx=0, pady=0)

        description2 = Tk.Label(
            self,
            text=text.front_description_2,
            justify='left',
            bg=asset.bg_color,
            fg=asset.font_color,
            font=asset.font,
            width=LEFT_BANNER_WIDTH
        )
        description2.grid(row=1, column=0, padx=0, pady=0)
        description3 = Tk.Label(
            self,
            text=text.front_description_3,
            justify='left',
            bg=asset.bg_color,
            fg=asset.font_color,
            font=asset.font,
            width=LEFT_BANNER_WIDTH
        )
        description3.grid(row=2, column=0, padx=0, pady=0)
        description4 = Tk.Label(
            self,
            text=text.front_description_4,
            justify='left',
            bg=asset.bg_color,
            fg=asset.font_color,
            font=asset.font,
            width=LEFT_BANNER_WIDTH
        )
        description4.grid(row=3, column=0, padx=0, pady=0)

        # right section
        description3 = Tk.Label(
            self,
            text='Proctor AI',
            justify='center',
            font=asset.font_title,
            width=16
        )
        description3.grid(row=0, column=1, padx=0, pady=0)

        # navigation
        login_btn = customtkinter.CTkButton(
            self,
            text='Sign In',
            command=lambda: controller.show_frame(SignIn),
            font=asset.button
        )
        login_btn.grid(row=1, column=1, padx=50, pady=0)
        create_account_btn = customtkinter.CTkButton(
            self,
            text='Sign Up',
            command=lambda: controller.show_frame(SignUp),
            font=asset.button
        )
        create_account_btn.grid(row=2, column=1, padx=50, pady=0)


class SignUp(Tk.Frame):
    def __init__(self, parent, controller):
        Tk.Frame.__init__(self, parent)

        # navigation
        proceed_btn = customtkinter.CTkButton(
            self,
            text='Proceed',
            command=self.create_account,
            font=asset.button
        )
        proceed_btn.grid(row=6, column=2, padx=5, pady=10)

        confirm_btn = customtkinter.CTkButton(
            self,
            text='Return',
            command=lambda: controller.show_frame(Front),
            font=asset.button
        )
        confirm_btn.grid(row=7, column=2, padx=5, pady=10)

        # labels
        padding_label = Tk.Label(
            self,
            text=text.padding,
            justify='center'
        )
        padding_label.grid(row=6, column=0, padx=20, pady=10)

        create_account_label = Tk.Label(
            self,
            text='Sign Up',
            font=asset.font_title,
            justify='center'
        )
        create_account_label.grid(row=0, column=2, padx=20, pady=10)

        username = Tk.Label(self, text='Username: ', font=asset.font, justify='center')
        username.grid(row=1, column=1, padx=10, pady=10)

        password = Tk.Label(self, text='Password: ', font=asset.font, justify='center')
        password.grid(row=3, column=1, padx=10, pady=10)

        # entries
        self.username_entry = customtkinter.CTkEntry(self, placeholder_text='Your username', width=300)
        self.username_entry.grid(row=1, column=2, padx=10, pady=10)

        self.password_entry = customtkinter.CTkEntry(self, placeholder_text='*************', width=300, show='*')
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        self.controller = controller

    def create_account(self):
        if len(self.username_entry.get()) <= 5 and len(self.password_entry.get()) <= 5:
            messagebox.showinfo('Invalid Input', 'Username and password must be greater than 5 characters!')
            return

        try:
            if not os.path.exists('./yolov7-dev.db'):
                create_teacher_table = """
                    CREATE TABLE IF NOT EXISTS teacher (
                        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        UNIQUE (username)
                    );
                """

                create_section_table = """
                    CREATE TABLE IF NOT EXISTS section (
                        section_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        teacher_id INTEGER NOT NULL,
                        section_name TEXT NOT NULL,
                        UNIQUE (section_name),
                        FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
                            ON DELETE NO ACTION
                            ON UPDATE NO ACTION
                    );
                """

                create_student_table = """
                    CREATE TABLE IF NOT EXISTS student (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        section_id INTEGER NOT NULL,
                        tracker_id INTEGER NOT NULL,
                        grade REAL NOT NULL,
                        FOREIGN KEY (section_id) REFERENCES section(section_id)
                            ON DELETE NO ACTION
                            ON UPDATE NO ACTION
                    );
                """

                tables = [create_teacher_table, create_section_table, create_student_table]
                conn = sqlite3.connect('./yolov7-dev.db')
                for table in tables:
                    conn.execute(table)
                conn.close()

            # insert new login credentials
            conn = sqlite3.connect('./yolov7-dev.db')
            cursor = conn.cursor()

            teacher_signup = {
                'username': str(self.username_entry.get()),
                'password': str(self.password_entry.get()),
            }

            insert_teacher = f"""
                INSERT INTO teacher (username, password)
                VALUES (:username, :password);
            """

            cursor.execute(insert_teacher, teacher_signup)
            conn.commit()
            conn.close()

            messagebox.showinfo('Database Operations', 'Account successfully created!')
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.controller.show_frame(Front)
            return teacher_signup
        except sqlite3.OperationalError:
            messagebox.showinfo('Database Operations', 'Incorrect database status and inputs!')
        except sqlite3.IntegrityError:
            messagebox.showinfo('Database Operations', 'Choose a different username!')


class SignIn(Tk.Frame):
    def __init__(self, parent, controller):
        Tk.Frame.__init__(self, parent)

        # navigation
        confirm_btn = customtkinter.CTkButton(
            self,
            text='Proceed',
            command=self.login_account,
            font=asset.button
        )
        confirm_btn.grid(row=6, column=2, padx=5, pady=10)

        return_btn = customtkinter.CTkButton(
            self,
            text='Return',
            command=lambda: controller.show_frame(Front),
            font=asset.button
        )
        return_btn.grid(row=7, column=2, padx=5, pady=10)

        # labels
        padding_label = Tk.Label(self, text=text.padding, justify='center')
        padding_label.grid(row=6, column=0, padx=10, pady=10)

        label = Tk.Label(self, text='Sign In', font=asset.font_title)
        label.grid(row=0, column=2, padx=10, pady=10)

        username_label = Tk.Label(self, text='Username: ', font=asset.font, justify='left')
        username_label.grid(row=1, column=1, padx=20, pady=10)

        password_label = Tk.Label(self, text='Password: ', font=asset.font, justify='left')
        password_label.grid(row=3, column=1, padx=20, pady=10)

        # entries
        self.username_entry = customtkinter.CTkEntry(self, placeholder_text='Your username', width=300)
        self.username_entry.grid(row=1, column=2, padx=10, pady=10)

        self.password_entry = customtkinter.CTkEntry(self, placeholder_text='*************', width=300, show='*')
        self.password_entry.grid(row=3, column=2, padx=10, pady=10)

        self.controller = controller

    def login_account(self):
        if len(self.username_entry.get()) == 0 or len(self.password_entry.get()) == 0:
            messagebox.showinfo('Invalid Input', 'Please do not leave any fields empty!')
            return

        try:
            conn = sqlite3.connect('./yolov7-dev.db')
            cursor = conn.cursor()

            teacher_signin = {
                'username': str(self.username_entry.get()),
                'password': str(self.password_entry.get()),
            }

            select_credentials = """
                SELECT username, password
                FROM teacher
                WHERE username = :username AND password = :password;
            """
            cursor.execute(select_credentials, teacher_signin)
            result = cursor.fetchall()
            username, result = result[0]

            get_teacher_id = """
                SELECT teacher_id
                FROM teacher
                WHERE username = :username AND password = :password;
            """
            attributes.teacher_id = cursor.execute(get_teacher_id, teacher_signin).fetchall()[0][0]
            cursor.close()

            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.controller.show_frame(Section)
            return username, result
        except IndexError:
            messagebox.showinfo('Login Credentials', 'Incorrect username or password!')
        except sqlite3.OperationalError:
            messagebox.showinfo('Database Operations', 'Incorrect database status and inputs!')


class Section(Tk.Frame):
    def __init__(self, parent, controller):
        Tk.Frame.__init__(self, parent)

        # navigation
        confirm_btn = customtkinter.CTkButton(
            self,
            text='Proceed',
            command=self.set_section,
            font=asset.button
        )
        confirm_btn.grid(row=6, column=2, padx=5, pady=10)

        return_btn = customtkinter.CTkButton(
            self,
            text='Return',
            command=lambda: controller.show_frame(Front),
            font=asset.button
        )
        return_btn.grid(row=7, column=2, padx=5, pady=10)

        # labels
        padding_label = Tk.Label(self, text=text.padding, justify='center')
        padding_label.grid(row=6, column=0, padx=10, pady=10)

        label = Tk.Label(self, text='Section', font=asset.font_title)
        label.grid(row=0, column=2, padx=10, pady=10)

        section_label = Tk.Label(self, text='Section Name: ', font=asset.font, justify='left')
        section_label.grid(row=1, column=1, padx=20, pady=10)

        # entries
        self.section_entry = customtkinter.CTkEntry(self, placeholder_text='Enter section', width=300)
        self.section_entry.grid(row=1, column=2, padx=10, pady=10)

        self.controller = controller

    def set_section(self):
        if len(self.section_entry.get()) == 0:
            messagebox.showinfo('Invalid Input', 'Please do not leave any fields empty!')
            return

        section = {
            'section_name': str(self.section_entry.get()),
            'teacher_id': attributes.teacher_id
        }

        conn = sqlite3.connect('./yolov7-dev.db')
        cursor = conn.cursor()

        create_section = """
            INSERT INTO section (section_name, teacher_id)
            VALUES (:section_name, :teacher_id);
        """
        select_section = """
            SELECT section_name, teacher_id
            FROM section
            WHERE section_name = :section_name AND teacher_id = :teacher_id;
        """

        try:
            cursor.execute(create_section, section)
            conn.commit()

            cursor.execute(select_section, section)
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute(select_section, section)
            conn.commit()
        except sqlite3.OperationalError:
            messagebox.showinfo('Database Operations', f'Incorrect database status and inputs!')
        finally:
            get_section_id = """
                SELECT section_id
                FROM section
                WHERE section_name = :section_name;
            """
            if len(cursor.execute(get_section_id, {'section_name': str(self.section_entry.get())}).fetchall()) != 0:
                attributes.section_id = cursor.execute(
                    get_section_id,
                    {'section_name': str(self.section_entry.get())}
                ).fetchall()[0][0]
            conn.close()
            self.section_entry.delete(0, END)
            self.controller.show_frame(Grades)

            attributes.to_json()
            return section


class Grades(Tk.Frame):
    def __init__(self, parent, controller):
        Tk.Frame.__init__(self, parent)

        # navigation
        self.export_to_csv_btn = customtkinter.CTkButton(
            self,
            text='Export to CSV',
            command=self.export_to_csv,
            font=asset.button
        )
        self.export_to_csv_btn.grid(row=6, column=5, padx=5, pady=10)

        self.snapshot_btn = customtkinter.CTkButton(
            self,
            text='Take a snapshot',
            command=self.snapshot,
            font=asset.button
        )
        self.snapshot_btn.grid(row=7, column=5, padx=5, pady=10)

        self.return_btn = customtkinter.CTkButton(
            self,
            text='Return',
            command=lambda: controller.show_frame(Section),
            font=asset.button
        )
        self.return_btn.grid(row=8, column=5, padx=5, pady=10)

        # labels
        label = Tk.Label(self, text='Dashboard', font=asset.font_title)
        label.grid(row=1, column=5, padx=0, pady=10)

        padding_label = Tk.Label(self, text=text.padding, justify='center')
        padding_label.grid(row=8, column=0, padx=110, pady=70)

    def snapshot(self):
        if not cap.isOpened():
            messagebox.showinfo('Camera Operations', 'Allow permissions to open the camera!')
            return

        ct = dt.datetime.now()
        ret, frame = cap.read()

        if not ret:
            messagebox.showinfo('Camera Operations', 'Camera could not capture the frame!')
            return

        snapshots = len(os.listdir('./snapshots')) + 1
        snapshot_name = f'./snapshots/{ct.year}{ct.month}{ct.day}-{snapshots}.png'
        cv2.imwrite(snapshot_name, frame)

        cv2.imshow('Snapshot', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return f'{ct.year}{ct.month}{ct.day}.png'

    def export_to_csv(self):
        conn = sqlite3.connect('./yolov7-dev.db')
        student_grades = """
            SELECT student_id, section_id, tracker_id, grade
            FROM student
            WHERE section_id = :section_id; 
        """

        cursor = conn.cursor()
        cursor.execute(student_grades, {'section_id': attributes.section_id})
        conn.commit()

        ct = dt.datetime.now()
        df = pd.read_sql_query(student_grades, conn, params=[attributes.section_id])
        df.to_csv(f'./csv/{ct.year}{ct.month}{ct.day}.csv', index=False)
        messagebox.showinfo('Database Operations', 'CSV successfully created!')
        conn.close()


if __name__ == '__main__':
    customtkinter.set_default_color_theme('green')
    customtkinter.set_appearance_mode('light')

    root = Controller()
    root.title('proctor.ai')
    root.resizable(False, False)
    root.iconbitmap('assets/images/proctor.ico')
    Tk.mainloop()
