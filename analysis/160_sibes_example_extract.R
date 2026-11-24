# Author's example R object. Never label this as complete until coverage is checked.
dir <- "ragworm_retry"
f <- file.path(dir,"SIBES_dataset.rda")
if (!file.exists(f)) quit(status=0)
e <- new.env()
load(f,envir=e)
stopifnot(exists("SIBES_dataset",envir=e))
d <- get("SIBES_dataset",envir=e)
stopifnot(all(c("biota","species","samples") %in% names(d)))
sp <- as.data.frame(d$species); bi <- as.data.frame(d$biota); sa <- as.data.frame(d$samples)
print(lapply(list(species=sp,biota=bi,samples=sa),function(z) list(n=nrow(z),columns=names(z))))
stopifnot(all(c("name","sibes_id") %in% names(sp)),all(c("sample_id","sibes_id","abundance_m2","afdm_m2") %in% names(bi)),all(c("sample_id","sampling_station_id","date","tidal_basin_name") %in% names(sa)))
id <- sp$sibes_id[tolower(trimws(sp$name))=="hediste diversicolor"]
stopifnot(length(id)==1L,!anyDuplicated(sa$sample_id))
b <- bi[bi$sibes_id==id & !is.na(bi$sibes_id),]
stopifnot(nrow(b)>0,!anyDuplicated(b$sample_id),all(b$sample_id %in% sa$sample_id))
write.csv(sp,file.path(dir,"example_taxonomy.csv"),row.names=FALSE)
# Only publish focal taxon and sample metadata needed for analysis, not the full RDA.
write.csv(b,file.path(dir,"example_hediste.csv"),row.names=FALSE)
write.csv(sa,file.path(dir,"example_samples.csv"),row.names=FALSE)
cat("Example source coverage: ",nrow(sa),"samples,",length(unique(sa$sampling_station_id)),"stations,",paste(range(as.Date(sa$date)),collapse=" to "),"\n")
