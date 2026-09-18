import importlib.util, sys, tempfile, unittest, threading
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import EigrutelDatePhoto as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name); self.src=self.base/'source'; self.src.mkdir()
 def tearDown(self): self.tmp.cleanup()
 def photo(self, name='image.jpg', value='2023:09:23 12:34:56', nested=False):
  p=self.src/name; p.parent.mkdir(parents=True,exist_ok=True)
  ex=m.Image.Exif()
  if nested: ex[34665]={36867:value}
  else: ex[36867]=value
  m.Image.new('RGB',(4,4),'red').save(p,exif=ex)
  return p
 def test_nested_exif(self):
  self.assertEqual(m.read_exif_datetime(self.photo(nested=True)),datetime(2023,9,23,12,34,56))
 def test_null_date(self):
  self.assertEqual(m.normalize_exif_datetime(b'2023:09:23 12:34:56\x00'),datetime(2023,9,23,12,34,56))
 def test_date_limits(self):
  self.assertFalse(m.is_valid_date(datetime(1989,12,31))); self.assertFalse(m.is_valid_date(datetime(2999,1,1))); self.assertTrue(m.is_valid_date(datetime(1990,1,1)))
 def test_fallback(self):
  p=self.photo(value='2999:01:01 00:00:00'); ex=m.Image.Exif(); ex[36867]='2999:01:01 00:00:00'; ex[306]='2022:01:02 00:00:00'
  m.Image.new('RGB',(3,3)).save(p,exif=ex)
  self.assertEqual(m.read_exif_datetime(p).year,2022)
 def test_idempotence(self):
  p=self.photo('2023_09_23_image.jpg'); planner=m.Planner(self.src); rows,_,_=planner.scan(); self.assertEqual(rows[0].status,'unchanged'); self.assertEqual(planner.execute(rows),0); self.assertTrue(p.exists())
 def test_reserved_collisions(self):
  self.photo('a/image.jpg'); self.photo('b/image.jpg'); planner=m.Planner(self.src,True,self.base/'out'); rows,_,_=planner.scan('classer'); self.assertNotEqual(rows[0].dest,rows[1].dest); self.assertTrue(rows[1].dest.name.endswith('_001.jpg'))
 def test_move_content(self):
  p=self.photo(); data=p.read_bytes(); planner=m.Planner(self.src); rows,_,_=planner.scan(); self.assertEqual(planner.execute(rows),1); self.assertFalse(p.exists()); self.assertEqual(rows[0].dest.read_bytes(),data)
 def test_destination_appears(self):
  p=self.photo(); planner=m.Planner(self.src); rows,_,_=planner.scan(); rows[0].dest.write_bytes(b'keep'); self.assertEqual(planner.execute(rows),0); self.assertTrue(p.exists()); self.assertEqual(rows[0].dest.read_bytes(),b'keep')
 def test_source_changed(self):
  p=self.photo(); planner=m.Planner(self.src); rows,_,_=planner.scan(); p.write_bytes(b'changed'); self.assertEqual(planner.execute(rows),0); self.assertEqual(p.read_bytes(),b'changed')
 def test_bad_image_and_undated(self):
  (self.src/'bad.jpg').write_bytes(b'invalid'); m.Image.new('RGB',(3,3)).save(self.src/'blank.jpg'); rows,total,dated=m.Planner(self.src).scan(); self.assertEqual({r.status for r in rows},{'failed','undated'}); self.assertEqual((total,dated),(2,0))
 def test_subfolder_and_target_exclusion(self):
  self.photo('a/a.jpg')
  self.photo('photos_annees/b.jpg')
  self.photo('my_photos_annees/c.jpg')
  # Explicit destination: do not depend on OS-specific default folders.
  self.assertEqual(len(list(m.Planner(self.src, custom_target=self.src).files())), 2)
  self.assertEqual(len(list(m.Planner(self.src, False, custom_target=self.src).files())), 0)
  # If filing elsewhere, the similarly named source folder must be included.
  self.assertEqual(len(list(m.Planner(self.src, custom_target=self.base/'outside').files())), 3)
 def test_cancel(self):
  self.photo(); cancel=threading.Event(); cancel.set(); rows,_,_=m.Planner(self.src).scan(cancel=cancel); self.assertEqual(rows,[])
 def test_exclusive_cross_device_copy(self):
  import errno
  p=self.photo(); dest=self.base/'out.jpg'; original=p.read_bytes()
  with patch.object(m.os,'rename' if m.os.name == 'nt' else 'link',side_effect=OSError(errno.EXDEV,'cross device')): m.safe_move(p,dest)
  self.assertEqual(dest.read_bytes(),original); self.assertFalse(p.exists())
 def test_failed_copy_preserves_source(self):
  import errno
  p=self.photo(); dest=self.base/'out.jpg'
  with patch.object(m.os,'rename' if m.os.name == 'nt' else 'link',side_effect=OSError(errno.EXDEV,'cross device')),patch.object(m.shutil,'copyfileobj',side_effect=OSError('disk full')):
   with self.assertRaises(OSError): m.safe_move(p,dest)
  self.assertTrue(p.exists()); self.assertFalse(dest.exists())
 def test_case_collision(self):
  self.photo(); (self.src/'2023_09_23_IMAGE.JPG').write_bytes(b'keep'); rows,_,_=m.Planner(self.src).scan(); row=next(r for r in rows if r.src.name=='image.jpg'); self.assertEqual(row.dest.name,'2023_09_23_image_001.jpg')
if __name__=='__main__': unittest.main(verbosity=2)
