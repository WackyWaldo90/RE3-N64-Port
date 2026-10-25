import tempfile, unittest, struct
from pathlib import Path
from extract_ps1_boot import Disc, boot_target, run

def directory_record(name,lba,size,flags=0):
    b=name.encode('ascii') if name else b'\0'
    length=33+len(b)+(len(b)%2==0)
    r=bytearray(length);r[0]=length
    struct.pack_into('<I',r,2,lba);struct.pack_into('>I',r,6,lba)
    struct.pack_into('<I',r,10,size);struct.pack_into('>I',r,14,size)
    r[25]=flags;r[28]=1;r[31]=1;r[32]=len(b);r[33:33+len(b)]=b
    return bytes(r)

def fixture(path,stride,offset):
    blocks=[bytearray(2048) for _ in range(24)]
    pvd=blocks[16];pvd[:7]=b'\x01CD001\x01'
    root=directory_record('',20,2048,2)
    pvd[156:156+len(root)]=root
    cnf=b'BOOT = cdrom:\\SLES_025.29;1\r\n'
    exe=b'PS-X EXE'+bytes(2040)
    struct.pack_into('<I',blocks[22],0,0) if False else None
    entries=[directory_record('SYSTEM.CNF;1',21,len(cnf)),directory_record('SLES_025.29;1',22,len(exe))]
    blocks[20][:sum(map(len,entries))]=b''.join(entries)
    blocks[21][:len(cnf)]=cnf;blocks[22][:]=exe
    with open(path,'wb') as f:
        for block in blocks:
            sector=bytearray(stride);sector[offset:offset+2048]=block
            f.write(sector)
    return exe

class Tests(unittest.TestCase):
    def test_boot_parse(self):
        self.assertEqual(boot_target(b'BOOT = cdrom:\\SLES_025.29;1\r\n'),'SLES_025.29;1')
    def test_iso_2048(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.iso';exe=fixture(path,2048,0)
            m=run(path,Path(t)/'out')
            self.assertEqual((Path(t)/'out'/'boot_executable.bin').read_bytes(),exe)
            self.assertEqual(m['sector_size'],2048)
    def test_bin_mode2(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.bin';exe=fixture(path,2352,24)
            m=run(path,Path(t)/'out')
            self.assertEqual(m['payload_offset'],24)
            self.assertEqual((Path(t)/'out'/'boot_executable.bin').read_bytes(),exe)
    def test_bin_mode1(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.bin';fixture(path,2352,16)
            self.assertEqual(run(path,Path(t)/'out')['payload_offset'],16)
    def test_missing_pvd(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.iso';path.write_bytes(bytes(24*2048))
            with self.assertRaises(ValueError):Disc(path)
if __name__=='__main__':unittest.main()
