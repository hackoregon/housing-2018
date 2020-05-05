import pandas as pd
import os
from data.loaders.django_import import DjangoImport
from api.models import Policy, Program
import boto3

class PolicyImport(DjangoImport):
    django_model = Policy

    def process_frame(self):
        self.data = pd.read_excel(self.file_loc, sheet_name='Policies')

    def get_queryset(self):
        return self.django_model.objects.all()

    def generate_json(self):
        for ix, row in self.data.iterrows():
            if pd.isnull(row['ID']):
                continue
            body = {
                'policy_id': row['ID'],
                'policy_type': row['Policy_Type'],
                'description': row['Description'],
                'category': row['Category'],
                'link1': row['Link 1'] if pd.notnull(row['Link 1']) else None,
                'link1_name': row['Link 1 Name'] if pd.notnull(row['Link 1 Name']) else None,
                'link2': row['Link 2'] if pd.notnull(row['Link 2']) else None,
                'link2_name': row['Link 2 Name'] if pd.notnull(row['Link 2 Name']) else None,
                'link3': row['Link 3'] if pd.notnull(row['Link 3']) else None,
                'link3_name': row['Link 3 Name'] if pd.notnull(row['Link 3 Name']) else None,
            }
            yield body

class ProgramImport(DjangoImport):
    django_model = Program

    def process_frame(self):
        self.data = pd.read_excel(self.file_loc, sheet_name='Program Inventory')
        self.data = self.data[pd.notnull(self.data['Policy_ID'])]

    def get_queryset(self):
        return self.django_model.objects.all()

    def generate_json(self):
        for ix, row in self.data.iterrows():
            try:
                name = row['Program_Name'].strip()
                if name.lower() == 'none':
                    name = None
            except:
                name = None
            
            try:
                desc = row['Program_Description'].strip()
                if desc.lower() == 'none':
                    desc = None
            except:
                desc = None

            try:
                time = row['Time']
                time = int(time)
            except:
                time = None
            
            try:
                policy = Policy.objects.get(pk=row['Policy_ID'])
            except:
                print(row['Policy_ID'])
                continue

            body = {
                'policy': policy,
                'name': name,
                'description': desc,
                'government_entity': row['Government_Entity'],
                'year_implemented': time,
                'link1': row['Link to program'] if pd.notnull(row['Link to program']) else None,
                'link1_name': row['Link 1 Name'] if pd.notnull(row['Link 1 Name']) else None,
                'link2': row['Link to program 2'] if pd.notnull(row['Link to program 2']) else None,
                'link2_name': row['Link 2 Name'] if pd.notnull(row['Link 2 Name']) else None,
            }
            yield body


def load_data():
    BUCKET_NAME = 'hacko-cdn'
    KEY = '2018-housing-affordability/data/'
    s3 = boto3.resource('s3')

    f = 'housing-framework.xlsx'
    file_path = '/data/{}'.format(f)
    if not os.path.isfile(file_path):
        key = KEY + f
        s3.Bucket(BUCKET_NAME).download_file(key, file_path)

    with pd.ExcelFile(file_path) as xlsx:
        policies = PolicyImport(file_loc=xlsx)
        programs = ProgramImport(file_loc=xlsx)

        policies.save()
        programs.save()
    
