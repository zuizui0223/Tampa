#!/usr/bin/env python3
"""Public BRAN2020 daily surface currents, small OPeNDAP subsets; no credentials."""
import hashlib,json,os,sys,urllib.request
from pathlib import Path
import numpy as np
import netCDF4 as nc
OUT=Path("torres_bran_sources");OUT.mkdir(exist_ok=True)
ROOT="https://thredds.nci.org.au/thredds/dodsC/gb6/BRAN/BRAN2020/daily/"
MONTHS=["2010_09","2010_10","2010_11","2010_12","2011_01","2011_02","2009_07","2009_08"]
# Depth/time/lon/lat inspected rather than hard-coded index offsets.
def subset(month,component):
    name=f"ocean_{component}_{month}.nc";url=ROOT+name
    rec={"month":month,"component":component,"url":url}
    try:
        with nc.Dataset(url) as ds:
            meta={k:{"dims":list(v.dimensions),"shape":list(v.shape),"units":getattr(v,"units",""),"standard_name":getattr(v,"standard_name","")} for k,v in ds.variables.items()}
            rec["variables"]=meta
            candidates=[k for k,v in ds.variables.items() if v.ndim==4 and (k in [component,"ocean_"+component] or getattr(v,"standard_name","")==("eastward_sea_water_velocity" if component=="u" else "northward_sea_water_velocity"))]
            if len(candidates)!=1:raise ValueError("velocity variable ambiguous "+str(candidates))
            v=ds[candidates[0]];td,zd,yd,xd=v.dimensions
            time=np.array(ds[td][:]);depth=np.array(ds[zd][:]);lat=np.array(ds[yd][:]);lon=np.array(ds[xd][:])
            assert np.all(np.diff(lat)>0) and np.all(np.diff(lon)>0)
            assert "degrees" in ds[yd].units and "degrees" in ds[xd].units
            assert v.units in ("m/s","m s-1","m s**-1","meter second-1","metre second-1","m s^-1"),v.units
            ix=np.where((lon>=139)&(lon<=147))[0];iy=np.where((lat>=-12.5)&(lat<=-7.5))[0]
            assert len(ix)>20 and len(iy)>20
            zi=int(np.argmin(np.abs(depth)));assert abs(depth[zi])<=5
            # single rectangular slab, monthly time dimension, top layer only.
            assert len(time)<=32 and len(time)>=28
            vv=np.ma.filled(v[:,zi,iy[0]:iy[-1]+1,ix[0]:ix[-1]+1].astype("float32"),np.nan)
            assert vv.shape==(len(time),len(iy),len(ix))
            dates=nc.num2date(time,ds[td].units,getattr(ds[td],"calendar","standard"))
            day=np.array([d.isoformat() for d in dates])
            f=OUT/f"{component}_{month}.npz"
            np.savez_compressed(f,values=vv,time=day,lat=lat[iy],lon=lon[ix],depth=float(depth[zi]))
            rec.update(state="ACQUIRED",file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),shape=vv.shape,valid_fraction=float(np.isfinite(vv).mean()),start=str(day[0]),end=str(day[-1]),depth=float(depth[zi]))
    except Exception as e:rec.update(state="STOP",reason=type(e).__name__+": "+str(e)[:350])
    return rec
if __name__=="__main__":
    res=[]
    # Stop after first failed pair; do not repeatedly retry a failing server.
    for month in MONTHS:
        for c in ["u","v"]:
            r=subset(month,c);res.append(r)
            (OUT/"manifest.json").write_text(json.dumps(res,indent=2)+"\n")
            print(json.dumps(r),flush=True)
            if r["state"]!="ACQUIRED":break
        if res[-1]["state"]!="ACQUIRED":break
