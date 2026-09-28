#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly=TRUE)
if(length(args) < 2) stop("usage: Rscript 27_compound_hotfresh_preflight.R INPUT_RDATA OUT_CSV")
inp <- args[[1]]
out <- args[[2]]

e <- new.env(parent=emptyenv())
load(inp, envir=e)
if(!exists("thralltrndat", envir=e, inherits=FALSE)) stop("thralltrndat missing")
d <- as.data.frame(get("thralltrndat", envir=e))

req <- c("bay_segment","station","salithr","tempthr","thrtyp","date","cnt","trnyr")
miss <- setdiff(req, names(d))
if(length(miss)) stop(paste("missing columns", paste(miss,collapse=",")))

x <- d[
  as.character(d$salithr)=="sali_25" &
  as.character(d$tempthr)=="temp_30" &
  as.character(d$thrtyp) %in% c("tempcnt","salicnt","bothcnt"),
  req
]
if(!nrow(x)) stop("no 30C/25ppt stress rows")
x$date <- as.Date(x$date)
x$trnyr <- as.integer(x$trnyr)
x$cnt <- as.logical(x$cnt)
x$thrtyp <- as.character(x$thrtyp)
x <- x[order(x$bay_segment,x$station,x$trnyr,x$thrtyp,x$date),]

maxrun <- function(v){
  v <- v[!is.na(v)]
  if(!length(v)) return(NA_integer_)
  rr <- rle(v)
  z <- rr$lengths[rr$values %in% TRUE]
  if(!length(z)) return(0L)
  as.integer(max(z))
}

keys <- interaction(x$bay_segment,x$station,x$trnyr,x$thrtyp,drop=TRUE,lex.order=TRUE)
spl <- split(x, keys)
rows <- lapply(spl, function(g){
  data.frame(
    bay_segment=as.character(g$bay_segment[[1]]),
    station=as.character(g$station[[1]]),
    trnyr=as.integer(g$trnyr[[1]]),
    stress_type=as.character(g$thrtyp[[1]]),
    interval_start=min(g$date,na.rm=TRUE),
    interval_end=max(g$date,na.rm=TRUE),
    daily_rows=nrow(g),
    stress_days=sum(g$cnt %in% TRUE,na.rm=TRUE),
    max_run_days=maxrun(g$cnt),
    stringsAsFactors=FALSE
  )
})
station <- do.call(rbind,rows)
station <- station[order(station$bay_segment,station$trnyr,station$station,station$stress_type),]

segkeys <- interaction(station$bay_segment,station$trnyr,station$stress_type,drop=TRUE,lex.order=TRUE)
segspl <- split(station,segkeys)
segrows <- lapply(segspl,function(g){
  data.frame(
    bay_segment=as.character(g$bay_segment[[1]]),
    trnyr=as.integer(g$trnyr[[1]]),
    stress_type=as.character(g$stress_type[[1]]),
    station_count=length(unique(g$station)),
    mean_max_run_days=mean(g$max_run_days,na.rm=TRUE),
    median_max_run_days=median(g$max_run_days,na.rm=TRUE),
    mean_stress_days=mean(g$stress_days,na.rm=TRUE),
    median_stress_days=median(g$stress_days,na.rm=TRUE),
    interval_start=min(g$interval_start,na.rm=TRUE),
    interval_end=max(g$interval_end,na.rm=TRUE),
    stringsAsFactors=FALSE
  )
})
segment <- do.call(rbind,segrows)
segment <- segment[order(segment$bay_segment,segment$trnyr,segment$stress_type),]

write.csv(station, sub("\\.csv$","_station.csv",out), row.names=FALSE)
write.csv(segment, out, row.names=FALSE)
cat(sprintf("station_stress_intervals=%d segment_stress_years=%d segments=%d years=%d stress_types=%d\n",
            nrow(station),nrow(segment),length(unique(segment$bay_segment)),
            length(unique(segment$trnyr)),length(unique(segment$stress_type))))
