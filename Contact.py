from difflib import SequenceMatcher
import os
from pathlib import Path
import quopri
from unidecode import unidecode
try:
    import vobject
    can_vcf = True
except ImportError:
    print('... cannot work with vcf contacts')
    can_vcf = False
class ContactList:
    def __init__(self, vcf, is_dir=False):
        self.counter = 0
        self.dic = {}
        self.ac_key = ''
        self.ac_val = ''
        try:
            if len(vcf) > 0 and can_vcf:
                if is_dir:  # this way counting number of files
                    for file in os.listdir(vcf):
                        with open(vcf+'\\'+file, mode='r', encoding='utf-8') as vcf_file:
                            self.counter += 1
                            self.append(vobject.readOne(vcf_file))
                else:  # this way counting number of records in a file
                    with open(vcf, mode='r', encoding='utf-8') as vcf_file:
                        for v in vobject.readComponents(vcf_file):
                            self.counter += 1
                            self.append(v)
        except Exception as e:
            print('error:', e)

    def append(self, vobj):
        # print(str(self.counter)+'. '+str(vobj))
        # vobj.n.value, str(vobj.tel.value).replace(' ', '')
        passed = False
        self.dic[self.counter] = {}
        for field in vobj.getSortedChildren():
            if field.name.lower() == 'fn':
                passed = True
            self.dic[self.counter][field.name] = field.value
        if not passed:
            self.dic[self.counter]['FN'] = self.dic[self.counter]['N']
        # append_to_vcf(vcf + 'pokus.vcf', v)
        # export_to_vcf(home_folder + 'work\\', vcard)

    def find_duplicates(self):
        # TODO: not valid, need to repair
        for key, value in self.dic.items():
            self.ac_key = key
            self.ac_val = value
            if self.search(value):
                print(f'... consider as a duplicate {key} ({value})')

    def search(self, s):
        # TODO: not valid, need to repair
        occurs = 0
        for item_no, details in self.dic.items():
            if item_no != self.ac_key:
                name_ratio = SequenceMatcher(None, s['FN'], details['FN']).ratio()
                tel_ratio = SequenceMatcher(None, s['TEL'], details['TEL']).ratio()
                if name_ratio > 0.9 or tel_ratio > 0.9:
                    occurs += 1
                    print(f'!!! found {details["FN"]} ({details["TEL"]}) that is suspect to {s["FN"]} ({s["TEL"]})')
        return occurs

    def export(self, path):
        i = 0
        for record in self.dic.keys():
            actual = vobject.readOne(
                '\n'.join(f'{k}:{v}' for k, v in self.dic[record].items())
            )
            actual.name = 'VCARD'
            actual.useBegin = True
            # actual.prettyPrint()
            print_path = os.path.join(path, self.dic[record]['FN']+'.vcf')
            if os.path.exists(print_path):
                print(f' overwrite {print_path}')
            with open(print_path, mode='w', encoding='utf-8') as f:
                f.write(actual.serialize())
            i += 1
        print('.'*3, f'processed {i} files')

    def merge(self, path):
        if os.path.isdir(path.name):
            with open(path + self.dic[self.ac_key]['FN'], mode='a', encoding='utf-8') as f:
                f.write(self.dic.serialize())
        else:
            with open(path.name, mode='a', encoding='utf-8') as f:
                f.write(self.dic.serialize())
            #for record in self.dic.keys():
            #    f.write(self.dic[record].serialize())

def open_vcf(location, debug=True):
    with open(location, mode='r', encoding='utf-8') as vcf_file:
        for v in vobject.readComponents(vcf_file):
            if debug:
                print(v.serialize())
                print('*'*20)
            return v

def vcf_object(first='', last='', tel='', loc=False):
    if loc:
        m = open_vcf(loc)
        print(f'replacing values in {loc} ({first} {last} / {tel})')
        m.n.value.family = last
        m.n.value.given = first
        m.fn.value = f'{first} {last}'
        m.tel.value = tel
    else:        
        m = vobject.vCard()
        m.version = '2.1'
        if first or last:    
            o = m.add('fn')
            o.value = f'{first} {last}'
            o = m.add('n')
            o.value = vobject.vcard.Name(family=last, given=first)
        if tel:
            o = m.add('tel')
            o.type_param = 'cell'
            o.value = tel
    return m

def smash_it(path=''):
    try:
        if os.path.isfile(path):
            os.remove(path)
        else:
            print(f'... soubor {path} neexistuje nebo neni vubec soubor')
    except OSError as e:  # 
        print(f"!!! Chyba pri mazani {e.filename} - {e.strerror}.")

def name_value(first='', last=''):
    if first and last:
        # return ';'.join((m.family, m.given, m.prefix, m.suffix, m.additional))
        return vobject.vcard.Name(family=last, given=first)

def quoted_printable(vcf, serialize=True):
    if vcf and serialize:
        #first = quopri.encodestring(first.encode('utf-8'))
        #last = quopri.encodestring(last.encode('utf-8'))
        a = quopri.encodestring(vcf.serialize().encode('utf-8'))
        a = a.replace(b'\nN:',b'\nN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        a = a.replace(b'FN:',b'FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        a = a.replace(b';CHARSET=3DUTF-8:', b';ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        return a

def export_to_vcf(location, vc):
    """
    exports vobject to a *.vcf file
    :param location: where to write
    :param vc: single vobject instance
    """
    vcf_name = f'{vc.fn.value}.vcf'   # .encode().decode('unicode-escape')
    with open(location + vcf_name, mode='w', encoding='utf-8') as f:
        f.write(vc.serialize())

def append_to_vcf(location, vc):
    """
    appends vobject to a *.vcf file
    :param location: where to write
    :param vc: single vobject instance
    """
    vcf_name = f'{vc.fn.value}.vcf'   # .encode().decode('unicode-escape')
    with open(location + vcf_name, mode='a', encoding='utf-8') as f:
        f.write(vc.serialize())

if __name__ == '__main__':
    source = Path('contacts') / 'export'
    target = Path('contacts') / 'processed'
    for filename in source.rglob('*.vcf'):
        print(filename)
        vcf = open_vcf(filename)
        print(quoted_printable(vcf))
        target_file = target / unidecode(filename.name)
        with open(target_file, 'wb') as output_file:
            output_file.write(quoted_printable(vcf))


    # debug_object = ContactList(file_name)
    #debug_object = ContactList(home_folder+'Dohromady', is_dir=True)
    #debug_object.find_duplicates()
