import os.path, json, csv

def add_while_checking_for_inconsistent_values(name, rec, row):
    val = rec.setdefault(name, row[name])
    if val != row[name]:
        raise ValueError("Inconsistent %s names for id#%s: \"%s\" != \"%s\"" %
                         (name, row['id'], val, row[name]))

def convert_dict_to_array(obj, idx, initial=1):
    d=obj[idx]
    itms = sorted((int(k), v) for (k,v) in d.items())
    keys = [k for (k,v) in itms]
    if len(d) != max(keys)-initial+1:
        raise ValueError("Wrong number of items in: "+str(keys))
    if keys != range(initial, len(d)+initial):
        raise ValueError("Wrong key in: "+str(d))
    obj[idx] = [v for (k,v) in itms]
    
def thesession_setup(add_folder, add_data_item, import_manager):
    @import_manager.command
    def thesession(path_to_csv_files):
        '''Import data from CSV files provided by TheSession.org'''
        recordings = {}
        with open(os.path.join(path_to_csv_files, 'recordings.csv')) as csvfile:
            for row in csv.DictReader(csvfile):
                rec = recordings.setdefault(row['id'], {})

                add_while_checking_for_inconsistent_values('recording', rec, row)
                add_while_checking_for_inconsistent_values('artist', rec, row)
   
                rec_track = rec.setdefault('tracks', {}).setdefault(row['track'], {})
                if rec_track.has_key(row['number']):
                    raise ValueError("Duplicate track/number entry for id#%s: %s/%s" %
                                     (row['id'], row['track'], row['number']))
                rec_track[row['number']] = row['tune']

        # #Now convert the tracks dicts into arrays, verifying they are not missing any keys.
        # #Too many are, so don't do this, at least for now.
        # for id in recordings:
        #     try:
        #         convert_dict_to_array(recordings[id], 'tracks')
        #         for i in range(len(recordings[id]['tracks'])):
        #             convert_dict_to_array(recordings[id]['tracks'], i)
        #     except ValueError, e:
        #         print "err"+`id`+':'+`e`+'; '+`recordings[id]`
            
        # print json.dumps(dict(recordings.items()[:10]), indent=2)
        for k, v in recordings.items():
            print add_data_item('thesession/release/'+k, 'release', json.dumps(v, separators=(',', ':'), sort_keys=True))
