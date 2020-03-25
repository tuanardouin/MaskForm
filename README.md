# MaskForm

This script is used to create a database of coordinates of a pdf file.

## Installation

```bash
git clone https://github.com/tuanardouin/MaskForm.git
cd MaskForm
virtualenv .venv
source .venv/bin/activate
pip install -R requierement.txt
```

## Usage

First you need to transform your PDF template into a jpg.

```python
python mask.py -p template.pdf
```

The script takes a list of labels to process in input. Thoses labels should be listed in a file, separated by a comma.
You should create one label file per page in your initial pdf.

```
label1,label2,label3,label4
```

Once your label file created you can start processing them.


```python
python mask.py -i template.pdf_page1.jpg -l list_of_labels.txt
```

Inside the script those are command you can use :

V -> Validate the zone selected

R -> Erase the current zone

C -> No save exit

P -> Write the current coordinates selected and exit (You need to erase them from the label file if you continu later)
