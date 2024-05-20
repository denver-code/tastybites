# Using PyBabel

### To get all strings for translation:
```bash
pybabel extract -F babel.cfg -o ./messages.pot .

```

### To run the po file (first time):
```bash
pybabel init -i ./messages.pot -d ./translations -l en

```

### There is a po file for the update:

```bash
pybabel update -i ./messages.pot -d ./translations

```

### To compile a po file for mo:

```bash
pybabel compile -f -d ./translations

```