# Contancts cleaner

This is a simple script to clean your contacts from duplicates and empty fields.
It also returns the phone number of contacts as used in whatsapp.

## Usage

The script is written in python 3.9. It uses the following libraries:
- pandas
- unidecode

## How to use
The script takes no arguments. It reads the .csv file that is in the same directory as the script. The cleaned file is saved in a new directory called "cleaned" and will have the same name as the original file with the prefix "cleaned". The .csv file must have the following columns:
- 'nome' : name of the contact 
- 'cel' : phone number of the contact
- 'email' : email of the contact
- 'timestamp' : timestamp of the generation of the contact

There is an example file in the repository that can be used to test the script.

## Installation
For convenience, there is a environment file that can be used to create a conda environment with the required libraries. To use it, run the following command:
```bash
conda env create -f environment.yml
```
## Making an executable from the script
The script can be made into an executable using pyinstaller. To do so, run the following command with the environment activated:
```bash
pyinstaller --onefile --name=cleaner main.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)