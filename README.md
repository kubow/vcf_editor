# vcf editor

Python GUI for VCF parsing and editing

Designed for fast use.  Security not implemented.

Depend on these python3 modules:

- [os (built-in)](https://docs.python.org/3/library/os.html)
- [difflib (built-in)](https://docs.python.org/3/library/difflib.html?highlight=difflib#module-difflib)
- [TkInter](https://docs.python.org/3/library/tkinter.html?highlight=tkinter#module-tkinter)
- [VObject](https://eventable.github.io/vobject/)

## To do

- Rebuild ContactList class (property dic will hold actual vobjects)
- Loading contact cards with special character sets (tested only utf-8 + win1250)
- Phones sanizitation
- Extend with contact details (picture, adresses, etc)

## Resources (backup for now)
### TkInter
https://www.tutorialkart.com/python/tkinter/entry/

### VCF

- [Vobject github source](https://github.com/eventable/vobject)
- [Vobject documentation](http://eventable.github.io/vobject/)
- [Vobject usage old](http://vobject.skyhouseconsulting.com/usage.html)
- [Vobject vcard definition](https://github.com/eventable/vobject/blob/master/vobject/vcard.py)
- [VCF Fields Definition (N section)](https://datatracker.ietf.org/doc/html/rfc6350#section-6.2.2)
- [VCF File Definition](https://docs.fileformat.com/email/vcf/)
- [VCF Linux Tools](https://github.com/vcftools/vcftools)
- [Error VCF Parsing](https://stackoverflow.com/questions/38410742/error-in-parsing-vcard-file-using-python-vobject-package)
### Encoding to hexa-chars
- [Encoding/Decoding to Quoted printable](https://www.webatic.com/quoted-printable-convertor)
- [ASCII to HEX](https://stackoverflow.com/questions/35536670/how-to-convert-ascii-to-hex-in-python)
- [convert string to bytes](https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3#17500651)
- [built-in qoupri module](https://docs.python.org/3/library/quopri.html)