from difflib import SequenceMatcher
from pathlib import Path
from quopri import encodestring
from unidecode import unidecode

try:
    import vobject
except ImportError:
    raise Exception('... cannot work with vcf_location contacts, please install vobject')


def parse_vcard(vcard: vobject) -> dict:
    """Extract detailed contact attributes from a VCard object into a dictionary."""
    contact = {
        'full_name': None,
        'given_name': None,
        'family_name': None,
        'phone_numbers': [],
        'emails': [],
        'addresses': [],
        'organization': None,
        'job_title': None,
        'birthday': None,
        'notes': None,
    }
    # Extract full name
    if hasattr(vcard, 'fn'):
        contact['full_name'] = str(vcard.fn.value)
    # Extract name components
    if hasattr(vcard, 'n'):
        contact['given_name'] = str(vcard.n.value.given)
        contact['family_name'] = str(vcard.n.value.family)
    # Extract phone numbers
    for tel in vcard.contents.get('tel', []):
        contact['phone_numbers'].append(str(tel.value))
    # Extract emails
    for email in vcard.contents.get('email', []):
        contact['emails'].append(str(email.value))
    # Extract addresses
    for adr in vcard.contents.get('adr', []):
        address = ', '.join(filter(None, [
            adr.value.street,
            adr.value.city,
            adr.value.region,
            adr.value.code,
            adr.value.country
        ]))
        contact['addresses'].append(address)
    # Extract organization
    if hasattr(vcard, 'org'):
        contact['organization'] = ' '.join(vcard.org.value)
    # Extract job title
    if hasattr(vcard, 'title'):
        contact['job_title'] = str(vcard.title.value)
    # Extract birthday
    if hasattr(vcard, 'bday'):
        contact['birthday'] = str(vcard.bday.value)
    # Extract notes
    if hasattr(vcard, 'note'):
        contact['notes'] = str(vcard.note.value)

    return contact


def create_vcard(contact: dict) -> vobject:
    """Convert a contact dictionary to a vCard object."""
    vcard = vobject.vCard()

    # Add full name
    if contact.get('full_name'):
        vcard.add('fn')
        vcard.fn.value = contact['full_name']

    # Add name components
    if contact.get('given_name') or contact.get('family_name'):
        vcard.add('n')
        vcard.n.value = vobject.vcard.Name(
            family=contact.get('family_name', ''),
            given=contact.get('given_name', '')
        )

    # Add phone numbers with types
    if isinstance(contact.get('phone_numbers', []), str):
        tel = vcard.add('tel')
        tel.value = contact.get('phone_numbers', [])
        tel.type_param = 'CELL'
    else:
        for phone in contact.get('phone_numbers', []):
            tel = vcard.add('tel')
            tel.value = phone
            tel.type_param = 'CELL'  # Example type

    # Add emails with types
    if isinstance(contact.get('emails', []), str):
        email_field = vcard.add('email')
        email_field.value = contact.get('emails', [])
        email_field.type_param = 'HOME'  # Example type
    else:
        for email in contact.get('emails', []):
            email_field = vcard.add('email')
            email_field.value = email
            email_field.type_param = 'HOME'  # Example type

    # Add addresses
    if isinstance(contact.get('addresses', []), str):
        address_field = vcard.add('adr')
        address_field.value = contact.get('addresses', [])
        address_field.type_param = 'HOME'  # Example type
    else:
        for address in contact.get('addresses', []):
            address_field = vcard.add('adr')
            address_field.value = address
            address_field.type_param = 'HOME'  # Example type

    return vcard


class ContactList:
    """Creates a Contact list object either from a single file or a directory with vcf files"""

    def __init__(self, vcf_location: str, is_dir=False) -> None:
        self.counter = 0  # Start index for contacts
        self.dic = {}  # Holds all the contact list indexed by counter
        self.ac_key = ''  # For duplicates and searching
        self.ac_val = ''
        try:
            if len(vcf_location) > 0:
                if is_dir:  # this way counting number of files
                    self.load_directory(vcf_location)
                else:  # this way counting number of records in a file
                    self.open_vcf(vcf_location)
            else:
                print("please follow with ContactList.open_vcf() or ContactList.load_directory()")
        except Exception as e:
            print('error:', e)

    def _step(self, i: int = 1) -> None:
        """Increment the current index by the specified step value."""
        self.counter += i

    def find_duplicates(self):
        """Finds duplicates across library."""
        # TODO: not valid, need to repair
        for key, value in self.dic.items():
            self.ac_key = key
            self.ac_val = value
            if self.search(value):
                print(f'... consider as a duplicate {key} ({value})')

    def search(self, s):
        """Search similar contacts."""
        # TODO: not valid, need to repair
        occurs = 0
        for item_no, details in self.dic.items():
            if item_no != self.ac_key:
                name_ratio = SequenceMatcher(None, s['full_name'], details['full_name']).ratio()
                tel_ratio = SequenceMatcher(None, s['TEL'], details['TEL']).ratio()
                if name_ratio > 0.9 or tel_ratio > 0.9:
                    occurs += 1
                    print(
                        f'!!! found {details["full_name"]} ({details["TEL"]}) that is suspect to {s["full_name"]} ({s["TEL"]})')
        return occurs

    def export(self, path):
        """Exporting contacts (currently multiple files in directory)."""
        print('.' * 3, f'processing {len(self.dic)} files')
        for record in self.dic.keys():
            actual = create_vcard(self.dic[record])
            actual.name = 'VCARD'
            actual.useBegin = True
            # actual.prettyPrint()
            print_path = Path(path) / f"{self.dic[record]['full_name']}.vcf"
            if Path(print_path).exists():
                print(f' overwrite {print_path}')
            with open(print_path, mode='w', encoding='utf-8') as f:
                f.write(actual.serialize())
        print('.' * 3, f'done')

    def merge(self, path):
        if Path(path.name).is_dir():
            with open(path + self.dic[self.ac_key]['FN'], mode='a', encoding='utf-8') as f:
                f.write(self.dic.serialize())
        else:
            with open(path.name, mode='a', encoding='utf-8') as f:
                f.write(self.dic.serialize())
            #for record in self.dic.keys():
            #    f.write(self.dic[record].serialize())

    def open_vcf(self, location: str):
        """Load contacts from a single VCF file."""
        try:
            with open(location, mode='r', encoding='utf-8') as vcf_file:
                vcard_data = vcf_file.read()
            for vcard in vobject.readComponents(vcard_data, allowQP=True):
                contact = parse_vcard(vcard)
                self._step(1)  # Incrementing the index contact
                self.dic[self.counter] = contact
        except Exception as e:
            print(f"Error loading file {location}: {e}")

    def load_directory(self, directory_path: str) -> None:
        """Load all VCF files in a directory."""
        for file in Path(directory_path).rglob("*.vcf"):
            self.open_vcf(str(file))

    def __str__(self) -> str:
        """String representation of the contact list."""
        return f"ContactList with {len(self.dic)} contacts"


def smash_it(path: str = ''):
    try:
        if Path(path).is_file():
            Path.unlink(path)
        else:
            print(f'... file {path} does not exist')
    except OSError as e:  # 
        print(f"!!! Error when deleting {e.filename} - {e.strerror}.")


def name_value(first='', last=''):
    if first and last:
        # return ';'.join((m.family, m.given, m.prefix, m.suffix, m.additional))
        return vobject.vcard.Name(family=last, given=first)


def quoted_printable(vcf: vobject, serialize: bool = True):
    if vcf and serialize:
        # first = encodestring(first.encode('utf-8'))
        # last = encodestring(last.encode('utf-8'))
        a = encodestring(vcf.serialize().encode('utf-8'))
        a = a.replace(b'\nN:', b'\nN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        a = a.replace(b'FN:', b'FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        a = a.replace(b';CHARSET=3DUTF-8:', b';ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:')
        return a


def export_to_vcf(location, vc):
    """
    exports vobject to a *.vcf_location file
    :param location: where to write
    :param vc: single vobject instance
    """
    vcf_name = f'{vc.fn.value}.vcf_location'  # .encode().decode('unicode-escape')
    with open(location + vcf_name, mode='w', encoding='utf-8') as f:
        f.write(vc.serialize())


def append_to_vcf(location, vc):
    """
    appends vobject to a *.vcf_location file
    :param location: where to write
    :param vc: single vobject instance
    """
    vcf_name = f'{vc.fn.value}.vcf_location'  # .encode().decode('unicode-escape')
    with open(location + vcf_name, mode='a', encoding='utf-8') as f:
        f.write(vc.serialize())


if __name__ == '__main__':
    source = Path('sample') / 'export'
    target = Path('sample') / 'processed'

    if source.is_dir():
        debug_object = ContactList(str(source), is_dir=True)
        print(quoted_printable(debug_object))
        for index, value in debug_object.dic.items():
            target_file = target / unidecode(value["full_name"] + ".vcf")
            with open(target_file, 'wb') as output_file:
                output_file.write(quoted_printable(value))
    else:
        debug_object = ContactList(str(source), is_dir=False)
        debug_object.find_duplicates()
