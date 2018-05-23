class DjangoImport(object):
    django_model = None

    def __init__(self, file_loc):
        """
        Base class to import data from an Excel sheet or csv into database via Django ORM.
        
        Parameters:
            file_loc: file path or pandas ExcelFile object that contains the sheets
        """
        self.data = None
        self.file_loc = file_loc
    
    def process_frame(self):
        """
        Process the dataframe created by pandas.read_excel into the desired format for import and set to self.df
        """
        raise NotImplementedError("process_frame must be implemented by child class.")
        
    def generate_objects(self):
        """
        Generator function to create Django objects to save to the database. Takes the json generated from 
        self.generate_json and creates objects out of it.
        """
        for body in self.generate_json():
            obj = self.django_model(**body)
            yield obj

    def get_queryset(self):
        """
        Returns all objects that come from this particular import e.g. for sheet A-1 import it will return all objects with source A-1
        """
        raise NotImplementedError("get_queryset must be implemented by child class.")
                
    def generate_json(self):
        raise NotImplementedError("generate_json must be implemented by child class.")

    def save(self, delete_existing=True, query=None):
        """
        Adds the dataframe to the database via the Django ORM using self.generate_objects to generate Django objects.

        Returns: Number of records added to database.
        
        Parameters:
            delete_existing: option to delete the existing items for this import
            query: Django Q object filter of objects to know what to delete before import.
        """
        if self.data is None:
            self.process_frame()
        if self.data is None:
            raise Exception("self.df has not been set, nothing to add to database.")
            
        if delete_existing:
            if query is None:
                qs = self.get_queryset()
            else:
                qs = django_model.objects.filter(query)
            # delete existing items in index
            qs.delete()

        results = self.django_model.objects.bulk_create(self.generate_objects(), batch_size=10000)
        return len(results)
        
    def is_valid_decimal(self, val):
        """
        Tests whether a number is a valid Decimal value that is not null.
        """
        try:
            d = Decimal(val)
            if pd.isnull(val):
                return False
            return True
        except:
            return False
