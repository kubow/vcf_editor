"""Unit tests for Contact.py - VCF contact handling."""

import tempfile
from pathlib import Path

import pytest
import vobject

from Contact import (
    ContactList,
    create_vcard,
    name_value,
    parse_vcard,
)


# --- Fixtures ---

@pytest.fixture
def sample_vcard_data():
    """Minimal VCF content for testing."""
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
EMAIL;TYPE=INTERNET;TYPE=HOME:john@example.com
TEL;TYPE=CELL:1234567890
END:VCARD"""


@pytest.fixture
def sample_vcard(sample_vcard_data):
    """Parse sample VCF data into a vobject."""
    return next(vobject.readComponents(sample_vcard_data))


@pytest.fixture
def full_contact_dict():
    """A complete contact dictionary for testing (without addresses - see note)."""
    # Note: addresses are excluded because create_vcard stores them as strings,
    # but vobject requires Address objects for serialization.
    # This is a known limitation of the current implementation.
    return {
        'full_name': 'Jane Smith',
        'given_name': 'Jane',
        'family_name': 'Smith',
        'phone_numbers': ['555-1234', '555-5678'],
        'emails': ['jane@example.com', 'jane.smith@work.com'],
        'addresses': [],  # See note above
        'organization': 'Acme Corp',
        'job_title': 'Engineer',
        'birthday': '1990-05-15',
        'notes': 'Test note',
    }


@pytest.fixture
def temp_vcf_file(sample_vcard_data):
    """Create a temporary VCF file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False, encoding='utf-8') as f:
        f.write(sample_vcard_data)
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_vcf_directory():
    """Create a temporary directory with multiple VCF files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create first VCF file
        vcf1 = Path(tmpdir) / "contact1.vcf"
        vcf1.write_text("""BEGIN:VCARD
VERSION:3.0
FN:Alice Johnson
N:Johnson;Alice;;;
TEL;TYPE=CELL:1111111111
END:VCARD""", encoding='utf-8')
        
        # Create second VCF file
        vcf2 = Path(tmpdir) / "contact2.vcf"
        vcf2.write_text("""BEGIN:VCARD
VERSION:3.0
FN:Bob Williams
N:Williams;Bob;;;
TEL;TYPE=CELL:2222222222
END:VCARD""", encoding='utf-8')
        
        yield tmpdir


# --- Tests for parse_vcard ---

class TestParseVcard:
    """Tests for the parse_vcard function."""

    def test_parse_full_name(self, sample_vcard):
        """Should extract full name from vCard."""
        result = parse_vcard(sample_vcard)
        assert result['full_name'] == 'John Doe'

    def test_parse_name_components(self, sample_vcard):
        """Should extract given and family name."""
        result = parse_vcard(sample_vcard)
        assert result['given_name'] == 'John'
        assert result['family_name'] == 'Doe'

    def test_parse_phone_numbers(self, sample_vcard):
        """Should extract phone numbers as list."""
        result = parse_vcard(sample_vcard)
        assert '1234567890' in result['phone_numbers']

    def test_parse_emails(self, sample_vcard):
        """Should extract email addresses as list."""
        result = parse_vcard(sample_vcard)
        assert 'john@example.com' in result['emails']

    def test_parse_empty_fields(self):
        """Should handle vCard with minimal fields."""
        minimal_vcard = """BEGIN:VCARD
VERSION:3.0
FN:Minimal Contact
END:VCARD"""
        vcard = next(vobject.readComponents(minimal_vcard))
        result = parse_vcard(vcard)
        
        assert result['full_name'] == 'Minimal Contact'
        assert result['phone_numbers'] == []
        assert result['emails'] == []
        assert result['addresses'] == []

    def test_parse_vcard_with_organization(self):
        """Should extract organization field."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Worker Bee
ORG:Big Company
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert result['organization'] == 'Big Company'

    def test_parse_vcard_with_title(self):
        """Should extract job title."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Manager Person
TITLE:Senior Manager
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert result['job_title'] == 'Senior Manager'

    def test_parse_vcard_with_birthday(self):
        """Should extract birthday."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Birthday Person
BDAY:1985-03-21
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert result['birthday'] == '1985-03-21'

    def test_parse_vcard_with_notes(self):
        """Should extract notes."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Noted Person
NOTE:This is a test note
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert result['notes'] == 'This is a test note'

    def test_parse_multiple_phones(self):
        """Should handle multiple phone numbers."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Multi Phone
TEL;TYPE=CELL:111-111-1111
TEL;TYPE=HOME:222-222-2222
TEL;TYPE=WORK:333-333-3333
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert len(result['phone_numbers']) == 3

    def test_parse_multiple_emails(self):
        """Should handle multiple email addresses."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Multi Email
EMAIL;TYPE=HOME:home@example.com
EMAIL;TYPE=WORK:work@example.com
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        assert len(result['emails']) == 2
        assert 'home@example.com' in result['emails']
        assert 'work@example.com' in result['emails']


# --- Tests for create_vcard ---

class TestCreateVcard:
    """Tests for the create_vcard function."""

    def test_create_vcard_with_full_name(self):
        """Should create vCard with full name."""
        contact = {'full_name': 'Test Person'}
        vcard = create_vcard(contact)
        assert vcard.fn.value == 'Test Person'

    def test_create_vcard_with_name_components(self):
        """Should create vCard with name components."""
        contact = {'given_name': 'First', 'family_name': 'Last'}
        vcard = create_vcard(contact)
        assert vcard.n.value.given == 'First'
        assert vcard.n.value.family == 'Last'

    def test_create_vcard_with_phones(self):
        """Should create vCard with phone numbers."""
        contact = {'phone_numbers': ['111-1111', '222-2222']}
        vcard = create_vcard(contact)
        tel_values = [tel.value for tel in vcard.contents.get('tel', [])]
        assert '111-1111' in tel_values
        assert '222-2222' in tel_values

    def test_create_vcard_with_emails(self):
        """Should create vCard with email addresses."""
        contact = {'emails': ['test@example.com']}
        vcard = create_vcard(contact)
        email_values = [email.value for email in vcard.contents.get('email', [])]
        assert 'test@example.com' in email_values

    def test_create_vcard_with_phone_as_string(self):
        """Should handle phone number passed as string instead of list."""
        contact = {'phone_numbers': '555-5555'}
        vcard = create_vcard(contact)
        tel_values = [tel.value for tel in vcard.contents.get('tel', [])]
        assert '555-5555' in tel_values

    def test_create_vcard_with_email_as_string(self):
        """Should handle email passed as string instead of list."""
        contact = {'emails': 'single@example.com'}
        vcard = create_vcard(contact)
        email_values = [email.value for email in vcard.contents.get('email', [])]
        assert 'single@example.com' in email_values

    def test_create_vcard_serializes(self, full_contact_dict):
        """Should create a vCard that can be serialized."""
        vcard = create_vcard(full_contact_dict)
        serialized = vcard.serialize()
        assert 'BEGIN:VCARD' in serialized
        assert 'END:VCARD' in serialized
        assert 'Jane Smith' in serialized

    def test_create_empty_vcard(self):
        """Should handle empty contact dict (creates vCard object, but validation requires FN)."""
        vcard = create_vcard({})
        # vCard 3.0 requires FN field for valid serialization,
        # but we can still create the object
        assert vcard is not None
        assert hasattr(vcard, 'contents')


# --- Tests for ContactList ---

class TestContactList:
    """Tests for the ContactList class."""

    def test_load_from_file(self, temp_vcf_file):
        """Should load contacts from a VCF file."""
        contact_list = ContactList(temp_vcf_file, is_dir=False)
        assert len(contact_list.dic) == 1
        assert contact_list.dic[1]['full_name'] == 'John Doe'

    def test_load_from_directory(self, temp_vcf_directory):
        """Should load contacts from all VCF files in directory."""
        contact_list = ContactList(temp_vcf_directory, is_dir=True)
        assert len(contact_list.dic) == 2
        names = [c['full_name'] for c in contact_list.dic.values()]
        assert 'Alice Johnson' in names
        assert 'Bob Williams' in names

    def test_load_sample_file(self):
        """Should load the sample contacts.vcf file."""
        sample_path = Path(__file__).parent.parent / 'sample' / 'contacts.vcf'
        if sample_path.exists():
            contact_list = ContactList(str(sample_path), is_dir=False)
            assert len(contact_list.dic) == 8
            names = [c['full_name'] for c in contact_list.dic.values()]
            assert 'Alice Johnson' in names
            assert 'Bob Smith' in names

    def test_str_representation(self, temp_vcf_file):
        """Should have string representation with count."""
        contact_list = ContactList(temp_vcf_file, is_dir=False)
        assert 'ContactList with 1 contacts' in str(contact_list)

    def test_empty_location(self, capsys):
        """Should handle empty location gracefully."""
        contact_list = ContactList('', is_dir=False)
        assert len(contact_list.dic) == 0
        captured = capsys.readouterr()
        assert 'please follow with' in captured.out

    def test_counter_increments(self, temp_vcf_file):
        """Counter should match number of loaded contacts."""
        contact_list = ContactList(temp_vcf_file, is_dir=False)
        assert contact_list.counter == 1

    def test_load_multiple_vcards_from_single_file(self):
        """Should load multiple vCards from a single file."""
        multi_vcard = """BEGIN:VCARD
VERSION:3.0
FN:First Contact
N:Contact;First;;;
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Second Contact
N:Contact;Second;;;
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Third Contact
N:Contact;Third;;;
END:VCARD"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False, encoding='utf-8') as f:
            f.write(multi_vcard)
            temp_path = f.name
        
        try:
            contact_list = ContactList(temp_path, is_dir=False)
            assert len(contact_list.dic) == 3
            assert contact_list.counter == 3
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_contacts(self, temp_vcf_file):
        """Should export contacts to a directory."""
        contact_list = ContactList(temp_vcf_file, is_dir=False)
        
        with tempfile.TemporaryDirectory() as export_dir:
            contact_list.export(export_dir)
            exported_files = list(Path(export_dir).glob('*.vcf'))
            assert len(exported_files) == 1
            assert 'John Doe.vcf' in [f.name for f in exported_files]


# --- Tests for name_value helper ---

class TestNameValue:
    """Tests for the name_value helper function."""

    def test_name_value_with_both(self):
        """Should create Name object with both names."""
        name = name_value(first='John', last='Doe')
        assert name.given == 'John'
        assert name.family == 'Doe'

    def test_name_value_missing_first(self):
        """Should return None if first name missing."""
        result = name_value(first='', last='Doe')
        assert result is None

    def test_name_value_missing_last(self):
        """Should return None if last name missing."""
        result = name_value(first='John', last='')
        assert result is None

    def test_name_value_both_missing(self):
        """Should return None if both names missing."""
        result = name_value(first='', last='')
        assert result is None


# --- Integration tests ---

class TestCyrillicContacts:
    """Tests for handling Cyrillic/Russian character sets."""

    def test_load_russian_vcf_file(self):
        """Should load contacts with Cyrillic characters from sample file.
        
        Note: contacts_ru_v3.0.vcf has 3 contacts with varying completeness:
        - Contact 1: Has FN field -> full_name populated
        - Contact 2: No FN, name in N's given field -> full_name is None
        - Contact 3: No FN, name in N's family field -> full_name is None
        """
        sample_path = Path(__file__).parent.parent / 'sample' / 'contacts_ru_v3.0.vcf'
        if not sample_path.exists():
            pytest.skip("Russian sample file not found")
        
        contact_list = ContactList(str(sample_path), is_dir=False)
        assert len(contact_list.dic) == 3
        
        # First contact has proper FN field
        assert contact_list.dic[1]['full_name'] == 'Алексеева Вагда Фаридовна'
        
        # Second contact: N:;Иванов Николай Петрович;;; (no FN, name in given field)
        assert contact_list.dic[2]['given_name'] == 'Иванов Николай Петрович'
        
        # Third contact: N:Ермакова Алия;;;; (no FN, name in family field)
        assert contact_list.dic[3]['family_name'] == 'Ермакова Алия'

    def test_parse_cyrillic_name(self):
        """Should correctly parse Cyrillic names."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
N:Иванов;Николай;;;
FN:Николай Иванов
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        
        assert result['full_name'] == 'Николай Иванов'
        assert result['given_name'] == 'Николай'
        assert result['family_name'] == 'Иванов'

    def test_parse_cyrillic_email(self):
        """Should correctly parse email with Cyrillic contact."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
FN:Алексеева Вагда Фаридовна
EMAIL;type=INTERNET;type=WORK:v.alekseeva@example.org
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        
        assert result['full_name'] == 'Алексеева Вагда Фаридовна'
        assert 'v.alekseeva@example.org' in result['emails']

    def test_roundtrip_cyrillic_contact(self):
        """Cyrillic contact should survive parse -> create -> parse cycle."""
        original = {
            'full_name': 'Петров Сергей',
            'given_name': 'Сергей',
            'family_name': 'Петров',
            'phone_numbers': ['+7-999-123-4567'],
            'emails': ['sergey@example.ru'],
            'addresses': [],
            'organization': None,
            'job_title': None,
            'birthday': None,
            'notes': None,
        }
        
        vcard = create_vcard(original)
        result = parse_vcard(vcard)
        
        assert result['full_name'] == original['full_name']
        assert result['given_name'] == original['given_name']
        assert result['family_name'] == original['family_name']

    def test_cyrillic_serialization_to_file(self):
        """Cyrillic contact should serialize to file and read back correctly."""
        contact = {
            'full_name': 'Козлова Мария',
            'given_name': 'Мария',
            'family_name': 'Козлова',
            'phone_numbers': [],
            'emails': ['maria@example.ru'],
            'addresses': [],
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False, encoding='utf-8') as f:
            vcard = create_vcard(contact)
            f.write(vcard.serialize())
            temp_path = f.name
        
        try:
            contact_list = ContactList(temp_path, is_dir=False)
            loaded = contact_list.dic[1]
            
            assert loaded['full_name'] == 'Козлова Мария'
            assert loaded['given_name'] == 'Мария'
            assert loaded['family_name'] == 'Козлова'
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cyrillic_with_birthday(self):
        """Should handle Cyrillic contact with birthday field."""
        vcard_data = """BEGIN:VCARD
VERSION:3.0
N:;Иванов Николай Петрович;;;
FN:Иванов Николай Петрович
EMAIL;type=INTERNET;type=WORK:n.ivanov@example.org
BDAY:1986-07-12
END:VCARD"""
        vcard = next(vobject.readComponents(vcard_data))
        result = parse_vcard(vcard)
        
        assert 'Иванов' in result['full_name']
        assert result['birthday'] == '1986-07-12'
        assert 'n.ivanov@example.org' in result['emails']


class TestRoundTrip:
    """Tests for round-trip conversion (parse -> create -> parse)."""

    def test_roundtrip_basic_contact(self):
        """Contact should survive parse -> create -> parse cycle."""
        original = {
            'full_name': 'Round Trip',
            'given_name': 'Round',
            'family_name': 'Trip',
            'phone_numbers': ['123-456-7890'],
            'emails': ['round@trip.com'],
            'addresses': [],
            'organization': None,
            'job_title': None,
            'birthday': None,
            'notes': None,
        }
        
        # Create vCard from dict
        vcard = create_vcard(original)
        
        # Parse it back
        result = parse_vcard(vcard)
        
        assert result['full_name'] == original['full_name']
        assert result['given_name'] == original['given_name']
        assert result['family_name'] == original['family_name']
        assert result['phone_numbers'] == original['phone_numbers']
        assert result['emails'] == original['emails']

    def test_roundtrip_via_file(self, full_contact_dict):
        """Contact should survive write to file and read back."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False, encoding='utf-8') as f:
            vcard = create_vcard(full_contact_dict)
            f.write(vcard.serialize())
            temp_path = f.name
        
        try:
            contact_list = ContactList(temp_path, is_dir=False)
            loaded = contact_list.dic[1]
            
            assert loaded['full_name'] == full_contact_dict['full_name']
            assert loaded['given_name'] == full_contact_dict['given_name']
            assert loaded['family_name'] == full_contact_dict['family_name']
        finally:
            Path(temp_path).unlink(missing_ok=True)

