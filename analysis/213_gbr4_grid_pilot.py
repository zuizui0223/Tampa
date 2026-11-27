#!/usr/bin/env python3
"""Read official GBR4 v4 daily NetCDF over OPeNDAP; grid only and one bounded velocity pilot."""
import hashlib,json
from pathlib import Path
import numpy as np
import netCDF4 as nc
OUT=Path("gbr4_pilot_sources");OUT.mkdir(exist_ok=True)
ROOT="https://thredds.nci.org.au/thredds/dodsC/fx3/gbr4_H4p0_ABARRAr2_OBRAN2020_FG2Gv3_Dhnd/"
DAY="2010-10-01"
def masked(v):
 return np.ma.filled(v.astype("float64"),np.nan)
def info(v):
 return dict(dims=list(v.dimensions),shape=list(v.shape),units=getattr(v,"units",None),standard_name=getattr(v,"standard_name",None),long_name=getattr(v,"long_name",None))
def save(name,**a):
 p=OUT/name;np.savez_compressed(p,**a);return dict(file=name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 r={"url":ROOT+"gbr4_simple_"+DAY+".nc","state":"STOP","files":[]}
 try:
  with nc.Dataset(r["url"]) as ds:
   r["variables"]={k:info(ds[k]) for k in ["latitude","longitude","botz","zc","time","u","v"]};print(json.dumps(r["variables"]),flush=True)
   x,y,z=[masked(ds[k][:]) for k in ["longitude","latitude","botz"]]
   assert x.shape==y.shape==z.shape and x.ndim==2 and x.size<=150000
   depth=masked(ds["zc"][:]);t=ds["time"];dates=np.array([d.isoformat() for d in nc.num2date(t[:],t.units,getattr(t,"calendar","standard"))])
   r["files"].append(save("gbr4_grid.npz",lon=x,lat=y,botz=z,depth=depth,time=dates))
   r["grid_state"]="ACQUIRED";r["time_units"]=t.units
   print(json.dumps(r),flush=True)
   (OUT/"manifest.json").write_text(json.dumps(r,indent=2)+"\n")
   eligible=np.isfinite(x)&np.isfinite(y)&(x>=141)&(x<=145)&(y>=-11.5)&(y<=-8.5)
   j,i=np.where(eligible);assert len(j)>0
   a,b=max(0,int(j.min())-1),min(x.shape[0],int(j.max())+2);c,d=max(0,int(i.min())-1),min(x.shape[1],int(i.max())+2)
   u,v=ds["u"],ds["v"];assert u.dimensions==v.dimensions and len(u.dimensions)==4 and u.dimensions[2:]==ds["longitude"].dimensions
   assert u.shape[1]==len(depth) and u.shape[0]<=25
   assert u.units.replace(" ","") in ("ms-1","ms^-1","m/s","m/sec","ms**-1"),u.units
   assert v.units==u.units
   k=int(np.argmin(np.where(depth<0,np.abs(depth),np.inf)))
   assert -5<=depth[k]<0
   assert (b-a)*(d-c)*u.shape[0]<500000
   uu,vv=masked(u[:,k,a:b,c:d]),masked(v[:,k,a:b,c:d])
   r["files"].append(save("gbr4_velocity_pilot.npz",u=uu,v=vv,lon=x[a:b,c:d],lat=y[a:b,c:d],botz=z[a:b,c:d],depth=depth[k],time=dates,offset=np.array([a,c])))
   r.update(state="ACQUIRED",surface_depth=float(depth[k]),grid_shape=list(x.shape),slab_shape=list(uu.shape),slab_bounds=[a,b,c,d],valid_fraction=float((np.isfinite(uu)&np.isfinite(vv)).mean()))
 except Exception as e:r["reason"]=type(e).__name__+": "+str(e)[:500]
 (OUT/"manifest.json").write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r),flush=True)
if __name__=="__main__":main()
