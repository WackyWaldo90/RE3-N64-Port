import unittest
from pack_collision_n64 import pack,unpack
class Tests(unittest.TestCase):
 def setUp(self):
  self.row=dict(x1="-10",z1="20",x2="30",z2="-40",id="65535",type="32768",floor_mask="0",unknown="42")
 def test_roundtrip(self):
  data=pack([self.row]);self.assertEqual(unpack(data),[(-10,20,30,-40,65535,32768,0,42)])
 def test_big_endian(self):
  self.assertEqual(pack([self.row])[16:18],bytes.fromhex("fff6"))
 def test_corruption(self):
  b=bytearray(pack([self.row]));b[-1]^=1
  with self.assertRaises(ValueError):unpack(b)
 def test_empty(self):self.assertEqual(unpack(pack([])),[])
if __name__=="__main__":unittest.main()
