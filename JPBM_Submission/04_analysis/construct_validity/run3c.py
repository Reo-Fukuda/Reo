import pandas as pd, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from driver import run
d = pd.read_csv('../data/study3c_public.csv')
print("rows", len(d), "| excluded:", d.loc[d.attention_1!=1,'participant_id'].tolist())
a = d[d.attention_1==1].copy()
run("STUDY 3c", a,
    [("Failure Inference", ['fail_inf_1','fail_inf_2','fail_inf_3']),
     ("Loss of Brand Luxuriousness", ['LOB_item1','LOB_item2','LOB_item3'])],
    "(5 attention-check failures excluded)")
a['FI'] = a[['fail_inf_1','fail_inf_2','fail_inf_3']].mean(axis=1)
a['LB'] = a[['LOB_item1','LOB_item2','LOB_item3']].mean(axis=1)
print("\nComposite M/SD by cell (source dummy 'low_flagship' x free_dummy):")
print(a.groupby(['low_flagship','free_dummy'])[['FI','LB']].agg(['mean','std','count']).round(3).to_string())
print("observed r(FI,LOB) =", round(a['FI'].corr(a['LB']),3))
