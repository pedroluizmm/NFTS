"""Persistência do disco educacional em um único documento JSON."""
import json
import os
import tempfile

class Disk:
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def load(self):
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        if data.get('format') != 'mini-ntfs-1':
            raise ValueError('Formato de disco inválido')
        return data

    def save(self, data):
        parent = os.path.dirname(self.path)
        fd, tmp = tempfile.mkstemp(prefix='.mini-', suffix='.tmp', dir=parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
