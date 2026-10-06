import datetime as dt,json,unittest
from pathlib import Path
from refill import plan,TZ
class Checks(unittest.TestCase):
 def setUp(self):self.rows=json.loads(Path('calendar.json').read_text())
 def test_calendar(self):
  self.assertEqual(len(self.rows),365)
  dates=[dt.date.fromisoformat(r['date']) for r in self.rows]
  self.assertEqual((dates[-1]-dates[0]).days,364)
  self.assertEqual(len(set(r['text'] for r in self.rows)),365)
  for r in self.rows:
   self.assertLessEqual(len(r['title']),100);self.assertLessEqual(len(r['text']),500);self.assertTrue(Path(r['image']).is_file())
 def test_horizon_duplicate_and_cap(self):
  now=dt.datetime(2026,10,10,9,tzinfo=TZ)
  posts=[{'status':'scheduled','dueAt':'2026-10-10T15:00:00Z'}]
  selected=plan(self.rows,posts,now)
  self.assertEqual(len(selected),6);self.assertEqual(selected[0][0]['date'],'2026-10-11')
  self.assertEqual(plan(self.rows,posts*10,now),[])
 def test_expiry(self):self.assertEqual(plan(self.rows,[],dt.datetime(2027,10,10,tzinfo=TZ)),[])
 def test_failed_post(self):
  with self.assertRaises(RuntimeError):plan(self.rows,[{'status':'error','dueAt':None}],dt.datetime(2026,10,10,tzinfo=TZ))
if __name__=='__main__':unittest.main()
