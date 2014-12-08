""" TheSession.org is a website focused on Celtic music.

Database downloads are available from: https://github.com/adactio/TheSession-data
"""

import os.path, json, csv

from flask.ext.script import Manager

def add_while_checking_for_inconsistent_values(name, rec, row, id_key='id'):
    val = rec.setdefault(name, row[name])
    if val != row[name]:
        raise ValueError("Inconsistent %s names for id#%s: \"%s\" != \"%s\"" %
                         (name, row[id_key], val, row[name]))

def convert_dict_to_array(obj, idx, initial=1):
    d=obj[idx]
    itms = sorted((int(k), v) for (k,v) in d.items())
    keys = [k for (k,v) in itms]
    if len(d) != max(keys)-initial+1:
        raise ValueError("Wrong number of items in: "+str(keys))
    if keys != range(initial, len(d)+initial):
        raise ValueError("Wrong key in: "+str(d))
    obj[idx] = [v for (k,v) in itms]

def read_csv(path, filename, limit, process_func):
    """Read a CSV file and process each row.

    The process_func() takes a dict containing the values in the row, and
    returns a count of entries for use by the limit param."""
    with open(os.path.join(path, filename)) as csvfile:
        for row in csv.DictReader(csvfile, escapechar='\\'):
            current_count = process_func(row)
            if limit != None and current_count >= int(limit):
                break

def thesession_setup(add_folder, add_data_item, import_manager):
    def add_data_items_from_dict(key_prefix, item_type, name_column, data_dict):
        for k, v in data_dict.items():
            item_id = add_data_item(key_prefix+k, item_type, json.dumps(v, separators=(',', ':'), sort_keys=True))
            print item_id, ':', v[name_column]

    manager = Manager(usage="Import data from CSV files provided by TheSession.org.")
    import_manager.add_command('thesession', manager)

    @manager.command
    def recordings(path_to_csv_files, filename='recordings.csv', limit=None):
        """Import recordings as Releases"""
        print 'Importing recordings...'
        recordings = {}
        def process_func(row):
            rec = recordings.setdefault(row['id'], {})

            add_while_checking_for_inconsistent_values('recording', rec, row)
            add_while_checking_for_inconsistent_values('artist', rec, row)

            rec_track = rec.setdefault('tracks', {}).setdefault(row['track'], {})
            if rec_track.has_key(row['number']):
                raise ValueError("Duplicate track/number entry for id#%s: %s/%s" %
                                 (row['id'], row['track'], row['number']))
            rec_track[row['number']] = row['tune']

            return len(recordings)

        read_csv(path_to_csv_files, filename, limit, process_func)

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
        add_data_items_from_dict('thesession/release/', 'release', 'recording', recordings)

    @manager.command
    def tunes(path_to_csv_files, filename='tunes.csv', limit=None):
        """Import tunes as Works."""
        print 'Importing tunes ...'
        tunes = {}
        def process_func(row):
            tune = tunes.setdefault(row['tune'], {})
            add_while_checking_for_inconsistent_values('name', tune, row, 'setting')
            add_while_checking_for_inconsistent_values('type', tune, row, 'setting')

            settings = tune.setdefault('settings', {})
            if settings.has_key(row['setting']):
                raise ValueError('Duplicate setting ids: '+repr(row))

            settings[row['setting']]={k:row[k] for k in row.keys() if k not in ('tune', 'setting', 'name', 'type')}

            return len(tunes)

        read_csv(path_to_csv_files, filename, limit, process_func)
        add_data_items_from_dict('thesession/tune/', 'work', 'name', tunes)

    @manager.command
    def events(path_to_csv_files, filename='events.csv', limit=None):
        """Import events as, well, Events."""
        print 'Importing events ...'
        events = {}
        def process_func(row):
            events[row['id']]={k:row[k] for k in row.keys() if k != 'id'}
            return len(events)

        read_csv(path_to_csv_files, filename, limit, process_func)
        add_data_items_from_dict('thesession/event/', 'event', 'event', events)

    @manager.command
    def sessions(path_to_csv_files, filename='sessions.csv', limit=None):
        """Import sessions as Places."""
        print 'Importing sessions ...'
        sessions = {}
        def process_func(row):
            sessions[row['id']]={k:row[k] for k in row.keys() if k != 'id'}
            return len(sessions)

        read_csv(path_to_csv_files, filename, limit, process_func)
        add_data_items_from_dict('thesession/session/', 'place', 'name', sessions)

    @manager.command
    def all(path_to_csv_files):
        """Import all data."""
        recordings(path_to_csv_files)
        tunes(path_to_csv_files)
        events(path_to_csv_files)
        sessions(path_to_csv_files)
