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
import Contact

# Main logic and layout
class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active = {
            'contact': {},
            'index': 0,
            'loading': True,  # flag after load a file/dir
            'location': '',
            'mode': tk.IntVar(value=0)  # folder value active
        }
        self.btn = {}
        self.form = {}
        self.contacts_lib = ''
        
        # ===================== (Main Menu + controls)
        self.current_location = tk.Label(self.master, text='Location : {0}'.format(self.active['location']))
        self.radio1 = tk.Radiobutton(self.master, text='Adresar', value=False, variable=self.active['mode'], command=self.set_dir)
        self.radio2 = tk.Radiobutton(self.master, text='Soubor', value=True, variable=self.active['mode'], command=self.set_file)
        
        self.current_location.grid(row=0, column=0, columnspan=3, sticky='w')
        self.radio1.grid(row=0, column=4)
        self.radio2.grid(row=0, column=5)
        
        # ===================== (Button Menu)
        self.btn['open'] = tk.Button(self.master, text='open', command=self.browse_dir)
        self.btn['expt'] = tk.Button(self.master, text='export', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save', command=self.save) 
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
        
        self.contacts_list.grid(row=2, column=0, rowspan=5, columnspan=2, sticky='nsew')
        self.contacts_scroll.grid(row=2, column=0, rowspan=5, columnspan=2, sticky='nse')

        # TODO: 1. Switcher between folder and file mode not working
        # TODO: 2. Exporting / Merging

        self.set_dir()  # first app init is hardcoded to folder

    def set_dir(self):
        if self.active['location']:
            print('browsing folder', self.active['location'])
        self.browse_dir()
        self.refresh()

    def set_file(self):
        if self.active['location']:
            print('setting file', self.active['location'])
        self.browse_dir()
        self.refresh()

    def browse_dir(self):
        backup = self.active['location']
        if self.active['mode'].get():
            self.active['location'] = dialog.askopenfilename()
            really = False
        else:
            self.active['location'] = dialog.askdirectory()
            really = True
        if self.active['location']:
            self.contacts_lib = Contact.ContactList(self.active['location'], is_dir=really)
            self.active['loading'] = True
        else:
            self.active['location'] = backup  # reverting to previous value

    def build_fields(self, contact):
        # the structure hardcoded for now, dynamic too cluttered
        if isinstance(contact['N'], str):
            x = {'given': '','family':contact['N'],'telephone': contact['TEL']}
        else:
            x = {
                'given': contact['N'].given,'family':contact['N'].family,
                'telephone': contact['TEL']
                }
        for i, key in enumerate(x, start=1):
            if self.form.get(f'f{key}_inp'):
                self.form[f'f{key}_inp'].delete(0, 'end')
                self.form[f'f{key}_inp'].destroy()
            if self.form.get(f'f{key}_lab'):
                self.form[f'f{key}_lab'].destroy()
            try:
                self.form[f'f{key}_lab'] = tk.Label(self.master, text=key)
                self.form[f'f{key}_inp'] = tk.Entry(self.master)
                self.form[f'f{key}_lab'].grid(row=1+i, column=3, columnspan=1)
                self.form[f'f{key}_inp'].grid(row=1+i, column=4, columnspan=2)
                self.form[f'f{key}_inp'].insert(20, x[key])
            except IndexError:
                print('skipping this one', contact.keys())

    def refresh(self):
        try:
            a = self.contacts_lib.dic
            if self.active['loading']:
                # clear and fill again contact list
                self.contacts_list.delete(0, 'end')
                for record in a.keys():
                    if isinstance(a[record]['FN'], str):
                        self.contacts_list.insert('end', str(record) + '. ' + a[record]['FN'])
                    else:
                        self.contacts_list.insert(
                            'end',
                            f'{record}. {a[record]["FN"].given} {a[record]["FN"].family}',
                        )

                self.active['loading'] = False
            self.current_location['text'] = 'Location : {0}'.format(self.active['location'])
        except AttributeError:
            print('... no contacts library loaded')

    def on_select(self, evt):
        w = evt.widget
        if w == self.contacts_list and w.curselection():  # click in contact list
            index = int(w.curselection()[0])
            value = int(w.get(index).split('.')[0])
            self.active['contact'] = self.contacts_lib.dic[value]
            self.build_fields(self.contacts_lib.dic[value])
        self.refresh()

    def which_mode(self):
        return not self.active['mode'].get()

    def prev(self):
        if self.contacts_lib:
            if self.active['index'] > 1:
                self.active['index'] -= 1
            self.control()

    def next(self):
        if self.contacts_lib:
            if self.active['index'] < len(self.contacts_lib.dic):
                self.active['index'] += 1
            self.control()

    def control(self):
        if (self.contacts_list.curselection()[0]+1) < len(self.contacts_lib.dic):
            self.active['contact'] = self.contacts_lib.dic[int(self.active['index'])]['FN']
            self.active['number'] = self.contacts_lib.dic[int(self.active['index'])]['TEL']
            self.form['f1_inp'].delete(0, 'end')
            self.form['f2_inp'].delete(0, 'end')
            self.form['f1_inp'].insert(20, self.active['contact'])
            self.form['f2_inp'].insert(20, self.active['number'])
            print('Setting', str(self.contacts_list.curselection()[0]+1), '>', str(self.active['index']), 'record')
            self.contacts_list.selection_clear(0, "end")
            self.contacts_list.selection_set(int(self.active['index'])-1)
            self.contacts_list.see(int(self.active['index'])-1)
            self.contacts_list.activate(int(self.active['index'])-1)
            self.contacts_list.selection_anchor(int(self.active['index'])-1)
            # self.contacts_list.select_set(int(self.active['index'])-1)
            # self.contacts_list.event_generate("<<ListboxSelect>>")

    def export(self):
        if self.contacts_lib:
            if self.active['mode'].get():  # file mode, export to directory
                final_loc = dialog.askdirectory()
            else:
                final_loc = dialog.asksaveasfile(mode='w', defaultextension=".txt")
            # self.contacts_lib.find_duplicates()  # for sure report them, later  do different
            if self.active['location'] != final_loc and final_loc:
                if self.active['mode'].get():
                    self.contacts_lib.export(final_loc)
                else:
                    self.contacts_lib.merge(final_loc)

    def save(self):
        if not self.active['contact']:
            return
        if self.active['mode'].get():
            print('...not implemented yet')
        else:  # folder mode
            self.build_contact()

    def build_contact(self):
        if self.active['contact']['N'].family:
            n = self.active['contact']['N'].given + ' ' + self.active['contact']['N'].family
        else:
            n = self.active['contact']['FN']
        path = self.active['location']+'/'+n+'.vcf'
        name = self.form['fgiven_inp'].get()
        family = self.form['ffamily_inp'].get()
        phone = self.form['ftelephone_inp'].get()
        v = Contact.vcf_object(name, family, phone, path)
        Contact.smash_it(path)
        path = path.replace(n,name+' '+family)
        # with open(path, 'w', encoding="utf-8") as original:  # bud prepis nebo novy
        with open(path, 'wb') as original: 
            original.write(Contact.quoted_printable(v))
        self.contacts_lib = Contact.ContactList(self.active['location'], is_dir=True)
        self.refresh()

    def quit(self):
        self.master.destroy()

    
def contacts_editor():
    root = tk.Tk()

    root.title('Editor VCF kontaktu')
    root.resizable(7, 6)
    # root.geometry('1200x900')
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)
    root.columnconfigure(4, weight=1)
    root.columnconfigure(5, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    root.rowconfigure(4, weight=1)
    root.rowconfigure(5, weight=1)
    root.rowconfigure(6, weight=1)
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    contacts_editor()
