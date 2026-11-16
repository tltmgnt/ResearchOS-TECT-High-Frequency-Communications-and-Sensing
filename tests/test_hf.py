import copy,math,subprocess,sys,tempfile,unittest
from pathlib import Path
from researchos_hf.model import C,analyze
from researchos_hf.records import ValidationError,dumps,read_json,sha,validate
from researchos_hf.workflow import run,verify_bundle,verify_evidence
ROOT=Path(__file__).resolve().parents[1];EXAMPLE=ROOT/'examples/synthetic-hf.json'

class HFTests(unittest.TestCase):
    def setUp(self):self.r=read_json(EXAMPLE)
    def test_vertical_geometry_and_cutoff_boundary(self):
        rows=analyze(self.r)['link_results'];a=rows[0]
        self.assertEqual(a['geometric_path_km'],500)
        self.assertEqual(a['incidence_from_vertical_deg'],0)
        self.assertEqual(a['toy_secant_cutoff_mhz'],5)
        self.assertEqual(rows[1]['toy_cutoff_status'],'not-above-toy-cutoff')
        self.assertEqual(rows[2]['toy_cutoff_status'],'above-toy-cutoff')
        self.assertEqual(rows[2]['threshold_status'],'not-assessed-above-toy-cutoff')
        self.assertAlmostEqual(a['geometric_delay_ms'],500000/C*1000)
    def test_oblique_geometry_and_noise_sensitivity(self):
        rows=analyze(self.r)['link_results'];ref=rows[12];noise=rows[28]
        self.assertAlmostEqual(ref['geometric_path_km'],math.sqrt(500**2+500**2))
        self.assertAlmostEqual(ref['toy_secant_cutoff_mhz'],5*math.sqrt(2))
        self.assertAlmostEqual(ref['incidence_from_vertical_deg'],45)
        self.assertAlmostEqual(noise['reference_snr_db'],ref['reference_snr_db']-10)
        self.assertEqual(noise['toy_secant_cutoff_mhz'],ref['toy_secant_cutoff_mhz'])
    def test_budget_equation_and_frequency_scaling(self):
        rows=analyze(self.r)['link_results'];a,b=rows[0],rows[1]
        self.assertAlmostEqual(a['geometric_reference_loss_db'],20*math.log10(4*math.pi*500000/(C/3e6)))
        self.assertAlmostEqual(b['geometric_reference_loss_db']-a['geometric_reference_loss_db'],20*math.log10(5/3))
        self.assertAlmostEqual(a['reference_received_power_dbm'],30-2-a['geometric_reference_loss_db']-10)
        self.assertEqual(len(rows),48)
    def test_sounding_and_zero_delay(self):
        s=analyze(self.r)['sounding_results']
        self.assertAlmostEqual(s[0]['virtual_height_km'],149.896229)
        self.assertAlmostEqual(s[0]['timing_only_height_uncertainty_km'],1.49896229)
        self.r['sounding']['assumed_round_trip_delays_ms']=[0]
        self.assertEqual(analyze(self.r)['sounding_results'][0]['virtual_height_km'],0)
    def test_invalid_records(self):
        mutations=[lambda r:r.update(schema_version=True),lambda r:r.update(id='../escape'),lambda r:r['link'].update(frequencies_mhz=[2]),lambda r:r['link'].update(ground_distances_km=[1001]),lambda r:r['scenarios'][0].update(virtual_height_km=0),lambda r:r['scenarios'][0].update(critical_frequency_mhz=float('nan')),lambda r:r['scenarios'].append(copy.deepcopy(r['scenarios'][0])),lambda r:r['sounding'].update(assumed_round_trip_delays_ms=[-1]),lambda r:r.update(data_kind='experimental')]
        for mutate in mutations:
            r=copy.deepcopy(self.r);mutate(r)
            with self.subTest(record=r),self.assertRaises(ValidationError):validate(r)
    def test_experimental_evidence_and_portability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=b'test fixture, not real ionospheric evidence';(root/'raw').write_bytes(data)
            self.r['data_kind']='experimental';self.r['evidence']=[{'id':'raw','path':'raw','sha256':sha(data),'description':'Fixture'}]
            self.r['measurements']=[{'metric':'in-band noise','unit':'dBm','value':-90,'uncertainty':1,'method':'Fixture','evidence_ids':['raw']}]
            p=root/'record.json';p.write_text(dumps(self.r));run(p,root/'run');(root/'raw').unlink();verify_bundle(root/'run');(root/'run/evidence/0000.bin').write_bytes(b'changed')
            with self.assertRaises(ValidationError):verify_bundle(root/'run')
    def test_integrity_no_overwrite_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a,b=root/'a',root/'b';run(EXAMPLE,a);run(EXAMPLE,b);verify_bundle(a)
            self.assertEqual({p.relative_to(a):p.read_bytes() for p in a.rglob('*') if p.is_file()},{p.relative_to(b):p.read_bytes() for p in b.rglob('*') if p.is_file()})
            with self.assertRaises(ValidationError):run(EXAMPLE,a)
            result=read_json(a/'results.json');result['link_results'][0]['toy_secant_cutoff_mhz']=999;(a/'results.json').write_text(dumps(result));manifest=read_json(a/'manifest.json');manifest['files']['results.json']=sha((a/'results.json').read_bytes());(a/'manifest.json').write_text(dumps(manifest))
            with self.assertRaises(ValidationError):verify_bundle(a)
            self.r['evidence']=[{'id':'raw','path':'../escape','sha256':sha(b'x'),'description':'Fixture'}]
            with self.assertRaises(ValidationError):validate(self.r)
            (root/'link').symlink_to(root.parent);self.r['evidence'][0]['path']='link/outside'
            with self.assertRaises(ValidationError):verify_evidence(validate(self.r),root)
    def test_strict_json_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json'
            for data in ['{"x":1,"x":2}','{"x":NaN}']:
                p.write_text(data)
                with self.assertRaises(ValidationError):read_json(p)
            output=str(Path(tmp)/'run')
            for args in [['validate',str(EXAMPLE)],['run',str(EXAMPLE),'--output',output],['verify',output],['report',output]]:
                r=subprocess.run([sys.executable,'-m','researchos_hf',*args],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
