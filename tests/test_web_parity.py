import copy,json,math,shutil,subprocess,unittest
from pathlib import Path
from researchos_hf.records import read_json
from researchos_hf.model import analyze
ROOT=Path(__file__).resolve().parents[1]
@unittest.skipUnless(shutil.which('node'),'Node required for web parity')
class WebParityTests(unittest.TestCase):
    def test_full_result_parity(self):
        base=read_json(ROOT/'examples/synthetic-hf.json');cases=[base]
        r=copy.deepcopy(base);r['link']['ground_distances_km']=[0,1000];r['sounding']['assumed_round_trip_delays_ms']=[0,10];cases.append(r)
        r=copy.deepcopy(base);r['scenarios'][0]['virtual_height_km']=500;r['scenarios'][0]['critical_frequency_mhz']=20;r['scenarios'].reverse();cases.append(r)
        script="import fs from 'node:fs';import{analyze}from './web/model.mjs';console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(analyze)))"
        results=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],input=json.dumps(cases),text=True,cwd=ROOT))
        def compare(a,b):
            if isinstance(b,dict):
                self.assertEqual(a.keys(),b.keys())
                for k in b:compare(a[k],b[k])
            elif isinstance(b,list):
                self.assertEqual(len(a),len(b))
                for x,y in zip(a,b):compare(x,y)
            elif type(b) is float:self.assertTrue(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-11),(a,b))
            else:self.assertEqual(a,b)
        for r,w in zip(cases,results):compare(w,analyze(r))
