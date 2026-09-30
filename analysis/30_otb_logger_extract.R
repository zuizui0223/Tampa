#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly=TRUE)
if(length(args) < 4) stop("usage: Rscript 30_otb_logger_extract.R META_RDATA TEMP_RDATA META_CSV DEPLOY_CSV")

meta_file <- args[[1]]
temp_file <- args[[2]]
meta_out <- args[[3]]
deploy_out <- args[[4]]

em <- new.env(parent=emptyenv())
et <- new.env(parent=emptyenv())
load(meta_file, envir=em)
load(temp_file, envir=et)
if(!exists("metadat", envir=em, inherits=FALSE)) stop("metadat object missing")
if(!exists("tempdat", envir=et, inherits=FALSE)) stop("tempdat object missing")

mobj <- get("metadat", envir=em)
tobj <- get("tempdat", envir=et)

# Avoid requiring sf merely to deserialize the committed metadata snapshot.
ml <- unclass(mobj)
reqm <- c("yr_site_logger","yr","site","logger","deploy_date","stratum","depthm","geometry")
missm <- setdiff(reqm, names(ml))
if(length(missm)) stop(paste("metadata columns missing:", paste(missm, collapse=",")))

geom <- ml[["geometry"]]
xy <- t(vapply(geom, function(pt){
  v <- as.numeric(pt)
  if(length(v) < 2) return(c(NA_real_, NA_real_))
  c(v[[1]], v[[2]])
}, numeric(2)))

meta <- data.frame(
  yr_site_logger=as.character(ml[["yr_site_logger"]]),
  yr=as.integer(ml[["yr"]]),
  site=as.character(ml[["site"]]),
  logger=as.character(ml[["logger"]]),
  deploy_date=as.character(ml[["deploy_date"]]),
  stratum=as.character(ml[["stratum"]]),
  depthm=as.numeric(ml[["depthm"]]),
  longitude=xy[,1],
  latitude=xy[,2],
  stringsAsFactors=FALSE
)
meta <- meta[order(meta$yr,meta$site,meta$logger),]
write.csv(meta, meta_out, row.names=FALSE)

t <- as.data.frame(tobj)
reqt <- c("yr_site_logger","datetime","tempc","yr","site","logger")
misst <- setdiff(reqt, names(t))
if(length(misst)) stop(paste("temperature columns missing:", paste(misst, collapse=",")))
t$yr_site_logger <- as.character(t$yr_site_logger)
t$tempc <- as.numeric(t$tempc)

spl <- split(t, t$yr_site_logger)
rows <- lapply(names(spl), function(k){
  g <- spl[[k]]
  ok <- !is.na(g$datetime) & is.finite(g$tempc)
  g <- g[ok,,drop=FALSE]
  if(!nrow(g)) return(NULL)
  g <- g[order(g$datetime),,drop=FALSE]
  tt <- as.numeric(g$datetime)
  difm <- diff(tt)/60
  difm <- difm[is.finite(difm) & difm > 0]
  data.frame(
    yr_site_logger=k,
    yr=as.integer(g$yr[[1]]),
    site=as.character(g$site[[1]]),
    logger=as.character(g$logger[[1]]),
    rows=nrow(g),
    start_datetime=format(min(g$datetime),tz="America/New_York",usetz=TRUE),
    end_datetime=format(max(g$datetime),tz="America/New_York",usetz=TRUE),
    duration_days=as.numeric(difftime(max(g$datetime),min(g$datetime),units="days")),
    median_interval_minutes=if(length(difm)) median(difm) else NA_real_,
    p95_interval_minutes=if(length(difm)) as.numeric(quantile(difm,0.95,names=FALSE)) else NA_real_,
    temp_min_c=min(g$tempc,na.rm=TRUE),
    temp_median_c=median(g$tempc,na.rm=TRUE),
    temp_max_c=max(g$tempc,na.rm=TRUE),
    stringsAsFactors=FALSE
  )
})
deploy <- do.call(rbind,rows)
deploy <- deploy[order(deploy$yr,deploy$site,deploy$logger),]
write.csv(deploy, deploy_out, row.names=FALSE)

cat(sprintf("metadata_rows=%d deployments=%d temp_rows=%d years=%d\n",
            nrow(meta),nrow(deploy),nrow(t),length(unique(deploy$yr))))
