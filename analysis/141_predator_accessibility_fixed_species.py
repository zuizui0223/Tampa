"""Reproduce core fixed-species burial contrasts and cross-study scenario; tank unit."""
import argparse,hashlib,io,json,zipfile,math
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
HASH="144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c"
def selected_sum_counts(vals,k):
    dp=[Counter() for _ in range(k+1)];dp[0][0]=1
    for i,v in enumerate(vals):
        for j in range(min(k,i+1),0,-1):
            for t,n in dp[j-1].items(): dp[j][t+v]+=n
    assert sum(dp[k].values())==math.comb(len(vals),k)
    return dp[k]
def exact(groups,a,b):
    scale=math.lcm(*[len(g[d]) for g in groups for d in (a,b)])
    obs=0;dist=Counter({0:1})
    for g in groups:
        x,y=g[a],g[b];n,m=len(x),len(y);total=int(x.sum()+y.sum())
        obs+=int(x.sum())*(scale//n)-int(y.sum())*(scale//m)
        dd={s*(scale//n+scale//m)-total*(scale//m):c for s,c in selected_sum_counts(list(map(int,np.r_[x,y])),n).items()}
        new=Counter()
        for s,c in dist.items():
            for t,d in dd.items(): new[s+t]+=c*d
        dist=new
    return sum(c for s,c in dist.items() if abs(s)>=abs(obs))/sum(dist.values())
def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        man=json.loads(z.read("manifest.json"))
        def rows(name):
            b=z.read(name);assert hashlib.sha256(b).hexdigest()==next(r["sha256"] for r in man["sources"] if r.get("file")==name)
            return list(load_workbook(io.BytesIO(b),data_only=True).active.values)
        r=rows("infantes_burial.xlsx");fr=rows("meysick_seed_trapping.xlsx")
    groups=[];err=[]
    for s,e,i,j,k in [(3,37,7,8,9),(41,70,2,3,4),(73,102,3,4,5)]:
        g=defaultdict(list)
        for idx in range(s,e+1):
            a=r[idx-1];assert a[i]==10 and 0<=a[j]<=10 and a[1] in (0,1,2)
            loss=int(a[i]-a[j]);g[a[1]].append(loss)
            if a[k]!=loss*10:err.append(idx)
        groups.append({d:np.array(v) for d,v in g.items()})
    assert err==[57] and [list(map(len,g.values())) for g in groups]==[[15,10,10],[10,10,10],[10,10,10]]
    rng=np.random.default_rng(20261124);B=50000
    means=np.array([[g[d].mean()/10 for d in range(3)] for g in groups])
    bs=np.array([[rng.choice(g[d],(B,len(g[d])),replace=True).mean(1)/10 for d in range(3)] for g in groups])
    ci=lambda x:np.quantile(x,[.025,.975]).tolist()
    eb=bs.mean(0);eq=means.mean(0);c1=eb[0]-eb[1];c2=eb[1]-eb[2]
    grid={2:{},16:{}}
    for t,_,_,_,v,_,k,n,*_ in fr[2:]:
        if t in grid:
            assert n==30 and v not in grid[t];grid[t][v]=k/n
    assert all(set(g)==set(range(12,31,2)) for g in grid.values())
    T0,T1=[np.mean(list(grid[t].values())) for t in (2,16)]
    ratios=means[:,1]/means[:,0]
    scenarios=[]
    for i,q in enumerate(ratios):
        valid=bs[i,0]>0;mult=(T1/T0)*bs[i,1,valid]/bs[i,0,valid]
        scenarios.append(dict(multiplier=float(T1/T0*q),ci=ci(mult) if i!=2 else None,flow_cells_above_one=int(sum(grid[16][v]/grid[2][v]*q>1 for v in grid[2]))))
    return dict(means=means.tolist(),species_first_cm_ci=[ci(x[0]-x[1]) for x in bs],equal_mean=eq.tolist(),first_ci=ci(c1),second_ci=ci(c2),difference_ci=ci(c1-c2),p01=exact(groups,0,1),p12=exact(groups,1,2),scenarios=scenarios)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);a=p.parse_args();print(json.dumps(run(a.artifact),indent=2))
