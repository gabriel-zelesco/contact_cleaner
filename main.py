import os
from datetime import datetime
import time

import pandas as pd
from unidecode import unidecode


columns = ['timestamp', 'nome', 'cel', 'email', 'bairro',
           'regiao', 'interesse', 'outros_interesses', 'lgpd', 'matriz']

class ContactList:
    def __init__(self, output: str = "cleaned", encoding: str = "latin1",):
        # Generates path to base directory
        base_dir = os.getcwd()       
        
        # Self
        self.columns = columns
        self.final_columns = ['timestamp','matriz', 'name', 'first_name', 'whatsapp',
                            'valid_num', 'email',  'bairro', 'regiao',
                            'interesse', 'outros_interesses', 'lgpd', 'nome', 'cel']
        self.encoding = encoding
        self.started = datetime.today()
        self.base_dir = base_dir
        self.input = f'{base_dir}'
        self.file = self.__find_filename()
        self.name = self.file[:-5]
        self.export_path = self.__create_dir()
        self.output = f'{self.export_path}/{output}-{self.name}.csv'
    
    def __create_dir(self):
        # Creates directory to export cleaned file
        export_path = (self.input + '/cleaned')
        if os.path.exists(export_path):
            pass
        else:
            os.mkdir(export_path)
        return export_path
    
    def __find_filename(self, suffix=".xlsx"):
        # Finds excel file in the same directory as main.py
        filenames = os.listdir(self.input)
        file_list = [filename for filename in filenames if filename.endswith(suffix)]
        if len(file_list) > 1:
            raise Exception(f'''Há {len(file_list)} arquivos selecionados para limpeza.
                            Só é possível trabalhar com um arquivo por vez.''')
        self.file = file_list[0]
        return self.file
    

    def from_csv(self):
        '''Open csv file and return dataframe without NaNs
        '''
        # Open csv with different encodings and separators
        csv_file = f'{self.input}/{self.file}'
        encoding_list = [open(f'{csv_file}').encoding, self.encoding, 'utf8']
        separetor_list = [',', ';']
        break_out_flag = False
        
        for enco in encoding_list:
            for sep in separetor_list:
                try:
                    df = pd.read_csv(csv_file, sep=sep, encoding=enco, dtype='str', usecols=lambda c: c in set(self.columns))
                    if df.empty:
                        raise Exception('Dataframe is empty.')
                except:
                    print(f'Encoding ({enco}) and separator ({sep}) did not work. Retrying.')
                else:
                    print(f'Encoding ({enco}) and separetor ({sep}) used successfully.')
                    break_out_flag = True
                    break
            if break_out_flag:
                break
        df = df.fillna('no_data')
        return df  
    
    def from_xlsx(self):
        '''Open xlsx file and return dataframe without NaNs
        '''
        # Open xlsx with different encodings and separators
        xlsx_file = f'{self.input}/{self.file}'
        
        try:
            df = pd.read_excel(xlsx_file, dtype='str', usecols=lambda c: c in set(self.columns))
            if df.empty:
                raise Exception('Dataframe is empty.')
        except:
            print(f'Fail to load {xlsx_file}.')

        df = df.fillna('no_data')
        return df
    
    def __string_normalizer(self, string):
        text = unidecode(string)
        return text
    
    def clean_names(self):
        '''Remove accents from names, capitalize first letter and create new column with first name.
        Returns dataframe with new columns.'''
        new_column = []
        for string in self.df['nome']:
            name = self.__string_normalizer(string)
            new_column.append(name)
        self.df = self.df.assign(name = new_column)
        self.df['name'] = self.df['name'].str.title()
        self.df = self.df.assign(first_name = self.df['name'].str.split().str.get(0))
        return self.df
    
    def __clean_column(self, column_name):
        new_column = []
        for string in self.df[column_name]:
            string = self.__string_normalizer(string)
            new_column.append(string)
        self.df = self.df.assign(**{column_name: new_column})
        self.df[column_name] = self.df[column_name].str.lower()
        return self.df
    
    def clean_columns(self):
        '''Remove accents from columns.
        Returns dataframe with new columns.'''
        for column in self.df.columns:
            self.df = self.__clean_column(column)
        return self.df
    
    def __get_DDI(self):
        new_column=[]
        for n in self.df['DDI']:
            try:
                if len(n) == 2:
                    pass
                else:
                    n = '55'
            except:
                n = 'invalid'
            new_column.append(n)
        self.df['DDI'] = new_column
        return self.df
    
    def __get_DDD(self):
        new_column=[]
        for n in self.df['DDD']:
            try:
                if len(n) == 2:
                    pass
                else:
                    n = '21'
            except:
                n = 'invalid'
            new_column.append(n)
        self.df['DDD'] = new_column
        return self.df
    
    def __get_number(self):
        new_column=[]
        for n in self.df['sufix']:
            try:
                if len(n) < 9:
                    n = 'invalid'
                else:
                    n = f"{n}"
            except:
                n = 'invalid'
            new_column.append(n)
        self.df['sufix'] = new_column
        return self.df
    
    def __concat_number(self):
        self.df['DDI'] = '="+' + self.df['DDI']
        self.df['sufix'] = self.df['sufix'] + '"'
        self.df['whatsapp'] = (self.df['DDI'].str.cat(self.df['DDD']).str.cat(self.df['sufix']))
        return self.df
    
    def __valid_numbers(self):
        self.df = self.df.assign(valid_num = ~(self.df['whatsapp'].str.contains('invalid')))
        return self.df
    
    def __drop_columns(self):
        self.df = self.df.drop(columns=['prefix', 'DDI', 'DDD', 'sufix'], axis=1)
        return self.df
    
    
    def clean_numbers(self):
        '''Remove non-numeric characters from numbers,
        create new columns with DDI, DDD and sufix 
        and concatenate them to create a new column with the complete number.
        Returns dataframe with new columns.'''

        self.df = self.df.assign(whatsapp = self.df['cel'].str.replace('\D+', '', regex=True))
        self.df = self.df.assign(prefix = self.df['whatsapp'].str[:-9])
        self.df = self.df.assign(DDI = self.df['prefix'].str[:-2],
                                 DDD = self.df['prefix'].str[-2:],
                                 sufix = self.df['whatsapp'].str[-9:])

        self.df = self.__get_DDI()
        self.df = self.__get_DDD()
        self.df = self.__get_number()
        self.df = self.__concat_number()
        self.df = self.__drop_columns()
        self.df = self.__valid_numbers()
        return self.df
    
    def clean_email(self):
        self.df['email'] = self.df['email'].str.replace(' ','')
        return self.df
    
    def check_existing_columns(self):
        '''Check if columns are in dataframe.
        Returns dataframe with new columns.'''
        for column in self.final_columns:
            if column not in self.df.columns:
                self.df = self.df.assign(**{column: 'no_data'})
        self.df.columns = self.final_columns
        return self.df
    
    def deduplicate(self):
        '''Remove duplicated contacts from dataframe based on whatsapp and email columns.
        Returns dataframe without duplicated contacts.
        '''
        critical_columns = ['whatsapp', 'email', 'interesse']
        self.original_length = len(self.df['name'])
        
        self.duplicated = self.df.duplicated(subset=critical_columns).sum()
        self.df = self.df.drop_duplicates(subset=critical_columns, keep='last')
        return self.df
    
    def report(self):
        '''Prints a report with the number of contacts added and the number
        of duplicated contacts found and removed.
        '''
        self.number_contacts = len(self.df['name'])
        print(f'Fim do script')
        print(f"-" * 30)
        print((f"\n\n"))
        print(f'Arquivo gerado com sucesso em: \n{self.output}.')
        print((f"\n"))
        print(f'{self.original_length} contatos encontrados no arquivo de origem.')
        print(f'{self.number_contacts} contatos adicionados.')
        print(f'{self.duplicated} contatos duplicados encontrados e excluidos.')
        print(f"\n")
        print(f'O critério de exclusão de contatos duplicados foi: \nwhatsapp, email, interesse.')
        print(f'Quando duplicado, foi mantido a última inclusão.')
        print(f'\n')
        print(f'Colunas do arquivo de saída: \n{self.final_columns}')
        print((f"\n\n"))
        print(self.df.head(10))
        print(f"-" * 30)
        print((f"\n\n"))
        time.sleep(2)
    
    
    def save_file(self):
        self.df.to_csv(self.output, header=False, sep=',',encoding='utf8', index = False)
        
        
# Functions   
def output_text():
    '''Prints a welcome message and the current directory.
    '''
    print('ATENÇÃO: Este script deve ser executado no mesmo diretório do arquivo .csv')
    print(f'O arquivo .csv deve conter as colunas: {columns}')
    time.sleep(2)
    print(f'Iniciando script...')
    print(f"-" * 30)
    print((f"\n"))
    print(f'Script rodado em: {os.getcwd()}')
    time.sleep(0.5)
      
def main():
    '''Main function. Creates an instance of ContactList and runs the methods.
    '''
    cl = ContactList()
    cl.df = cl.from_xlsx()
    cl.clean_columns()
    cl.clean_names()   
    cl.clean_numbers()
    cl.clean_email()
    cl.check_existing_columns()
    cl.deduplicate()
    cl.save_file()
    cl.report()
    close = input('Press ENTER to close this window.')
    exit()
      
if __name__ == '__main__':
    output_text()
    main()    
    exit()