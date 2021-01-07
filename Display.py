# -*- coding: utf-8 -*-
import os


# Must do for compatibility win <> lnx
try:
    import Tkinter as tk
    print('using big tkinter')
except ImportError:
    import tkinter as tk
    print('using small tkinter')
    
# Now contact list
from Contact import ContactList


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active_sel = ''
        self.contacts_lib = ContactList(directory, is_dir=True)
        
        # ===================== (Main Menu + controls)
        self.main_menu = tk.Label(self.master, text=' Main Menu ...')
        self.current_location = tk.Label(self.master, text='Location : {0}'.format(directory))
        
        self.main_menu.grid(row=0, column=0, sticky='w')
        self.current_location.grid(row=0, column=1, sticky='e')
        
        # ===================== (Contacts list)
        self.contacts_list = tk.Listbox(self.master, height=7)
        self.contacts_list.bind('<<ListboxSelect>>', self.on_select)
        self.contacts_scroll = tk.Scrollbar(self.master, orient='vertical')
        
        self.contacts_list['yscrollcommand'] = self.contacts_scroll.set
        self.contacts_scroll['command'] = self.contacts_list.yview
        
        self.contacts_list.grid(row=1, column=0, rowspan=6, columnspan=1, sticky='nse', pady=(5, 5), padx=(5, 5))
        self.contacts_scroll.grid(row=1, column=0, rowspan=6, columnspan=1, sticky='nse', pady=(5, 5), padx=(5, 5))
        
        # ===================== (Fields list)
        
        # TODO: 1. Switcher between folder and file mode
        # TODO: 2. Field list 
        # TODO: 3. Exporting / Merging
        
        self.refresh()  # list widgets



    def refresh(self):
        # refreshing whole layout
        self.contacts_list.delete(0, 'end')
        if self.contacts_lib:
            for c_file in self.contacts_lib.dic.keys():
                self.contacts_list.insert('end', c_file)
        
            
    def on_select(self, evt):
        w = evt.widget
        if w.curselection():
            index = int(w.curselection()[0])
            value = w.get(index)
            if w == self.contacts_list:
                print('get', value)
            else:
                print('clicked view list, specialized layout for each separate')
            self.refresh()  # list widgets




    
def contacts_editor():
    root = tk.Tk()

    root.title('Editor VCF kontaktu')
    root.resizable(0, 0)
    root.geometry('1200x900')

    global directory
    # directory = os.getcwd()
    directory = 'C:\\Users\\jirib\\Downloads\\SD_samci\\work'
    print('using directory', directory)

    MainWindow(root)  # .pack(side="top", fill="both", expand=True)
    root.mainloop()


    
if __name__ == '__main__':
    contacts_editor()
