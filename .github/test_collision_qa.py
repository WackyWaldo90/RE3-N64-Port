import unittest,csv
from pathlib import Path
from collision_qa import audit
class Tests(unittest.TestCase):
 def test_full_audit(self):
  base=Path(__file__).parent
  with (base/"collision_records.csv").open() as f:rows=list(csv.DictReader(f))
  issues=audit(rows)
  self.assertEqual(len(issues),9)
  self.assertEqual(sum("duplicate_exact_record" in x["flags"] for x in issues),6)
  self.assertEqual(sum("z_descending" in x["flags"] for x in issues),3)
 def test_synthetic(self):
  x=dict(room="r",record="0",shape="1",x1="10",z1="8",x2="5",z2="1",id="1",type="0",floor_mask="0",unknown="0")
  self.assertEqual(audit([x])[0]["flags"],"x_descending|z_descending")
if __name__=="__main__":unittest.main()
