import unittest,struct
from inspect_psx_exe import inspect
def fixture():
 b=bytearray(2048+16)
 b[:8]=b"PS-X EXE"
 struct.pack_into("<I",b,0x10,0x80010000)
 struct.pack_into("<I",b,0x18,0x80010000)
 struct.pack_into("<I",b,0x1c,16)
 return b
class Tests(unittest.TestCase):
 def test_valid(self):
  r=inspect(fixture())
  self.assertEqual(r["load_address"],0x80010000)
  self.assertEqual(r["payload_bytes"],16)
 def test_bad_magic(self):
  b=fixture();b[0]=0
  with self.assertRaises(ValueError):inspect(b)
 def test_truncated(self):
  b=fixture();struct.pack_into("<I",b,0x1c,32)
  with self.assertRaises(ValueError):inspect(b)
 def test_short(self):
  with self.assertRaises(ValueError):inspect(b"PS-X EXE")
if __name__=="__main__":unittest.main()
