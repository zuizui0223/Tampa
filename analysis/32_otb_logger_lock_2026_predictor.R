#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly=TRUE)
if(length(args) < 4) stop("usage: Rscript 32_otb_logger_lock_2026_predictor.R TEMP_RDATA CROSSWALK_CSV DEPLOY_OUT NODE_OUT")
temp_file <- args[[1]]
cross_file <- args[[2]]
deploy_out <- args[[3]]
node_out <- args[[4]]

e <- new.env(parent=emptyenv())
load(temp_file, envir=e)
if(!exists("tempdat", envir=e, inherits=FALSE)) stop("tempdat object missing")
t <- as.data.frame(get("tempdat", envir=e))
cw <- read.csv(cross_file, stringsAsFactors=FALSE)

reqt <- c("yr_site_logger","datetime","tempc")
reqc <- c("yr_site_logger","yr","deploy_date","qualified_temporal","primary_spatial_match",
          "nearest_fixed_node","nearest_fixed_distance_km","site")
if(length(setdiff(reqt,names(t)))) stop("temperature columns missing")
if(length(setdiff(reqc,names(cw)))) stop("crosswalk columns missing")

cw26 <- cw[cw$yr == 2026 & cw$qualified_temporal %in% c(TRUE,"True","TRUE",1),,drop=FALSE]
if(!nrow(cw26)) stop("no qualified 2026 deployments")
keys <- unique(cw26$yr_site_logger)
t <- t[t$yr_site_logger %in% keys & !is.na(t$tempc),,drop=FALSE]
if(!nrow(t)) stop("no qualified 2026 temperature rows")

spl <- split(t,t$yr_site_logger)
rows <- lapply(names(spl),function(k){
  g <- spl[[k]]
  x <- as.numeric(g$tempc)
  data.frame(
    yr_site_logger=k,
    temperature_rows=length(x),
    mean_temp_c=mean(x,na.rm=TRUE),
    median_temp_c=median(x,na.rm=TRUE),
    max_temp_c=max(x,na.rm=TRUE),
    fraction_ge_30=mean(x >= 30,na.rm=TRUE),
    heat_load_30=mean(pmax(x-30,0),na.rm=TRUE),
    stringsAsFactors=FALSE
  )
})
met <- do.call(rbind,rows)
d <- merge(cw26,met,by="yr_site_logger",all.x=TRUE,sort=FALSE)
if(any(is.na(d$heat_load_30))) stop("missing deployment heat metric")

# Normalize within deployment date, as recommended by the OTB logger programme
# when comparing spatial temperature among non-contemporaneous deployment rounds.
d$heat_load_30_deploy_mean <- ave(d$heat_load_30,d$deploy_date,FUN=mean)
d$heat_load_30_anomaly <- d$heat_load_30-d$heat_load_30_deploy_mean
d$mean_temp_deploy_mean <- ave(d$mean_temp_c,d$deploy_date,FUN=mean)
d$mean_temp_anomaly <- d$mean_temp_c-d$mean_temp_deploy_mean

write.csv(d[order(d$deploy_date,d$site),],deploy_out,row.names=FALSE)

m <- d[d$primary_spatial_match %in% c(TRUE,"True","TRUE",1),,drop=FALSE]
if(!nrow(m)) stop("no primary spatial matches in 2026")
spln <- split(m,m$nearest_fixed_node)
node_rows <- lapply(names(spln),function(node){
  g <- spln[[node]]
  data.frame(
    nearest_fixed_node=node,
    matched_deployments=nrow(g),
    logger_sites=length(unique(g$site)),
    deployment_dates=length(unique(g$deploy_date)),
    mean_nearest_distance_km=mean(g$nearest_fixed_distance_km),
    primary_heat_load_30_anomaly=mean(g$heat_load_30_anomaly),
    diagnostic_mean_temp_anomaly=mean(g$mean_temp_anomaly),
    diagnostic_fraction_ge_30=mean(g$fraction_ge_30),
    diagnostic_max_temp_c=max(g$max_temp_c),
    stringsAsFactors=FALSE
  )
})
node <- do.call(rbind,node_rows)
node <- node[order(node$nearest_fixed_node),]
if(nrow(node)!=6) stop(sprintf("expected 6 locked fixed nodes, got %d",nrow(node)))
write.csv(node,node_out,row.names=FALSE)
print(node)
