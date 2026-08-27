import pandas as pd, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from driver import run
d = pd.read_csv('../data/study3a_public.csv')
print("attention_1 != 1 rows:", d.loc[d.attention_1!=1,'participant_id'].tolist())
a = d[d.attention_1==1].copy()
run("STUDY 3a", a,
    [("Failure Inference", ['fail_inf_1','fail_inf_2','fail_inf_3']),
     ("Loss of Brand Luxuriousness", ['LOB_item1','LOB_item2','LOB_item3'])],
    "(2 attention-check failures excluded)")
print("\nComposite M/SD by condition (1=complimentary gift? check codebook):")
print(a.groupby('condition')[['failure_inference','LOB']].agg(['mean','std','count']).round(3).to_string())
print("observed r(FI, LOB) =", round(a['failure_inference'].corr(a['LOB']),3))
