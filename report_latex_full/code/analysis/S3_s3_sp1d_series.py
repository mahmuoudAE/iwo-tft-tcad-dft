"""S3 task 5: no-trap SP vs classical for a denser thickness series (3, 4, 5 nm); same model as s3_sp1d.py."""
import json
import s3_sp1d as sp
s = sp.main(traps=False, thick=(3.0, 4.0, 5.0))
json.dump(s, open('s3_sp1d_series.json', 'w'), indent=1)
