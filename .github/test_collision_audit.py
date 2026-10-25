import csv,unittest
from pathlib import Path
class Tests(unittest.TestCase):
 def test_records(self):
  with (Path(__file__).parent/"collision_records.csv").open() as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),5291)
  self.assertEqual(sum(int(x["shape"])==9 for x in r),32)
  self.assertEqual(sum(int(x["shape"])==10 for x in r),89)
 def test_inventory(self):
  with (Path(__file__).parent/"room_inventory.csv").open() as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),169)
  self.assertEqual(sum(int(x["sca_count"]) for x in r),5291)
 def test_shapes(self):
  with (Path(__file__).parent/"collision_records.csv").open() as f:
   for r in csv.DictReader(f):
    self.assertEqual(int(r["id"])&15,int(r["shape"]))
if __name__=="__main__":unittest.main()
