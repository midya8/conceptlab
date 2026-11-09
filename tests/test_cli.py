import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from conceptlab import audit

class CLI(unittest.TestCase):
    def test_stdout(self):
        d={'attributes':2,'objects':[[0],[0,1]]}
        p=subprocess.run([sys.executable,'-m','conceptlab','-'],input=json.dumps(d),capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),audit(d))
    def test_file_and_reject_preserves_existing(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'in.json';out=Path(temp)/'out.json';out.write_text('retain me')
            for text in ['{}','{"attributes":1,"objects":[],"attributes":2}','{"attributes":NaN,"objects":[]}', ' '*65537,'[[[[']:
                source.write_text(text)
                p=subprocess.run([sys.executable,'-m','conceptlab',str(source),'-o',str(out)],capture_output=True,text=True)
                self.assertNotEqual(p.returncode,0);self.assertEqual(p.stdout,'');self.assertEqual(out.read_text(),'retain me')
            d={'attributes':0,'objects':[]};source.write_text(json.dumps(d))
            subprocess.run([sys.executable,'-m','conceptlab',str(source),'-o',str(out)],check=True)
            self.assertEqual(json.loads(out.read_text()),audit(d))
            self.assertEqual(sorted(x.name for x in Path(temp).iterdir()),['in.json','out.json'])
    def test_invalid_utf8(self):
        p=subprocess.run([sys.executable,'-m','conceptlab','-'],input=b'\xff',capture_output=True)
        self.assertEqual(p.returncode,2)

if __name__=='__main__':unittest.main()
