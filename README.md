# vcf editor

Python GUI for VCF parsing and editing

Designed for fast use.  Security not implemented.

Prepare environment:

```shell
python -m venv venv
source ./venv/bin/activate
venv/Script/activate #windows way
pip install -r requirements.txt
```

Then running a corresponding file will trigger an action:

```shell
python Contact.py  # batch vcf processing
python main.py  # tkinter interface
```

![user_interface](./screenshot.png)

## To do

- Loading contact cards with special character sets (tested only utf-8 + win1250)
- Phones sanizitation
- Improve TkInter

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
- [python encodings guide](https://realpython.com/python-encodings-guide/)
- [built-in qoupri module](https://docs.python.org/3/library/quopri.html)
- [special ASCII characters](http://www.addressmunger.com/special_ascii_characters/)
- [UTF-8 charcter table](https://www.utf8-chartable.de/)