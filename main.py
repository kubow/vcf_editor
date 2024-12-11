# -*- coding: utf-8 -*-
from tkinter import Button, Entry, IntVar, Label, Listbox, Radiobutton, Scrollbar, TclError, Tk
from tkinter.filedialog import asksaveasfile, askopenfilename, askdirectory
from Contact import ContactList, create_vcard, parse_vcard, quoted_printable, smash_it


class MainWindow:
    def __init__(self, master):
        """Maintain tkinter logic"""
        self.master = master
        self.active = {
            'contact': {},
            'index': 0,
            'loading': True,  # flag after load a file/dir
            'location': '',
            'mode': IntVar(value=0)  # folder value active
        }
        self.contacts_lib = None  # here is the whole vcf library held
        self.tk_btn = {}
        self.tk_form = {}

        # ===================== (Main Menu + controls - 3 separate tk variables)
        self.tk_current_location = Label(self.master, text=f'Location: {self.active['location']}')
        self.tk_radio_directory = Radiobutton(self.master, text='Directory', value=False,
                                              variable=self.active['mode'],
                                              command=self.set_dir)
        self.tk_radio_file = Radiobutton(self.master, text='File', value=True, variable=self.active['mode'],
                                         command=self.set_file)

        self.tk_current_location.grid(row=0, column=0, columnspan=3, sticky='w')
        self.tk_radio_directory.grid(row=0, column=4)
        self.tk_radio_file.grid(row=0, column=5)

        # ===================== (Button Menu - all 6 buttons in one dict variable)
        self.tk_btn['open'] = Button(self.master, text='open', command=self.browse_dir)
        self.tk_btn['expt'] = Button(self.master, text='export', command=self.export)
        self.tk_btn['prev'] = Button(self.master, text='<', command=self.prev)
        self.tk_btn['save'] = Button(self.master, text='save', command=self.save)
        self.tk_btn['next'] = Button(self.master, text='>', command=self.next)
        self.tk_btn['exit'] = Button(self.master, text='quit', command=self.quit)
        self.tk_btn['open'].grid(row=1, column=0, pady=5, sticky='nsew')
        self.tk_btn['expt'].grid(row=1, column=1, pady=5, sticky='nsew')
        self.tk_btn['prev'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.tk_btn['save'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.tk_btn['next'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.tk_btn['exit'].grid(row=1, column=5, pady=5, sticky='nsew')

        # ===================== (Contacts list)
        self.tk_contacts_list = Listbox(self.master, height=7)  # selectmode='SINGLE'
        self.tk_contacts_list.bind('<<ListboxSelect>>', self.on_select)
        self.tk_contacts_scroll = Scrollbar(self.master, orient='vertical')

        self.tk_contacts_list['yscrollcommand'] = self.tk_contacts_scroll.set
        self.tk_contacts_scroll['command'] = self.tk_contacts_list.yview

        self.tk_contacts_list.grid(row=2, column=0, rowspan=5, columnspan=2, sticky='nsew')
        self.tk_contacts_scroll.grid(row=2, column=0, rowspan=5, columnspan=2, sticky='nse')

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
            self.active['location'] = askopenfilename()
            really = False
        else:
            self.active['location'] = askdirectory()
            really = True
        if self.active['location']:
            self.contacts_lib = ContactList(self.active['location'], is_dir=really)
            self.active['loading'] = True
        else:
            self.active['location'] = backup  # reverting to previous value

    def build_fields(self, contact):
        """Main function for building a right side form with contact details"""
        for i, key in enumerate(contact, start=1):
            self.destroy_form_field(key)
            if not contact[key]:
                continue  # skip render for empty fields
            self.build_form_field(key)
            self.tk_form[f'{key}_lab'].grid(row=1 + i, column=3, columnspan=1)
            self.tk_form[f'{key}'].grid(row=1 + i, column=4, columnspan=2)
            self.tk_form[f'{key}'].insert(20, contact[key])

    def build_form_field(self, key):
        try:
            self.tk_form[f'{key}_lab'] = Label(self.master, text=key)
            self.tk_form[f'{key}'] = Entry(self.master)
        except TclError:
            print('... skipping field', key, 'already deleted')

    def destroy_form_field(self, key):
        try:
            if self.tk_form.get(f'{key}_lab'):
                self.tk_form[f'{key}_lab'].destroy()
            if self.tk_form.get(f'{key}'):
                self.tk_form[f'{key}'].delete(0, 'end')
                self.tk_form[f'{key}'].destroy()
        except TclError:
            print('... skipping field', key, 'already deleted')

    def on_select(self, evt):
        w = evt.widget
        if w == self.tk_contacts_list and w.curselection():  # click in contact list
            index = int(w.curselection()[0])
            value = int(w.get(index).split('.')[0])
            self.active['index'] = value
            self.active['contact'] = self.contacts_lib.dic[value]
            self.build_fields(self.contacts_lib.dic[value])
        self.refresh()

    def refresh(self):
        try:
            a = self.contacts_lib.dic
            if self.active['loading']:
                # clear and fill again contact list
                self.tk_contacts_list.delete(0, 'end')
                for record in a.keys():
                    if isinstance(a[record]['full_name'], str):
                        self.tk_contacts_list.insert('end', f'{record}. {a[record]["full_name"]}')
                    else:
                        self.tk_contacts_list.insert('end', f'{record}. {a[record]["family_name"]}')
                self.active['loading'] = False
            self.tk_current_location['text'] = f'Location: {self.active['location']}'
        except AttributeError:
            print('... no contacts library loaded')
            # TODO: meaningful error handling

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
        # setting active contact based on previously activated record
        self.active['contact'] = self.contacts_lib.dic[self.active['index']]
        self.build_fields(self.contacts_lib.dic[self.active['index']])

        self.tk_contacts_list.selection_clear(0, "end")
        self.tk_contacts_list.selection_set(int(self.active['index']) - 1)
        self.tk_contacts_list.see(int(self.active['index']) - 1)
        self.tk_contacts_list.activate(int(self.active['index']) - 1)
        self.tk_contacts_list.selection_anchor(int(self.active['index']) - 1)
        # self.tk_contacts_list.select_set(int(self.active['index'])-1)
        # self.tk_contacts_list.event_generate("<<ListboxSelect>>")

    def export(self):
        if self.contacts_lib:
            if self.active['mode'].get():  # file mode, export to directory
                final_loc = askdirectory()
            else:
                final_loc = asksaveasfile(mode='w', defaultextension=".txt")
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
        """reconstruct contact from the form and re-save the file (name may differ)
        note: FN field is not obligatory (in vCard 2.1) but python implementation requires that
              thus it is enforced to enrich the tag from original name (N tag)
        """
        packed_form = {key: get_widget_value(value) for key, value in self.tk_form.items() if "_lab" not in key}
        if "full_name" not in packed_form.keys():
            packed_form["full_name"] = packed_form["given_name"] + " " + packed_form["family_name"]
        v = create_vcard(packed_form)
        
        if self.active["contact"]["full_name"]:
            path = f'{self.active["location"]}/{self.active["contact"]["full_name"]}.vcf'
            new_path = path.replace(self.active["contact"]["full_name"], v.contents.get("fn")[0].value)
        else:
            path = f'{self.active["location"]}/{self.active["contact"]["given_name"]} {self.active["contact"]["family_name"]}.vcf'
            new_path = path.replace(
                self.active["contact"]["given_name"] + " " + self.active["contact"]["family_name"],
                v.contents.get("n")[0].value.given + " " + v.contents.get("n")[0].value.family
            )
        smash_it(path)
        # TODO: check if open(path, 'w', encoding="utf-8") needed
        with open(new_path, 'wb') as changed:
            changed.write(quoted_printable(v))
        self.contacts_lib = ContactList(self.active['location'], is_dir=True)
        self.refresh()

    def quit(self):
        self.master.destroy()


def get_widget_value(widget):
    try:
        if hasattr(widget, "get"):
            return widget.get()
        elif hasattr(widget, "cget"):
            return widget.cget("text")
    except Exception as e:
        return f"Error retrieving value: {e}"
    return "Unsupported widget"


def contacts_editor():
    root = Tk()

    root.title('VCF contact editor')
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
