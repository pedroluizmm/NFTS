import argparse
import json
import shlex
from .filesystem import FileSystem

HELP = '''Comandos (caminhos absolutos ou relativos; use aspas para texto):
  mkdir CAMINHO | touch CAMINHO | ls [CAMINHO] | cd CAMINHO | pwd
  write CAMINHO TEXTO    acrescenta texto
  overwrite CAMINHO TEXTO substitui o conteúdo mantendo o ID
  read CAMINHO | rename CAMINHO NOVO_NOME | mv ORIGEM DESTINO
  replace ORIGEM DESTINO substitui o arquivo de destino pela origem
  rm CAMINHO | rmdir CAMINHO (vazio) | info CAMINHO | status | tree
  help | exit'''

def run(fs, line):
    args = shlex.split(line, posix=True)
    if not args: return True
    cmd, *v = args
    counts = {'mkdir':1,'touch':1,'cd':1,'write':2,'overwrite':2,'read':1,'rename':2,'mv':2,'replace':2,'rm':1,'rmdir':1,'info':1,'status':0,'tree':0,'pwd':0,'help':0,'exit':0,'quit':0}
    if cmd == 'ls':
        if len(v)>1: raise ValueError('Uso: ls [CAMINHO]')
        for e in fs.ls(v[0] if v else '.'): print(f"{e['type']:4}  ID {e['id']:3}  {e['name']}")
    elif cmd not in counts: raise ValueError('Comando desconhecido; use help')
    elif len(v) != counts[cmd]: raise ValueError('Número de argumentos inválido; use help')
    elif cmd in ('exit','quit'): return False
    elif cmd == 'help': print(HELP)
    elif cmd == 'mkdir': fs.mkdir(*v)
    elif cmd == 'touch': fs.touch(*v)
    elif cmd == 'write': fs.write(v[0],v[1].encode('utf-8'),append=True)
    elif cmd == 'overwrite': fs.write(v[0],v[1].encode('utf-8'))
    elif cmd == 'read': print(fs.read(*v).decode('utf-8', errors='replace'))
    elif cmd == 'rename': fs.rename(*v)
    elif cmd == 'mv': fs.move(*v)
    elif cmd == 'replace': fs.replace(*v)
    elif cmd == 'rm': fs.remove(*v)
    elif cmd == 'rmdir': fs.remove(v[0],directory=True)
    elif cmd == 'info': print(json.dumps(fs.get(*v),ensure_ascii=False,indent=2))
    elif cmd == 'status':
        s=fs.status(); print(f"Blocos: {s['used']}/{s['total']} ocupados; {s['free']} livres; {s['block_size']} bytes por bloco")
    elif cmd == 'cd':
        e=fs.get(*v)
        if e['type'] != 'dir': raise NotADirectoryError(v[0])
        fs.cwd=e['id']
    elif cmd == 'pwd': print(fs.path_of(fs.cwd))
    elif cmd == 'tree':
        def show(path, indent):
            for e in fs.ls(path):
                print('  '*indent + ('📁 ' if e['type']=='dir' else '📄 ') + e['name'] + f" [ID {e['id']}]")
                if e['type']=='dir': show(fs.path_of(e['id']),indent+1)
        print('/'); show('/',1)
    return True

def main():
    p=argparse.ArgumentParser(description='Mini sistema de arquivos educacional inspirado em NTFS')
    p.add_argument('disk', help='Arquivo do disco virtual')
    p.add_argument('--init', action='store_true', help='criar disco novo, sem sobrescrever um existente')
    p.add_argument('--block-size',type=int,default=64); p.add_argument('--blocks',type=int,default=128)
    opts=p.parse_args()
    try: fs=FileSystem.create(opts.disk,opts.block_size,opts.blocks) if opts.init else FileSystem(opts.disk)
    except (OSError,ValueError) as e: p.exit(1, f'Erro: {e}\n')
    print('Mini sistema educacional (não é NTFS real). Digite help para comandos.')
    while True:
        try:
            if not run(fs,input(f'ntfs:{fs.path_of(fs.cwd)}> ')): break
        except (ValueError,OSError,UnicodeError) as e: print(f'Erro: {e}')
        except (EOFError,KeyboardInterrupt): print(); break

if __name__ == '__main__': main()
