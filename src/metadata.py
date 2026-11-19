"""Tabela de registros e resolução de caminhos."""
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def child(state, parent, name):
    return next((e for e in state['entries'].values() if e['parent'] == parent and e['name'] == name), None)

def resolve(state, path, cwd=0):
    if not path:
        raise ValueError('Caminho vazio')
    current = 0 if path.startswith('/') else cwd
    for part in path.split('/'):
        if not part or part == '.':
            continue
        entry = state['entries'][str(current)]
        if entry['type'] != 'dir':
            raise NotADirectoryError(path)
        if part == '..':
            current = entry['parent'] if entry['parent'] is not None else 0
        else:
            found = child(state, current, part)
            if found is None:
                raise FileNotFoundError(path)
            current = found['id']
    return state['entries'][str(current)]

def parent_name(state, path, cwd=0):
    path = path.rstrip('/')
    if not path:
        raise ValueError('A raiz não pode ser alterada')
    prefix, sep, name = path.rpartition('/')
    if name in ('', '.', '..') or '\\' in name:
        raise ValueError('Nome inválido')
    parent = resolve(state, (prefix or '/') if sep else '.', cwd)
    if parent['type'] != 'dir':
        raise NotADirectoryError(prefix)
    return parent, name
