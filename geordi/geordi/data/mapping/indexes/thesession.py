from ..rule import Rule

thesession = {
    'release': [Rule(['recording'], ['release_group', 'name']),
                Rule(['recording'], ['release', 'name']),
                Rule(['tracks', ('t_index', True)],
                     lambda *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'name'],
                     transform=lambda val, *args, **kwargs: ' / '.join(v for (k,v) in sorted(val.items()))),
                Rule(['artist'], ['release', 'artists', 'unsplit'])
                ]
}
