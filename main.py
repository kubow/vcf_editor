# -*- coding: utf-8 -*-

# Must do for compatibility win <> lnx
try:
    import Tkinter as tk
    import Tkinter.filedialog as dialog
    print('using big tkinter (linux way)')
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as dialog
    print('using small tkinter (windows way)')

# Contact list constructor
from Contact import ContactList


# Main logic and layout
class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active_sel = {
            'contact': '',
            'index': 0,
            'name': '',
            'number': '',
            'various': ''
        }
        self.await_load = True
        self.btn = {}
        self.curr_loc = ''
        self.form = {}
        self.mode = tk.IntVar(value=0)  # folder value active
        self.contacts_lib = ''
        
        # ===================== (Main Menu + controls)
        self.current_location = tk.Label(self.master, text='Location : {0}'.format(self.curr_loc))
        self.radio1 = tk.Radiobutton(self.master, text='Adresar', value=False, variable=self.mode, command=self.set_dir)
        self.radio2 = tk.Radiobutton(self.master, text='Soubor', value=True, variable=self.mode, command=self.set_file)
        
        self.current_location.grid(row=0, column=0, columnspan=3, sticky='w')
        self.radio1.grid(row=0, column=4)
        self.radio2.grid(row=0, column=5)
        
        # ===================== (Button Menu)
        self.btn['open'] = tk.Button(self.master, text='open', command=self.browse_dir)
        self.btn['expt'] = tk.Button(self.master, text='export', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save')  # editing not yet implemented
        self.btn['next'] = tk.Button(self.master, text='>', command=self.next)
        self.btn['exit'] = tk.Button(self.master, text='quit', command=self.quit)
        self.btn['open'].grid(row=1, column=0, pady=5, sticky='nsew')
        self.btn['expt'].grid(row=1, column=1, pady=5, sticky='nsew')
        self.btn['prev'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.btn['save'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.btn['next'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.btn['exit'].grid(row=1, column=5, pady=5, sticky='nsew')

        # ===================== (Contacts list)
        self.contacts_list = tk.Listbox(self.master, height=7)  # selectmode='SINGLE'
        self.contacts_list.bind('<<ListboxSelect>>', self.on_select)
        self.contacts_scroll = tk.Scrollbar(self.master, orient='vertical')
        
        self.contacts_list['yscrollcommand'] = self.contacts_scroll.set
        self.contacts_scroll['command'] = self.contacts_list.yview
        
        self.contacts_list.grid(row=2, column=0, rowspan=8, columnspan=2, sticky='wse', pady=(3, 3), padx=(3, 3))
        self.contacts_scroll.grid(row=2, column=0, rowspan=8, columnspan=2, sticky='nse', pady=(5, 5), padx=(5, 5))
        
        # ===================== (Fields list)
        self.form['f1_lab'] = tk.Label(self.master, text='Jmeno')
        self.form['f1_inp'] = tk.Entry(self.master, textvariable=self.active_sel['name'])
        self.form['f2_lab'] = tk.Label(self.master, text='Cislo')
        self.form['f2_inp'] = tk.Entry(self.master, textvariable=self.active_sel['number'])
        self.form['f3_lab'] = tk.Label(self.master, text='Dalsi')
        self.form['f3_inp'] = tk.Entry(self.master, textvariable=self.active_sel['various'])
        self.form['f3_inp'].insert(0, 'zatim nic...')

        self.form['f1_lab'].grid(row=2, column=2, columnspan=1)
        self.form['f1_inp'].grid(row=2, column=3, columnspan=2)
        self.form['f2_lab'].grid(row=3, column=2, columnspan=1)
        self.form['f2_inp'].grid(row=3, column=3, columnspan=2)
        self.form['f3_lab'].grid(row=4, column=2, columnspan=1)
        self.form['f3_inp'].grid(row=4, column=3, columnspan=2)

        # TODO: 1. Switcher between folder and file mode still not working
        # TODO: 2. Exporting / Merging

        self.set_dir()  # first app init is hardcoded to folder

    def set_dir(self):
        if self.curr_loc:
            print('browsing folder', self.curr_loc)
        self.browse_dir()
        self.refresh()

    def set_file(self):
        if self.curr_loc:
            print('setting file', self.curr_loc)
        self.browse_dir()
        self.refresh()

    def browse_dir(self):
        backup = self.curr_loc
        if self.mode.get():
            self.curr_loc = dialog.askopenfilename()
            really = False
        else:
            self.curr_loc = dialog.askdirectory()
            really = True
        if self.curr_loc:
            self.contacts_lib = ContactList(self.curr_loc, is_dir=really)
            self.await_load = True
        else:
            self.curr_loc = backup  # reverting to previous value

    def refresh(self):
        try:
            self.contacts_lib.dic
            if self.await_load:
                self.contacts_list.delete(0, 'end')
                for record in self.contacts_lib.dic.keys():
                    self.contacts_list.insert('end', str(record) + '. ' + self.contacts_lib.dic[record]['FN'])
                self.await_load = False
            self.current_location['text'] = 'Location : {0}'.format(self.curr_loc)
        except AttributeError:
            print('no contacts library loaded')

    def on_select(self, evt):
        w = evt.widget
        if w == self.contacts_list:  # click in contact list
            if w.curselection():
                self.form['f1_inp'].delete(0, 'end')
                self.form['f2_inp'].delete(0, 'end')
                index = int(w.curselection()[0])
                value = int(w.get(index).split('.')[0])
                self.active_sel['index'] = value
                self.active_sel['contact'] = self.contacts_lib.dic[value]['FN']
                self.active_sel['number'] = self.contacts_lib.dic[value]['TEL']

                self.form['f1_inp'].insert(20, self.contacts_lib.dic[value]['FN'])
                self.form['f2_inp'].insert(20, self.contacts_lib.dic[value]['TEL'])
                # TODO: need to change a lot more
        self.refresh()

    def which_mode(self):
        return False if self.mode.get() else True

    def prev(self):
        if self.contacts_lib:
            if self.active_sel['index'] > 1:
                self.active_sel['index'] -= 1
            self.control()

    def next(self):
        if self.contacts_lib:
            if self.active_sel['index'] < len(self.contacts_lib.dic):
                self.active_sel['index'] += 1
            self.control()

    def control(self):
        if (self.contacts_list.curselection()[0]+1) < len(self.contacts_lib.dic):
            self.active_sel['contact'] = self.contacts_lib.dic[int(self.active_sel['index'])]['FN']
            self.active_sel['number'] = self.contacts_lib.dic[int(self.active_sel['index'])]['TEL']
            self.form['f1_inp'].delete(0, 'end')
            self.form['f2_inp'].delete(0, 'end')
            self.form['f1_inp'].insert(20, self.active_sel['contact'])
            self.form['f2_inp'].insert(20, self.active_sel['number'])
            print('Setting', str(self.contacts_list.curselection()[0]+1), '>', str(self.active_sel['index']), 'record')
            self.contacts_list.selection_clear(0, "end")
            self.contacts_list.selection_set(int(self.active_sel['index'])-1)
            self.contacts_list.see(int(self.active_sel['index'])-1)
            self.contacts_list.activate(int(self.active_sel['index'])-1)
            self.contacts_list.selection_anchor(int(self.active_sel['index'])-1)
            # self.contacts_list.select_set(int(self.active_sel['index'])-1)
            # self.contacts_list.event_generate("<<ListboxSelect>>")

    def export(self):
        if self.contacts_lib:
            if self.mode.get():  # file mode, export to directory
                final_loc = dialog.askdirectory()
            else:
                final_loc = dialog.asksaveasfile(mode='w', defaultextension=".txt")
            if self.curr_loc != final_loc and final_loc:
                if self.mode.get():
                    self.contacts_lib.dic.export(final_loc)
                else:
                    self.contacts_lib.dic.merge(final_loc)

    def quit(self):
        self.master.destroy()

    
def contacts_editor():
    root = tk.Tk()

    root.title('Editor VCF kontaktu')
    root.resizable(10, 10)
    # root.geometry('1200x900')
    #root.columnconfigure(0, weight=2)
    #root.columnconfigure(1, weight=1)
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    contacts_editor()
