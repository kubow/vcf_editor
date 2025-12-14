# -*- coding: utf-8 -*-
"""
VCF Contact Editor - Main Launcher

Run with:
    python main.py          # Tkinter GUI (default)
    python main.py --tk     # Tkinter GUI
    python main.py --st     # Streamlit GUI (launches via subprocess)
    
Or run interfaces directly:
    python gui_tkinter.py
    streamlit run gui_streamlit.py
"""

import sys
import subprocess


def main():
    """Launch the appropriate GUI based on command line arguments."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ('--st', '--streamlit', '-s'):
            print("Launching Streamlit interface...")
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'gui_streamlit.py'])
        elif arg in ('--tk', '--tkinter', '-t'):
            print("Launching Tkinter interface...")
            from gui_tkinter import run
            run()
        elif arg in ('--help', '-h'):
            print(__doc__)
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
    else:
        # Default to Tkinter
        from gui_tkinter import run
        run()


if __name__ == '__main__':
    main()
