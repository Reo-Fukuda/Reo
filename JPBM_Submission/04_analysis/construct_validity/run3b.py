import pandas as pd, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from driver import run
d = pd.read_csv('../data/study3b_public.csv'); a = d[d.attention_1==1].copy()
run("STUDY 3b", a,
    [("Failure Inference", ['fail_inf_1','fail_inf_2','fail_inf_3']),
     ("Loss of Brand Luxuriousness", ['LOB_item1','LOB_item2','LOB_item3'])],
    "(1 attention-check failure excluded)")
print("\nComposite M/SD by cell (free_dummy x low_flagship):")
print(a.groupby(['low_flagship','free_dummy'])[['failure_inference','LOB']]
       .agg(['mean','std','count']).round(3).to_string())
print("observed r(FI,LOB) =", round(a['failure_inference'].corr(a['LOB']),3))
