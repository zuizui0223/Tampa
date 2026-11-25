#!/usr/bin/env python3
"""Exact source-member retrieval for local reproductive analysis.
Public Dryad archives only; no raw data committed. Prior inventory run 45371643990.
"""
import hashlib, io, json, zipfile, urllib.request, urllib.error
from pathlib import Path
ROOT=Path("reproductive_input")
SOURCES={
    "johnson": (50250, {
       "Seedling_Competition_Exp_MASTER.csv":"97918fffb039b7111c7825cdaa331c8be38d3c7b1c2b1883e4b53a3330666385",
       "Meta_Data_Seedling_Competition.csv":"c05d06ebeccb51a56f9ee254ab403f025495c2368315348dd229455618f75689",
       "Random_Core_Data_Natural_Seedling_Survey_and_Potential_Seed_Limitation.csv":"8101eb6199400569670b61e119c296f52c705537980088bc289bc1b19e14964d",
       "Natural_Seedling_Survey_and_Potential_Seed_Limitation_Metadata.csv":"3def11f4261fb8d619794b8ddf881c21ac6fe93551a36ce04f242d3359366908",
       "Model_Data_1m2_Transplant_Garden_Plots_No_bare_sed._control.csv":"e0400b05730cdd98fb7deef006391dfac374657de1d4c7cb01ebf6f713351e79",
       "Model_Data_4m2_transplant_garden_plots_NO_bare_sed._control.csv":"ba62a1af4359e5b388fe60d1c08b3c7bc9ee87dc6a37ac1149c679b1a0ca8904",
       "Adult_Shoot_Neighbors_and_Seedling_Survival_Lockwasher_MASTER.csv":"bae201c4c6986232e6b851500d217d06bdc69b194bc5c08575852fb9358d18ac",
       "Adult_Shoot_Neighbors_and_Seedling_Survival_Adult_Shoot_Counts.csv":"535fcf130da44cd039a9199791f9a8cab782ba0e541ec3300c0ed054a6c48acd",
       "Adult_Shoot_Neighbors_and_Seedling_Survival_Metadata_Sheet.xlsx":"6ea0f6bd6f4821793e11436244309fa18a9245ff8c7583ac36a04bec0f2b289d"}),
    "kendrick": (283088, {
       "inflor_shoot_ReprodEffort_2013-2018.csv":"405e75b888bef02df40c8746dc8db1a0a2afb41c7f2d7a55c9347ae39ed2f8cd",
       "flower_Fruit_and_ratio_2013-2018.csv":"249076a1ae7a0118020d3142a8fb2962b2eceb783caca861312b7c858e7d159b",
       "Recruitment_14_18.csv":"0ca8b775da4778e84ea4b1dc66dc8acc92058ad2622cfd9e219ebccd51ee59b5",
       "README.txt":"c1a26400068324a9aa0b35da8761bc5e127328865aaa90975a5085900645d1cb",
       "README.md":"3bc876b704538f77a4d4d71d405f4bb7ec951056c137fed4b57398ff30c4d9c0"}),
    "balestri": (132602, {"Copia_di_Dataset_publication.xlsx":"cbfc07553ee6e071e83579784171c66d6dab8dcc589e2bdb92ee11d74d1aa2b1"}),
    "yu": (24040, {"Ramets For Two plots.xlsx":"10e1465ac9255ad2d873d6142386b5140320740ebc660196b4a9eb0e2251c959"}),
}
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Tampa-reproductive-audit/1.0","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=45) as r:
        raw=r.read(20_000_001)
    if len(raw)>20_000_000: raise ValueError("download cap")
    return raw
def sha(raw): return hashlib.sha256(raw).hexdigest()
def extract(name,version,expected):
    url=f"https://datadryad.org/api/v2/versions/{version}/download"
    raw=fetch(url)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(x.file_size for x in z.infolist())>50_000_000: raise ValueError("expansion cap")
        members={k:z.read(k) for k in expected}
        if any(sha(v)!=expected[k] for k,v in members.items()): raise ValueError("member hash drift")
    dest=ROOT/name; dest.mkdir(parents=True,exist_ok=True)
    for k,v in members.items(): (dest/k).write_bytes(v)
    return {"name":name,"version":version,"archive_sha256":sha(raw),"member_hashes":expected,
            "status":"EXACT_MEMBERS_ACQUIRED"}
def alternatives():
    # Published DOI route, never guess unknown version/file IDs.
    urls={"foster_dataset_download":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.ns1rn8pt4/download",
          "foster_version_files":"https://datadryad.org/api/v2/versions/128223/files",
          "kendrick_genotypes_metadata":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.dfn2z3577"}
    out=[]
    for name,url in urls.items():
        try:
            raw=fetch(url)
            item={"name":name,"status":"retrieved","bytes":len(raw),"sha256":sha(raw)}
            if zipfile.is_zipfile(io.BytesIO(raw)):
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    item["archive_members"]=z.namelist()
                # Not yet source-locked; metadata only, no outcome fits.
            else:
                meta=json.loads(raw)
                item["links"]=meta.get("_links",{})
                item["title"]=meta.get("title")
                if name=="foster_version_files":
                    item["files"]=[{"path":x.get("path"),"links":x.get("_links",{})} for x in (meta.get("_embedded",{}).get("stash:files",[]))]
            out.append(item)
        except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
            out.append({"name":name,"status":"STOP","reason":str(e)[:200]})
    return out
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    out=[]
    for name,(version,members) in SOURCES.items():
        try: out.append(extract(name,version,members))
        except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
            out.append({"name":name,"status":"STOP","reason":str(e)[:200]})
    report={"sources":out,"alternatives":alternatives(),"scope":"Source files only, not ecological estimates. Cite the original Dryad datasets; no raw files committed."}
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if not any(x["status"]=="EXACT_MEMBERS_ACQUIRED" for x in out): raise SystemExit("No exact members acquired")
