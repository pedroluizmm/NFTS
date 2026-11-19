"""Alocação first-fit de blocos fixos, codificados em base64 no disco."""
import base64
import math

def read(state, blocks, size):
    return b''.join(base64.b64decode(state['blocks'][i]) for i in blocks)[:size]

def allocate(state, content, old):
    size = state['block_size']
    need = math.ceil(len(content) / size)
    free = [i for i, b in enumerate(state['blocks']) if b is None or i in old]
    if need > len(free):
        raise ValueError('Espaço insuficiente no disco virtual')
    chosen = free[:need]
    for i in old:
        state['blocks'][i] = None
    for n, i in enumerate(chosen):
        chunk = content[n*size:(n+1)*size]
        state['blocks'][i] = base64.b64encode(chunk).decode('ascii')
    return chosen
