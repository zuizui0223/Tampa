function analyze(input){
 const {sites,taxa,data}=input;
 const sum=a=>a.reduce((x,y)=>x+y,0),mean=a=>sum(a)/a.length,gm=a=>Math.exp(mean(a.map(Math.log)));
 const rows=[];
 for(const [month,d] of Object.entries(data)){
   for(let i=0;i<sites.length;i++){
    if(month==="October"&&sites[i]==="BFI")continue;
    const read=arm=>taxa.map((_,j)=>Object.hasOwn(d[arm],j)?d[arm][j][i]:0);
    const v=read("V"),f=read("F");
    if([...v,...f].some(x=>x===null||!Number.isFinite(x)||x<0))throw Error("missing or invalid cells");
    const V=sum(v),F=sum(f);if(V<=0||F<=0)throw Error("nonpositive total");
    const shared=taxa.map((_,j)=>v[j]>0&&f[j]>0),union=taxa.map((_,j)=>v[j]>0||f[j]>0),richV=v.filter(x=>x>0).length,richF=f.filter(x=>x>0).length;
    const sharedDiff=sum(f.map((x,j)=>shared[j]?x-v[j]:0)),flowerOnly=sum(f.filter((x,j)=>x>0&&v[j]===0)),vegOnly=sum(v.filter((x,j)=>x>0&&f[j]===0));
    if(Math.abs(sharedDiff+flowerOnly-vegOnly-(F-V))>1e-8)throw Error("decomposition");
    const bc=sum(v.map((x,j)=>Math.abs(x/V-f[j]/F)))/2;
    const capV=sum(v.slice(0,3)),capF=sum(f.slice(0,3)),nonV=V-capV,nonF=F-capF;
    rows.push({site:sites[i],month,V,F,ratio:F/V,richV,richF,jaccard:shared.filter(Boolean).length/union.filter(Boolean).length,composition_BC:bc,sharedDiff,flowerOnly,vegOnly,capV,capF,nonV,nonF,nonRatio:nonF/nonV,ampithoeV:v[5],ampithoeF:f[5],v,f});
   }
 }
 if(rows.length!==14)throw Error("pair count");
 function summarize(a){const V=mean(a.map(r=>r.V)),F=mean(a.map(r=>r.F)),capDiff=mean(a.map(r=>r.capF-r.capV)),sharedDiff=mean(a.map(r=>r.sharedDiff));return {n:a.length,V,F,ratioMeans:F/V,geometricMeanRatio:gm(a.map(r=>r.ratio)),Fgreater:a.filter(r=>r.F>r.V).length,meanRichnessDifference:mean(a.map(r=>r.richF-r.richV)),meanJaccard:mean(a.map(r=>r.jaccard)),meanCompositionBC:mean(a.map(r=>r.composition_BC)),sharedDiff,flowerOnly:mean(a.map(r=>r.flowerOnly)),vegOnly:mean(a.map(r=>r.vegOnly)),sharedShare:(F-V)!==0?sharedDiff/(F-V):null,capDiff,capShare:(F-V)!==0?capDiff/(F-V):null,nonRatioMeans:mean(a.map(r=>r.nonF))/mean(a.map(r=>r.nonV)),nonGeometricRatio:gm(a.map(r=>r.nonRatio)),nonGreater:a.filter(r=>r.nonF>r.nonV).length}};
 const bySite=Object.fromEntries(sites.map(s=>[s,summarize(rows.filter(r=>r.site===s))]));
 const weighted=(a)=>{let ss=[...new Set(a.map(r=>r.site))].map(s=>summarize(a.filter(r=>r.site===s)));const V=mean(ss.map(x=>x.V)),F=mean(ss.map(x=>x.F));return {V,F,ratioMeans:F/V,geometricRatio:gm(ss.map(x=>x.geometricMeanRatio)),sharedShare:mean(ss.map(x=>x.sharedDiff))/(F-V),capShare:mean(ss.map(x=>x.capDiff))/(F-V),meanRichnessDifference:mean(ss.map(x=>x.meanRichnessDifference)),meanJaccard:mean(ss.map(x=>x.meanJaccard)),nonGeometricRatio:gm(ss.map(x=>x.nonGeometricRatio))}};
 const sharedTaxonDifferences=taxa.map((name,i)=>({name,difference:mean(rows.map(r=>r.f[i]-r.v[i])),positivePairs:rows.filter(r=>r.f[i]>r.v[i]).length,negativePairs:rows.filter(r=>r.f[i]<r.v[i]).length,flowerPositive:rows.filter(r=>r.f[i]>0).length,vegetativePositive:rows.filter(r=>r.v[i]>0).length})).sort((a,b)=>b.difference-a.difference);
 // Source omitted taxon rows coded as no reported mean (0) only for reconstructing table sum.
 // Sensitivity restrict to taxa explicitly listed in both month x shoot tables.
 const restricted=rows.map(r=>{const d=data[r.month],idx=taxa.map((_,i)=>i).filter(i=>Object.hasOwn(d.V,i)&&Object.hasOwn(d.F,i));const V=sum(idx.map(i=>r.v[i])),F=sum(idx.map(i=>r.f[i]));return {site:r.site,month:r.month,V,F,ratio:F/V}});
 return {source:{doi:"10.1111/j.1439-0485.2010.00411.x",citation:"Carr, Boyer & Brooks 2011 Marine Ecology 32:88–103 Tables A1–A2 pp100–101",url:"https://www.researchgate.net/publication/227686046_Spatial_patterns_of_epifaunal_communities_in_San_Francisco_Bay_eelgrass_Zostera_marina_beds"},status:"Executed published-table arithmetic on site-month mean counts; not independent shoots or raw data",taxa,rows,pooled:summarize(rows),siteEqual:weighted(rows),bySite,byMonth:Object.fromEntries(Object.keys(data).map(m=>[m,summarize(rows.filter(r=>r.month===m))])),leaveOneSiteOut:sites.map(s=>({omitted:s,...weighted(rows.filter(r=>r.site!==s))})),sharedTaxonDifferences,explicitRowsOnly:{pairs:restricted,geometricRatio:gm(restricted.map(r=>r.ratio)),positive:restricted.filter(r=>r.F>r.V).length},limits:["Counts per shoot, not per flower, interaction incidence or animal visit rate. No adjustment for actual area, height, branching, epiphytes.","Three months and five sites from one study; no independent study effects; aggregate means, no SE/covariance for new contrasts.","October BFI no flowering shoots sampled; excluded, not zero. April excluded due to no flowering shoot samples. Omitted taxon rows used as no reported abundance, not proven absence. Copepods merged to broad category; richness is count of displayed positive taxonomic categories, not species richness.","Observed differences in total counts/composition are not preferences or evidence of pollination/predation. Caprellids counted as taxonomic group only; unknown function."]};
}
const input={
  "sites": [
    "PSP",
    "CB",
    "KB",
    "BFI",
    "RB"
  ],
  "taxa": [
    "juvenile_caprellids",
    "Caprella_cf_drepanochir",
    "Caprella_californica",
    "juvenile_gammarids",
    "Corophium_alienense",
    "Ampithoe_valida",
    "Jassa_marmorata",
    "Synidotea_lavidorsalis",
    "Idotea_wosnesenskii",
    "Paranthura_elegans",
    "Idotea_resecata",
    "cumaceans",
    "nematodes",
    "copepods_broad",
    "polychaetes",
    "bivalves",
    "gastropods",
    "juvenile_isopods"
  ],
  "data": {
    "June": {
      "V": {
        "0": [
          9.7,
          56.5,
          9.9,
          2255.3,
          86.3
        ],
        "1": [
          18.8,
          10.7,
          4.8,
          289.2,
          0
        ],
        "2": [
          0,
          0,
          0,
          0,
          37.1
        ],
        "3": [
          9.2,
          0.4,
          0,
          19.1,
          9.7
        ],
        "4": [
          23.4,
          3.9,
          1.2,
          215.5,
          12.3
        ],
        "5": [
          0.4,
          0.5,
          0.4,
          0,
          0.1
        ],
        "6": [
          0,
          0,
          0,
          0,
          8.2
        ],
        "8": [
          0,
          0,
          0.1,
          0,
          0
        ],
        "9": [
          0,
          0,
          0,
          0.4,
          0
        ],
        "13": [
          13.9,
          0.3,
          0.9,
          0,
          7.2
        ],
        "14": [
          2.5,
          0,
          0,
          0,
          0.7
        ],
        "15": [
          0.1,
          0.8,
          0,
          0,
          0
        ],
        "16": [
          0.1,
          0,
          0.2,
          0.1,
          0
        ]
      },
      "F": {
        "0": [
          32.9,
          251.2,
          25.4,
          4600.7,
          587.1
        ],
        "1": [
          28.2,
          50.6,
          3.9,
          417.2,
          0
        ],
        "2": [
          0,
          0,
          0,
          0,
          221.3
        ],
        "3": [
          55.3,
          9.9,
          1.8,
          46,
          201.6
        ],
        "4": [
          89.4,
          12.3,
          1.7,
          245.6,
          111.1
        ],
        "5": [
          0.3,
          9.3,
          1.8,
          0,
          1.4
        ],
        "6": [
          0,
          0,
          0,
          0,
          233.3
        ],
        "7": [
          2.9,
          0,
          0,
          0,
          0
        ],
        "8": [
          0,
          0,
          1.2,
          0,
          0
        ],
        "9": [
          0,
          0,
          0,
          3.2,
          1.3
        ],
        "10": [
          0,
          0,
          0,
          0,
          0.9
        ],
        "11": [
          0,
          0,
          0.1,
          0,
          0
        ],
        "13": [
          31.3,
          0.1,
          31.8,
          0,
          12.3
        ],
        "14": [
          3,
          0,
          0,
          0,
          4
        ],
        "15": [
          0.6,
          1.2,
          0,
          0,
          0
        ],
        "16": [
          0,
          0,
          0,
          0,
          0
        ]
      }
    },
    "August": {
      "V": {
        "0": [
          374.7,
          59.2,
          127.9,
          176.9,
          3.6
        ],
        "1": [
          130.9,
          14.1,
          3.9,
          56.4,
          0
        ],
        "2": [
          0,
          0,
          0,
          0,
          2.2
        ],
        "3": [
          3.2,
          0.6,
          0.3,
          0,
          2.6
        ],
        "4": [
          1.9,
          1,
          0.2,
          2.8,
          0.5
        ],
        "5": [
          3.8,
          7,
          0.5,
          0,
          0
        ],
        "6": [
          0,
          0,
          0,
          0,
          6.1
        ],
        "8": [
          0,
          0,
          0.5,
          0,
          0
        ],
        "9": [
          0,
          1,
          0,
          0,
          0
        ],
        "10": [
          0,
          0.1,
          0,
          0,
          0
        ],
        "11": [
          0,
          0.9,
          0,
          0,
          0
        ],
        "12": [
          0,
          0,
          0,
          0,
          0.2
        ],
        "13": [
          37.3,
          0,
          1.1,
          0,
          0.6
        ],
        "14": [
          0,
          0,
          0.4,
          0,
          0.6
        ]
      },
      "F": {
        "0": [
          1318.9,
          347.1,
          440.4,
          1760.5,
          45.6
        ],
        "1": [
          281.1,
          89.2,
          20.7,
          530.2,
          0
        ],
        "2": [
          0,
          0,
          0,
          0,
          12
        ],
        "3": [
          11.5,
          2.2,
          1.9,
          3.2,
          20.1
        ],
        "4": [
          17.9,
          0.8,
          0.2,
          2.8,
          0.5
        ],
        "5": [
          18.1,
          59.1,
          4.3,
          0,
          8.1
        ],
        "6": [
          3.2,
          0,
          0,
          0,
          74.9
        ],
        "8": [
          0,
          0,
          0.5,
          0,
          0
        ],
        "9": [
          0,
          2.2,
          0,
          8,
          1
        ],
        "11": [
          0,
          0,
          0.1,
          0,
          0
        ],
        "12": [
          0,
          0,
          0,
          0,
          0.5
        ],
        "13": [
          49.9,
          0,
          13.3,
          0,
          4.9
        ],
        "14": [
          0.3,
          0,
          0.1,
          0,
          4.6
        ]
      }
    },
    "October": {
      "V": {
        "0": [
          969.6,
          527.8,
          27.6,
          201.8,
          4.3
        ],
        "1": [
          243.2,
          230.5,
          9,
          106.7,
          0
        ],
        "2": [
          0,
          0,
          0,
          0,
          2.9
        ],
        "3": [
          6.4,
          1,
          0.2,
          0,
          2.6
        ],
        "4": [
          2.4,
          0.2,
          0,
          0.1,
          0.2
        ],
        "5": [
          91.2,
          6.2,
          1.3,
          0.2,
          0
        ],
        "6": [
          0,
          0,
          0.4,
          0,
          0.9
        ],
        "9": [
          0,
          0.7,
          0,
          0,
          2.1
        ],
        "10": [
          0,
          0,
          0.3,
          0,
          0
        ],
        "13": [
          0,
          0,
          0,
          0,
          3.6
        ],
        "14": [
          0,
          0,
          0.9,
          0.1,
          1.6
        ]
      },
      "F": {
        "0": [
          904,
          1957.6,
          238.7,
          null,
          0
        ],
        "1": [
          376.9,
          739.4,
          176.3,
          null,
          0
        ],
        "2": [
          0,
          0,
          0,
          null,
          0
        ],
        "3": [
          40,
          0.8,
          22.1,
          null,
          0
        ],
        "4": [
          32.8,
          0.4,
          92.2,
          null,
          0
        ],
        "5": [
          200.8,
          17.6,
          17.3,
          null,
          0
        ],
        "6": [
          0,
          0,
          0.4,
          null,
          0.9
        ],
        "9": [
          12.8,
          0,
          28.3,
          null,
          0
        ],
        "10": [
          0,
          0,
          14.9,
          null,
          0
        ],
        "13": [
          1.6,
          0,
          2,
          null,
          0
        ],
        "14": [
          0,
          0,
          2.3,
          null,
          0
        ],
        "17": [
          0,
          3.2,
          0.4,
          null,
          0
        ]
      }
    }
  }
};
if(require.main===module){const fs=require('fs'),r=analyze(input);if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(r,null,2)+'\n');else console.log(JSON.stringify(r,null,2));}
module.exports=analyze;
