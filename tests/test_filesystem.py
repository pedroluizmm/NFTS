import tempfile
import unittest
from pathlib import Path
from src.filesystem import FileSystem

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'disk.json'
        self.fs=FileSystem.create(self.path,4,3)
    def tearDown(self): self.tmp.cleanup()
    def test_operations_and_persistence(self):
        f=self.fs; f.mkdir('/docs'); f.mkdir('/dest'); f.touch('/docs/a'); f.write('/docs/a',b'abc'); f.write('/docs/a',b'de',True)
        self.assertEqual(f.read('/docs/a'),b'abcde'); old=f.get('/docs/a')['id']
        f.write('/docs/a',b'z'); self.assertEqual(f.get('/docs/a')['id'],old)
        f.rename('/docs/a','b'); f.move('/docs/b','/dest'); self.assertEqual(f.read('/dest/b'),b'z')
        f.touch('/docs/source'); f.write('/docs/source',b'new'); source=f.get('/docs/source')['id']
        f.replace('/docs/source','/dest/b'); self.assertEqual(f.get('/dest/b')['id'],source)
        self.assertEqual(FileSystem(self.path).read('/dest/b'),b'new')
        self.assertEqual([x['name'] for x in f.ls('/dest')],['b']); f.remove('/dest/b'); f.remove('/dest',True)
        self.assertEqual(f.status()['used'],0)
    def test_errors_and_no_partial_write(self):
        f=self.fs; f.touch('/a'); f.write('/a',b'1234')
        with self.assertRaises(FileExistsError): f.touch('/a')
        with self.assertRaises(FileNotFoundError): f.read('/missing')
        with self.assertRaises(FileNotFoundError): f.touch('/missing/a')
        with self.assertRaises(ValueError): f.write('/a',b'x'*13)
        self.assertEqual(f.read('/a'),b'1234'); self.assertEqual(FileSystem(self.path).read('/a'),b'1234')
        with self.assertRaises(FileExistsError): FileSystem.create(self.path)
    def test_blocks_reuse_and_relative(self):
        f=self.fs; f.mkdir('/d'); f.cwd=f.get('/d')['id']; f.touch('a'); f.write('a',b'12345678')
        self.assertEqual(f.get('a')['blocks'],[0,1]); f.remove('a'); f.touch('b'); f.write('b',b'1234')
        self.assertEqual(f.get('b')['blocks'],[0]); self.assertEqual(f.read('../d/b'),b'1234')
        with self.assertRaises(ValueError): f.remove('/d',True)
        with self.assertRaises(ValueError): f.move('/d','/d/inside')
    def test_replace_and_conflicts(self):
        f=self.fs; f.touch('/a'); f.touch('/b'); f.write('/a',b'1111'); f.write('/b',b'2222')
        with self.assertRaises(ValueError): f.replace('/a','/a')
        with self.assertRaises(FileExistsError): f.move('/a','/b')
        f.replace('/a','/b'); self.assertEqual(f.read('/b'),b'1111'); self.assertEqual(f.status()['used'],1)
        with self.assertRaises(FileNotFoundError): f.read('/a')

if __name__ == '__main__': unittest.main()
