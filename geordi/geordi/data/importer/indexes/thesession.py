import json

def thesession_setup(add_folder, add_data_item, import_manager):
    @import_manager.command
    def thesession(path_to_csv_files):
        '''Import data from CSV files provided by TheSession.org'''
        print 'does nothing, so far'
        pass
