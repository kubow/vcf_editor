# Architecture & Common Logic

This document describes the shared logic between Tkinter and Streamlit interfaces.

## Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Contact.py                              │
│  (Shared library - no GUI dependencies)                        │
├─────────────────────────────────────────────────────────────────┤
│  • ContactList       - Load/manage VCF contacts                 │
│  • parse_vcard()     - VCard → Python dict                      │
│  • create_vcard()    - Python dict → VCard                      │
│  • quoted_printable()- Encoding for special characters          │
│  • smash_it()        - Delete file safely                       │
└─────────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐      ┌─────────────────────────┐
│   gui_tkinter.py    │      │    gui_streamlit.py     │
│   (Desktop GUI)     │      │    (Web GUI)            │
└─────────────────────┘      └─────────────────────────┘
```

## File/Folder Dialog Logic

### Tkinter Behavior

The Tkinter interface uses native OS dialogs:

```python
def set_dir(self):
    """Called when Directory radio button is selected"""
    self.browse_dir()  # Opens dialog immediately
    self.refresh()

def set_file(self):
    """Called when File radio button is selected"""
    self.browse_dir()  # Opens dialog immediately
    self.refresh()

def browse_dir(self):
    """Opens appropriate dialog based on mode"""
    if self.active['mode'].get():  # File mode
        self.active['location'] = askopenfilename()  # File picker
        is_dir = False
    else:  # Directory mode
        self.active['location'] = askdirectory()     # Folder picker
        is_dir = True
    
    if self.active['location']:
        self.contacts_lib = ContactList(self.active['location'], is_dir=is_dir)
```

**Key behaviors:**
1. Mode switch → Dialog opens automatically
2. Open button → Dialog opens based on current mode
3. Dialog type matches mode (file picker vs folder picker)

### Streamlit Behavior

Web browsers cannot trigger native file dialogs programmatically. Streamlit uses:

```python
def on_mode_change():
    """When mode changes, show the file uploader"""
    st.session_state.show_open_dialog = True  # Auto-expand uploader

# Mode selection triggers dialog
mode = st.radio("Mode", ['Directory', 'File'], on_change=on_mode_change)

# File uploader (browser's file picker)
uploaded_files = st.file_uploader("Choose VCF files", accept_multiple_files=True)
```

**Adaptations for web:**
1. Mode switch → Expands file uploader section automatically
2. Upload button → User clicks to trigger browser's file picker
3. Both modes use file uploader (folders can't be uploaded in browsers)
4. Alternative: Enter local path (works when running Streamlit locally)

## Common Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Open/Upload │ ──▶ │ ContactList  │ ──▶ │   Display    │
│  VCF files   │     │   .dic{}     │     │   in list    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Export    │ ◀── │ create_vcard │ ◀── │  Edit form   │
│   VCF files  │     │   (dict→vcf) │     │   changes    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Session State (Streamlit)

```python
st.session_state = {
    'contacts_lib': ContactList,  # The loaded contacts
    'active_index': int,          # Currently selected contact (1-based)
    'location': str,              # File/folder path or "Uploaded"
    'mode': str,                  # 'Directory' or 'File'
    'uploaded_mode': bool,        # True if loaded from upload (can't save back)
    'show_open_dialog': bool,     # Controls dialog visibility
}
```

## Platform Differences

| Feature | Tkinter | Streamlit |
|---------|---------|-----------|
| File dialog | Native OS picker | Browser file upload |
| Folder dialog | Native OS picker | Multiple file upload or path input |
| Auto-open on mode switch | ✅ Native dialog | ✅ Expands uploader section |
| Save to original file | ✅ Direct write | ⚠️ Only for local paths |
| Export/Download | Write to folder | Download button + local export |

