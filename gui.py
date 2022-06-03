from tkinter import *
from tkinter import ttk
from tkinter.ttk import Treeview
from tkinter.ttk import Combobox
from tkinter.ttk import Radiobutton
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import pymysql
import hashlib
from datetime import datetime
import pandas as pd
from random import randint
from xlsxwriter.workbook import Workbook
import time

app = Tk()


def check_num(phone):
    if len(phone) == 11:
        if phone[0] == '7':
            return True
        else:
            return False
    else:
        return False


def clear():
    for widget in app.winfo_children():
        widget.destroy()


def Authorization():
    font_header = ('Arial', 15)
    font_entry = ('Arial', 12)
    label_font = ('Arial', 11)
    base_padding = {'padx': 10, 'pady': 8}
    header_padding = {'padx': 10, 'pady': 12}

    def clicked():
        global rec
        username = usr.get()
        password = psw.get()
        print(username, password)
        rec = db.search_logins(username, password)

        if len(rec) != 0:
            clear()
            Main()
            messagebox.showinfo('Уведомление', 'Вы успешно вошли')
        else:
            messagebox.showinfo('Уведомление', 'Неверный логин или пароль')

    main_label = Label(app, text='Авторизация', font=font_header, justify=CENTER, **header_padding)
    main_label.pack()

    username_label = Label(app, text='Имя пользователя', font=label_font, **base_padding)
    username_label.pack()
    usr = StringVar()
    username_entry = Entry(app, bg='#fff', fg='#444', font=font_entry, textvariabl=usr)
    username_entry.pack()

    password_label = Label(app, text='Пароль', font=label_font, **base_padding)
    password_label.pack()
    psw = StringVar()
    password_entry = Entry(app, bg='#fff', fg='#444', font=font_entry, show='*', textvariabl=psw)
    password_entry.pack()

    send_btn = Button(app, text='Войти', command=clicked)
    send_btn.pack(**base_padding)


class Database:
    def __init__(self, user, password, db):
        self.conn = pymysql.connect(host='localhost',
                                    user=user,
                                    password=password,
                                    database=db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS pass_holders (Id text, FIO text, NUM_Phone text, TG_Nick text, Type text,Division text)")
        self.conn.commit()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS pass_logs (Date text, FIO text,Id text, Direction text)")
        self.conn.commit()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS authorization (FIO text, Login text, Password text, Type text)")
        self.conn.commit()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS type_of_pass_holders (Type text)")
        self.conn.commit()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS divisions (Division text, Type text)")
        self.conn.commit()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS time_inside (FIO text, Time_inside text, Time_in text, Time_out text)")
        self.conn.commit()

    def fetch(self, FIO=''):
        self.cur.execute(
            f"SELECT * FROM pass_holders WHERE FIO LIKE '%{FIO}%'")
        rows = self.cur.fetchall()
        return rows

    def fetch_FIO(self, Type, Division):
        self.cur.execute(f"SELECT FIO,Id FROM pass_holders WHERE Type='{Type}' and Division='{Division}'")
        rows = self.cur.fetchall()
        return rows

    def insert(self, FIO, NUM_Phone, TG_Nick, Type, Division):
        self.byte_name = bytearray(FIO + str(datetime.now())[-1] + str(randint(0, 1000000)), encoding='utf-8')
        self.id = hashlib.md5(self.byte_name).hexdigest()
        self.cur.execute(
            f"INSERT INTO pass_holders VALUES ('{self.id}', '{FIO}', '{NUM_Phone}', '{TG_Nick}', '{Type}','{Division}')")
        self.conn.commit()

    def remove(self, Id):
        self.cur.execute(f"DELETE FROM pass_holders WHERE Id='{Id}'")
        self.conn.commit()

    def update(self, Id, FIO, NUM_Phone, TG_Nick, Type):
        self.cur.execute(
            f"UPDATE pass_holders SET FIO = '{FIO}', NUM_Phone = '{NUM_Phone}', TG_Nick = '{TG_Nick}', Type = '{Type}' WHERE Id = '{Id}'")
        self.conn.commit()

    def insert_mark(self, Date, FIO, Id, Direction):
        self.cur.execute(f"INSERT INTO pass_logs VALUES ('{Date}', '{FIO}', '{Id}','{Direction}')")
        self.conn.commit()

    def search_logins(self, login, password):
        self.cur.execute(f"SELECT FIO,Type from authorization WHERE Login = '{login}' AND Password = '{password}'")
        return self.cur.fetchall()

    def fetch_mark(self):
        self.cur.execute(
            "SELECT Date,FIO,Direction FROM pass_logs")
        rows = self.cur.fetchall()
        return rows

    def __del__(self):
        self.conn.close()


db = Database('root', 'Slowpoke00', 'SKUD')


def Main():
    tab_control = ttk.Notebook(app)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)
    tab3 = ttk.Frame(tab_control)
    tab4 = ttk.Frame(tab_control)
    if rec[0][1] == 'Admin':
        tab_control.add(tab1, text='Владельцы пропусков')
    tab_control.add(tab2, text='Посещаемость')
    tab_control.add(tab3, text='Управление')
    tab_control.add(tab4, text='Авторизация')
    tab_control.pack(expand=1, fill='both')
    frame_search = Frame(tab1)
    frame_search.grid(row=0, column=0)
    frame_tree = Frame(tab2)
    frame_tree.grid(row=5, column=0, sticky=W, padx=20)
    frame_tree2 = Frame(tab2)
    frame_tree2.grid(row=5, column=0, sticky=W, padx=180)
    frame_control = Frame(tab3)
    frame_control.place(x=250, y=105)
    lbl = Label(frame_control, text='Закрыт')
    lbl.grid(column=0, row=0, sticky=E)

    def get_var_1(event):
        value = cb1_var.get()
        cb2_var.set(Types[value][0])
        combo2.config(values=Types[value])

    def get_var_2(event):
        value = cb1_mark_var.get()
        cb2_mark_var.set(Types[value][0])
        combo2_mark.config(values=Types[value])

    def file_open():
        try:
            filePath = askopenfilename(initialdir="/", title="Select file",
                                       filetypes=[('Excel Files', ['*.xls', '*.xlsx', '*.xlsm', '*.xlsb'])])
            wb = pd.read_excel(filePath)
            for index, row in wb.iterrows():
                byte_name = bytearray(row.FIO + str(datetime.now())[-1] + str(randint(0, 1000000)), encoding='utf-8')
                id = hashlib.md5(byte_name).hexdigest()
                if check_num(str(row.Phone)) == False:
                    messagebox.showerror('Ошибка', 'Неверный формат номера телефона загрузка данных прервана')
                    return
                db.cur.execute(
                    f"INSERT INTO pass_holders (Id,FIO,NUM_Phone,TG_Nick,Type,Division) values('{id}','{row.FIO}','{row.Phone}','{row.TG}','{row.Type}','{row.Division}')")
            db.conn.commit()
            populate_list()
        except:
            messagebox.showerror('Ошибка', 'Что-то пошло не так')

    def populate_list(FIO=''):
        for i in holders_tree_view.get_children():
            holders_tree_view.delete(i)
        for row in db.fetch(FIO):
            holders_tree_view.insert('', 'end', values=row)

    def populate_list2():
        for i in mark_tree_view.get_children():
            mark_tree_view.delete(i)
        for row in db.fetch_FIO(combo_mark.get(), combo2_mark.get()):
            mark_tree_view.insert('', 'end', values=row)

    def populate_list3():
        for i in Write_tree_view.get_children():
            Write_tree_view.delete(i)
        for row in db.fetch_mark():
            Write_tree_view.insert('', 'end', values=row)

    def add_holder():
        if Phone_text.get() == '' or FIO_text.get() == '':
            messagebox.showerror('Ошибка', 'Заполните все поля')
            return
        if check_num(Phone_text.get()) == False:
            messagebox.showerror('Ошибка', 'Неверный формат номера телефона')
            return

        db.insert(FIO_text.get(), Phone_text.get(),
                  TG_text.get(), combo.get(), combo2.get())
        clear_text()
        populate_list()

    def select_holder(event):
        try:
            global selected_item
            index = holders_tree_view.selection()[0]
            selected_item = holders_tree_view.item(index)['values']
            FIO_entry.delete(0, END)
            FIO_entry.insert(END, selected_item[1])
            Phone_entry.delete(0, END)
            Phone_entry.insert(END, selected_item[2])
            TG_entry.delete(0, END)
            TG_entry.insert(END, selected_item[3])
            combo.delete(0, END)
            combo.insert(END, selected_item[4])
        except IndexError:
            pass

    def select_FIO(event):
        try:
            id = mark_tree_view.selection()[0]
            selected_item = mark_tree_view.item(id)['values']
            FIO = selected_item[0]
            global Id_Mark
            Id_Mark = selected_item[1]
            FIO_mark_entry.delete(0, END)
            FIO_mark_entry.insert(END, FIO)
        except IndexError:
            pass

    def remove_holder():
        try:
            db.remove(selected_item[0])
            clear_text()
            populate_list()
        except:
            messagebox.showerror('Ошибка', 'Что-то пошло не так')

    def update_holder():
        try:
            db.update(selected_item[0], FIO_text.get(), Phone_text.get(),
                      TG_text.get(), combo.get())
            populate_list()

        except:
            messagebox.showerror('Ошибка', 'Что-то пошло не так')

    def clear_text():
        Phone_entry.delete(0, END)
        FIO_entry.delete(0, END)
        TG_entry.delete(0, END)

    def search_FIO():
        FIO = FIO_search.get()
        populate_list(FIO)

    lbl_search = Label(frame_search, text='Поиск по ФИО',
                       font=('bold', 12), pady=20)
    lbl_search.grid(row=0, column=0, sticky=W)
    FIO_search = StringVar()
    FIO_search_entry = Entry(frame_search, textvariable=FIO_search)
    FIO_search_entry.grid(row=0, column=1)

    frame_fields = Frame(tab1)
    frame_fields.grid(row=1, column=0)
    # FIO
    FIO_text = StringVar()
    FIO_label = Label(frame_fields, text='ФИО', font=('bold', 12))
    FIO_label.grid(row=0, column=0, sticky=E)
    FIO_entry = Entry(frame_fields, textvariable=FIO_text)
    FIO_entry.grid(row=0, column=1, sticky=W)
    # Phone
    Phone_text = StringVar()
    Phone_label = Label(frame_fields, text='Телефон', font=('bold', 12))
    Phone_label.grid(row=0, column=2, sticky=E)
    Phone_entry = Entry(frame_fields, textvariable=Phone_text)
    Phone_entry.grid(row=0, column=3, sticky=W)
    # TG
    TG_text = StringVar()
    TG_label = Label(frame_fields, text='Телеграм', font=('bold', 12))
    TG_label.grid(row=1, column=0, sticky=E)
    TG_entry = Entry(frame_fields, textvariable=TG_text)
    TG_entry.grid(row=1, column=1, sticky=W)
    # Type
    Type_label = Label(frame_fields, text='Тип', font=('bold', 12), pady=20)
    Type_label.grid(row=1, column=2, sticky=E)

    Division_label = Label(frame_fields, text='Подразделение', font=('bold', 12), pady=0)
    Division_label.grid(row=2, column=2, sticky=E)

    db.cur.execute("Select Type from type_of_pass_holders")
    val = []
    Types = {}
    for i in db.cur.fetchall():
        info = i[0]
        db.cur.execute(f"Select Division from divisions WHERE Type='{info}'")
        info2 = []
        for j in db.cur.fetchall():
            print(j)
            info2.append(j[0])
        Types[info] = info2
        val.append(info)
    print(val)
    Divisions = []
    for i in Types:
        Divisions += Types.get(i)
    cb1_values = list(Types.keys())
    cb1_var = StringVar()
    cb1_var.set(cb1_values[0])
    combo = Combobox(frame_fields, state="readonly", values=list(Types.keys()), textvariable=cb1_var)
    combo.grid(row=1, column=3, sticky=NE, padx=0, pady=20)

    combo.bind('<<ComboboxSelected>>', get_var_1)

    cb2_var = StringVar()
    cb2_var.set(Types[cb1_values[0]][0])
    combo2 = Combobox(frame_fields, state="readonly", values=Types[cb1_values[0]], textvariable=cb2_var)
    combo2.grid(row=2, column=3, sticky=SE, padx=0, pady=0)

    frame_holders = Frame(tab1)
    frame_holders.grid(row=4, column=0, columnspan=4, rowspan=6, pady=20, padx=0)

    columns = ['id', 'ФИО', 'Телефон', 'Телеграм', 'Тип', 'Подразделение']
    holders_tree_view = Treeview(frame_holders, columns=columns, show="headings")
    holders_tree_view.column("id", width=30)
    for col in columns[1:]:
        holders_tree_view.column(col, width=120)
        holders_tree_view.heading(col, text=col)
    holders_tree_view.bind('<<TreeviewSelect>>', select_holder)
    holders_tree_view.pack(side="left", fill="y")
    scrollbar = Scrollbar(frame_holders, orient='vertical')
    scrollbar.configure(command=holders_tree_view.yview)
    scrollbar.pack(side="right", fill="y")
    holders_tree_view.config(yscrollcommand=scrollbar.set)

    frame_btns = Frame(tab1)
    frame_btns.grid(row=3, column=0)

    add_btn = Button(frame_btns, text='Добавить', width=12, command=add_holder)
    add_btn.grid(row=0, column=0, pady=20)

    remove_btn = Button(frame_btns, text='Удалить',
                        width=12, command=remove_holder)
    remove_btn.grid(row=0, column=1)

    update_btn = Button(frame_btns, text='Править',
                        width=12, command=update_holder)
    update_btn.grid(row=0, column=2)

    clear_btn = Button(frame_btns, text='Очистить',
                       width=12, command=clear_text)
    clear_btn.grid(row=0, column=3)

    open_btn = Button(frame_fields, text='Импорт из файла',
                      width=20, command=file_open)
    open_btn.grid(row=2, column=1, sticky=SE)

    search_btn = Button(frame_search, text='Поиск',
                        width=12, command=search_FIO)
    search_btn.grid(row=0, column=2)

    def Quit():
        clear()
        Authorization()

    def clicked():
        Value = selected.get()
        if Value == 1:
            lbl.configure(text='Открыт')
        elif Value == 2:
            lbl.configure(text='Закрыт')

    def calculate_time(In, Out):
        time1 = datetime.strptime(In, "%H:%M:%S %Y-%m-%d")
        time2 = datetime.strptime(Out, "%H:%M:%S %Y-%m-%d")
        return str(time2 - time1)

    def write_mark():
        if DIR_mark_entry.get() == '' or FIO_mark_entry.get() == '':
            messagebox.showerror('Ошибка', 'Заполните все поля')
            return
        time = str(datetime.now().time())[:8] + ' ' + str(datetime.now().date())
        db.insert_mark(time, FIO_mark_text.get(), Id_Mark, DIR_mark_entry.get())
        if DIR_mark_entry.get() == "Вышел":
            db.cur.execute(f"SELECT Date FROM pass_logs WHERE id='{Id_Mark}' and Direction='Вошел'")
            inside = db.cur.fetchall()
            if len(inside) != 0:
                db.cur.execute(f"SELECT Date FROM pass_logs WHERE id='{Id_Mark}' and Direction='Вышел'")
                outside = db.cur.fetchall()
                time1 = inside[-1][0]
                time2 = outside[-1][0]
                all_time = calculate_time(time1, time2)
                db.cur.execute(
                    f"INSERT INTO time_inside VALUES('{FIO_mark_text.get()}','{all_time}','{time1}','{time2}')")
                db.conn.commit()
        DIR_mark_entry.delete(0, END)
        FIO_mark_entry.delete(0, END)
        populate_list3()

    def export():
        workbook = Workbook('logs.xlsx')
        worksheet = workbook.add_worksheet()
        db.cur.execute('select * from pass_logs')
        header = [row[0] for row in db.cur.description]
        rows = db.cur.fetchall()
        row_index = 0
        column_index = 0
        for column_name in header:
            worksheet.write(row_index, column_index, column_name)
            column_index += 1
        row_index += 1
        for row in rows:
            column_index = 0
            for column in row:
                worksheet.write(row_index, column_index, column)
                column_index += 1
            row_index += 1
        workbook.close()

    selected = IntVar()
    rad1 = Radiobutton(frame_control, text='Открыть', value=1, variable=selected)
    rad2 = Radiobutton(frame_control, text='Закрыть', value=2, variable=selected)
    btn_c = Button(frame_control, text="Выбрать", command=clicked)
    rad1.grid(column=0, row=1)
    rad2.grid(column=1, row=1)
    btn_c.grid(column=0, row=2, sticky=E)

    Frame_mark = Frame(tab2)
    Frame_mark.grid(row=0, column=0, padx=0, pady=10, sticky=W)
    Type_label_mark = Label(Frame_mark, text='Тип:', font=('bold', 12))
    Type_label_mark.grid(row=0, column=0, sticky=NW, padx=0, pady=0)

    Division_label_mark = Label(Frame_mark, text='Подразделение:', font=('bold', 12))
    Division_label_mark.grid(row=0, column=1, sticky=NW, padx=0, pady=0)

    cb1_mark_values = list(Types.keys())
    cb1_mark_var = StringVar()
    cb1_mark_var.set(cb1_mark_values[0])
    combo_mark = Combobox(Frame_mark, state="readonly", values=list(Types.keys()), textvariable=cb1_mark_var)
    combo_mark.grid(row=1, column=0, sticky=NW, padx=0, pady=0)

    combo_mark.bind('<<ComboboxSelected>>', get_var_2)

    cb2_mark_var = StringVar()
    cb2_mark_var.set(Types[cb1_mark_values[0]][0])
    combo2_mark = Combobox(Frame_mark, state="readonly", values=Types[cb1_mark_values[0]], textvariable=cb2_mark_var)
    combo2_mark.grid(row=1, column=1, sticky=NW, padx=0, pady=0)

    show = Button(Frame_mark, text="Показать", command=populate_list2)
    show.grid(row=1, column=2, sticky=NW, padx=0, pady=0)

    # FIO
    FIO_mark_text = StringVar()
    FIO_mark_label = Label(Frame_mark, text='ФИО', font=('bold', 12))
    FIO_mark_label.grid(row=3, column=0, sticky=W)
    FIO_mark_entry = Entry(Frame_mark, textvariable=FIO_mark_text)
    FIO_mark_entry.grid(row=3, column=0, sticky=E, padx=50)
    # DIR
    DIR_mark_label = Label(Frame_mark, text='Направление', font=('bold', 12))
    DIR_mark_label.grid(row=3, column=1, sticky=W)
    DIR_mark_entry = Combobox(Frame_mark, state="readonly")
    DIR_mark_entry['values'] = ("Вошел", "Вышел")
    DIR_mark_entry.grid(row=3, column=1, sticky=W)
    DIR_mark_entry.current(1)

    btn_mark = Button(Frame_mark, text="Записать", command=write_mark)
    btn_mark.grid(row=3, column=2)
    exp_btn = Button(Frame_mark, text='Экспортировать данные',
                     width=20, command=export)
    exp_btn.grid(row=5, column=1, sticky=SW, pady=10)
    columns = ['ФИО']
    mark_tree_view = Treeview(frame_tree, columns=columns, show="headings")
    for col in columns:
        mark_tree_view.column(col, width=120)
        mark_tree_view.heading(col, text=col)
    mark_tree_view.bind('<<TreeviewSelect>>', select_FIO)
    mark_tree_view.pack(side="left", fill="y")
    scrollbar_mark = Scrollbar(frame_tree, orient='vertical')
    scrollbar_mark.configure(command=mark_tree_view.yview)
    scrollbar_mark.pack(side="right", fill="y")
    mark_tree_view.config(yscrollcommand=scrollbar_mark.set)

    columns = ['Дата', 'ФИО', 'Направление']
    Write_tree_view = Treeview(frame_tree2, columns=columns, show="headings")
    for col in columns:
        Write_tree_view.column(col, width=120)
        Write_tree_view.heading(col, text=col)
    Write_tree_view.pack(side="left", fill="y")
    scrollbar_Write = Scrollbar(frame_tree2, orient='vertical')
    scrollbar_Write.configure(command=Write_tree_view.yview)
    scrollbar_Write.pack(side="right", fill="y")
    Write_tree_view.config(yscrollcommand=scrollbar_Write.set)

    Frame_auth = Frame(tab4)
    Frame_auth.grid(row=0, column=0)
    Label_FIO = Label(Frame_auth, text=f'Здравствуйте, {rec[0][0]}')
    Label_FIO.grid(row=0, column=0)
    if rec[0][1] == 'Admin':
        Label_Status = Label(Frame_auth, text='Ваш статус: Администратор')
    elif rec[0][1] == 'Guard':
        Label_Status = Label(Frame_auth, text='Ваш статус: Охранник')
    Label_Status.grid(row=1, column=0)
    quit_btn = Button(Frame_auth, text='Выйти', width=12, command=Quit)
    quit_btn.grid(row=2, column=0, pady=20)
    populate_list()
    populate_list2()
    populate_list3()


Authorization()

app.title('СКУД')
app.geometry('700x550')
app.resizable(width=False, height=False)

while True:
    app.update_idletasks()
    app.update()
    time.sleep(0.01)
