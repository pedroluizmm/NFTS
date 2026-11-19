"""Mini sistema de arquivos: não lê nem cria volumes NTFS reais."""
import copy
import os
from .disk import Disk
from . import metadata as m, allocation as a

class FileSystem:
    def __init__(self, path):
        self.disk = Disk(path)
        self.state = self.disk.load()
        self.cwd = 0

    @classmethod
    def create(cls, path, block_size=64, block_count=128):
        if block_size <= 0 or block_count <= 0:
            raise ValueError('Tamanho e quantidade de blocos devem ser positivos')
        if os.path.exists(path):
            raise FileExistsError('Disco já existe; escolha outro caminho')
        t = m.now()
        state = {'format':'mini-ntfs-1', 'block_size':block_size, 'blocks':[None]*block_count,
                 'next_id':1, 'entries':{'0':{'id':0,'name':'','parent':None,'type':'dir','created':t,'modified':t}}}
        Disk(path).save(state)
        return cls(path)

    def commit(self, state):
        self.disk.save(state)
        self.state = state

    def get(self, path):
        return m.resolve(self.state, path, self.cwd)

    def create_entry(self, path, kind):
        s = copy.deepcopy(self.state)
        parent, name = m.parent_name(s, path, self.cwd)
        if m.child(s, parent['id'], name):
            raise FileExistsError(path)
        i = s['next_id']; s['next_id'] += 1; t = m.now()
        e = {'id':i,'name':name,'parent':parent['id'],'type':kind,'created':t,'modified':t}
        if kind == 'file': e.update(size=0, blocks=[])
        s['entries'][str(i)] = e; parent['modified'] = t
        self.commit(s)

    def mkdir(self, path): self.create_entry(path, 'dir')
    def touch(self, path): self.create_entry(path, 'file')

    def read(self, path):
        e = self.get(path)
        if e['type'] != 'file': raise IsADirectoryError(path)
        return a.read(self.state, e['blocks'], e['size'])

    def write(self, path, content, append=False):
        if not isinstance(content, bytes): raise TypeError('Conteúdo deve ser bytes')
        s = copy.deepcopy(self.state); e = m.resolve(s, path, self.cwd)
        if e['type'] != 'file': raise IsADirectoryError(path)
        if append: content = a.read(s, e['blocks'], e['size']) + content
        e['blocks'] = a.allocate(s, content, e['blocks']); e['size'] = len(content); e['modified'] = m.now()
        self.commit(s)

    def replace(self, source, destination):
        """Substitui o destino pelo arquivo de origem; consome a origem e seu ID."""
        s = copy.deepcopy(self.state); src = m.resolve(s, source, self.cwd); dst = m.resolve(s, destination, self.cwd)
        if src['type'] != 'file' or dst['type'] != 'file': raise ValueError('Origem e destino devem ser arquivos')
        if src['id'] == dst['id']: raise ValueError('Origem e destino são o mesmo arquivo')
        for i in dst['blocks']: s['blocks'][i] = None
        src['parent'], src['name'], src['modified'] = dst['parent'], dst['name'], m.now()
        del s['entries'][str(dst['id'])]
        self.commit(s)

    def remove(self, path, directory=False):
        s = copy.deepcopy(self.state); e = m.resolve(s, path, self.cwd)
        if e['id'] == 0 or e['id'] == self.cwd: raise ValueError('Não é possível remover a raiz ou diretório atual')
        if directory:
            if e['type'] != 'dir': raise NotADirectoryError(path)
            if any(x['parent'] == e['id'] for x in s['entries'].values()): raise ValueError('Diretório não está vazio')
        elif e['type'] != 'file': raise IsADirectoryError(path)
        for i in e.get('blocks', []): s['blocks'][i] = None
        del s['entries'][str(e['id'])]; self.commit(s)

    def move(self, source, destination):
        s = copy.deepcopy(self.state); e = m.resolve(s, source, self.cwd)
        if e['id'] == 0: raise ValueError('Não é possível mover a raiz')
        try: target = m.resolve(s, destination, self.cwd)
        except FileNotFoundError: target = None
        if target is not None:
            if target['type'] != 'dir': raise FileExistsError(destination)
            parent, name = target, e['name']
        else: parent, name = m.parent_name(s, destination, self.cwd)
        if m.child(s, parent['id'], name): raise FileExistsError(destination)
        p = parent
        while p['parent'] is not None:
            if p['id'] == e['id']: raise ValueError('Não é possível mover diretório para dentro de si')
            p = s['entries'][str(p['parent'])]
        e.update(parent=parent['id'], name=name, modified=m.now()); self.commit(s)

    def rename(self, path, name):
        if not name or name in ('.','..') or '/' in name or '\\' in name: raise ValueError('Informe apenas um nome válido')
        e = self.get(path); parent = self.path_of(e['parent']) if e['parent'] is not None else '/'
        self.move(path, parent.rstrip('/') + '/' + name)

    def path_of(self, i):
        parts = []
        while i != 0:
            e = self.state['entries'][str(i)]; parts.append(e['name']); i = e['parent']
        return '/' + '/'.join(reversed(parts))

    def ls(self, path='.'):
        e = self.get(path)
        if e['type'] != 'dir': raise NotADirectoryError(path)
        return sorted((x for x in self.state['entries'].values() if x['parent'] == e['id']), key=lambda x:x['name'])

    def status(self):
        total = len(self.state['blocks']); used = sum(b is not None for b in self.state['blocks'])
        return {'block_size':self.state['block_size'], 'total':total, 'used':used, 'free':total-used}
