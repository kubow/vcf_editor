# -*- coding: utf-8 -*-
"""Streamlit GUI for VCF contact editor - matching tkinter layout exactly."""

import streamlit as st
from pathlib import Path
from Contact import ContactList, create_vcard, parse_vcard, quoted_printable, smash_it

try:
    import vobject
except ImportError:
    raise Exception('Cannot work with VCF contacts, please install vobject')


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'contacts_lib': None,
        'active_index': 0,
        'location': '',
        'mode': 'Directory',
        'uploaded_mode': False,
        'show_file_input': True,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def load_contacts(path: str, is_dir: bool):
    """Load contacts from file or directory."""
    try:
        st.session_state.contacts_lib = ContactList(path, is_dir=is_dir)
        st.session_state.location = path
        st.session_state.active_index = 1 if st.session_state.contacts_lib.dic else 0
        st.session_state.uploaded_mode = False
        st.session_state.show_file_input = False
        return True
    except Exception as e:
        st.error(f"Error loading: {e}")
        return False


def load_from_uploaded_files(uploaded_files):
    """Load contacts from uploaded VCF files."""
    try:
        st.session_state.contacts_lib = ContactList('', is_dir=False)
        st.session_state.contacts_lib.dic = {}
        st.session_state.contacts_lib.counter = 0
        
        for uploaded_file in uploaded_files:
            content = uploaded_file.read().decode('utf-8')
            for vcard in vobject.readComponents(content, allowQP=True):
                contact = parse_vcard(vcard)
                st.session_state.contacts_lib.counter += 1
                st.session_state.contacts_lib.dic[st.session_state.contacts_lib.counter] = contact
        
        st.session_state.location = f'Uploaded: {len(uploaded_files)} file(s)'
        st.session_state.active_index = 1 if st.session_state.contacts_lib.dic else 0
        st.session_state.uploaded_mode = True
        st.session_state.show_file_input = False
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def get_display_name(contact: dict) -> str:
    """Get display name for a contact."""
    if contact.get('full_name'):
        return contact['full_name']
    elif contact.get('given_name') or contact.get('family_name'):
        return f"{contact.get('given_name', '')} {contact.get('family_name', '')}".strip()
    return "Unknown"


def run():
    """Main Streamlit application - clean tkinter-style layout."""
    st.set_page_config(page_title="VCF Contact Editor", page_icon="📇", layout="wide")
    init_session_state()
    
    # ==================== HEADER ====================
    st.title("VCF contact editor")
    
    # ==================== ROW 1: Location + Mode Switcher ====================
    col_loc, col_mode = st.columns([3, 1])
    
    with col_loc:
        loc = st.session_state.location or '(no file loaded)'
        st.text(f"Location: {loc}")
    
    with col_mode:
        prev_mode = st.session_state.mode
        mode = st.radio("Mode:", ['Directory', 'File'], 
                       index=0 if st.session_state.mode == 'Directory' else 1,
                       horizontal=True)
        # Mode change triggers file picker (like tkinter)
        if mode != prev_mode:
            st.session_state.mode = mode
            st.session_state.show_file_input = True
            st.rerun()
        st.session_state.mode = mode
    
    # ==================== ROW 2: Button Menu ====================
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        if st.button("open", use_container_width=True):
            st.session_state.show_file_input = True
            st.rerun()
    
    with c2:
        if st.button("export", use_container_width=True):
            pass  # Handled below if contacts exist
    
    with c3:
        if st.button("<", use_container_width=True):
            if st.session_state.contacts_lib and st.session_state.active_index > 1:
                st.session_state.active_index -= 1
                st.rerun()
    
    with c4:
        save_clicked = st.button("save", use_container_width=True)
    
    with c5:
        if st.button(">", use_container_width=True):
            if st.session_state.contacts_lib and st.session_state.active_index < len(st.session_state.contacts_lib.dic):
                st.session_state.active_index += 1
                st.rerun()
    
    with c6:
        if st.button("quit", use_container_width=True):
            st.info("Close browser tab to exit")
    
    # ==================== FILE PICKER (shown when triggered) ====================
    if st.session_state.show_file_input:
        st.divider()
        
        # File uploader - the "dialog" in web context
        help_text = "Drop VCF file here" if st.session_state.mode == 'File' else "Drop VCF files here (folder contents)"
        uploaded = st.file_uploader(
            help_text,
            type=['vcf'],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.mode}"
        )
        
        if uploaded:
            if load_from_uploaded_files(uploaded):
                st.rerun()
    
    st.divider()
    
    # ==================== EXPORT DOWNLOAD (if contacts exist) ====================
    if st.session_state.contacts_lib and st.session_state.contacts_lib.dic:
        with st.container():
            all_vcards = '\n'.join([create_vcard(c).serialize() for c in st.session_state.contacts_lib.dic.values()])
            st.download_button("⬇️ Download All Contacts", all_vcards, "contacts_export.vcf", "text/vcard")
    
    # ==================== MAIN CONTENT: List + Form ====================
    contacts = st.session_state.contacts_lib.dic if st.session_state.contacts_lib else {}
    
    col_list, col_form = st.columns([1, 2])
    
    # LEFT: Contact List
    with col_list:
        if contacts:
            options = [f"{idx}. {get_display_name(c)}" for idx, c in contacts.items()]
            current = st.session_state.active_index - 1 if st.session_state.active_index > 0 else 0
            current = min(current, len(options) - 1) if options else 0
            
            selected = st.selectbox("Contacts", options, index=current, label_visibility="collapsed")
            if selected:
                new_idx = int(selected.split('.')[0])
                if new_idx != st.session_state.active_index:
                    st.session_state.active_index = new_idx
                    st.rerun()
        else:
            # Empty list placeholder
            st.selectbox("Contacts", ["(no contacts)"], disabled=True, label_visibility="collapsed")
    
    # RIGHT: Form
    with col_form:
        # Get current contact or empty for new
        if contacts and st.session_state.active_index in contacts:
            current = contacts[st.session_state.active_index]
        else:
            current = {}
        
        form = {}
        form['full_name'] = st.text_input("full_name", value=current.get('full_name') or '')
        form['given_name'] = st.text_input("given_name", value=current.get('given_name') or '')
        form['family_name'] = st.text_input("family_name", value=current.get('family_name') or '')
        
        phones = current.get('phone_numbers', [])
        form['phone_numbers'] = st.text_input("phone_numbers", 
            value=', '.join(phones) if isinstance(phones, list) else (phones or ''))
        
        emails = current.get('emails', [])
        form['emails'] = st.text_input("emails",
            value=', '.join(emails) if isinstance(emails, list) else (emails or ''))
        
        addrs = current.get('addresses', [])
        form['addresses'] = st.text_input("addresses",
            value='; '.join(addrs) if isinstance(addrs, list) else (addrs or ''))
        
        form['organization'] = st.text_input("organization", value=current.get('organization') or '')
        form['job_title'] = st.text_input("job_title", value=current.get('job_title') or '')
        form['birthday'] = st.text_input("birthday", value=current.get('birthday') or '')
        form['notes'] = st.text_area("notes", value=current.get('notes') or '')
        
        # Handle SAVE
        if save_clicked:
            packed = {
                'full_name': form['full_name'] or f"{form['given_name']} {form['family_name']}".strip(),
                'given_name': form['given_name'],
                'family_name': form['family_name'],
                'phone_numbers': [p.strip() for p in form['phone_numbers'].split(',') if p.strip()],
                'emails': [e.strip() for e in form['emails'].split(',') if e.strip()],
                'addresses': [a.strip() for a in form['addresses'].split(';') if a.strip()],
                'organization': form['organization'],
                'job_title': form['job_title'],
                'birthday': form['birthday'],
                'notes': form['notes'],
            }
            
            if not packed['full_name']:
                st.warning("Enter at least a name")
            else:
                vcard = create_vcard(packed)
                vcf_data = vcard.serialize()
                st.download_button("⬇️ Download contact", vcf_data, 
                                 f"{packed['full_name']}.vcf", "text/vcard",
                                 use_container_width=True)


if __name__ == '__main__':
    run()
