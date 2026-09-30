#!/usr/bin/env Rscript
# Response-independent calendar feasibility preflight for Tampa event-stress debt.
#
# Uses only the pinned Beck et al. daily GAM exposure artifact.
# No Tampa seagrass/TNC response is read.
#
# Goal: choose a fixed 42-day calendar window that historically maximizes
# broad occurrence of the already-frozen 30 C AND 25 ppt joint condition.
# Thresholds and window length are NOT optimized here.
#
# Frozen selection rule:
#   1) for every possible non-wrapping 42-day start day (non-leap calendar),
#      estimate bay-specific fraction of station-years with >=1 joint day;
#   2) rank windows by the SECOND-HIGHEST bay-specific fraction, matching the
#      prospective variation gate that requires non-zero exposure in >=2 bays;
#   3) tie-break by overall station-year nonzero fraction;
#   4) tie-break by overall mean joint days per station-year;
#   5) final tie-break = earliest calendar start.
#
# This selects a deployment season from environmental climatology only.

args <- commandArgs(trailingOnly=TRUE)
if(length(args) != 2) stop("usage: Rscript 59_event_stress_calendar_preflight.R INPUT.RData OUTPUT.json")
inp <- args[[1]]
out <- args[[2]]

load(inp)
if(!exists("thralltrndat")) stop("thralltrndat not found in RData")
x <- thralltrndat

req <- c("bay_segment","station","salithr","tempthr","thrtyp","date","cnt")
miss <- setdiff(req, names(x))
if(length(miss)) stop(paste("missing fields:", paste(miss, collapse=",")))

x <- x[
  x$bay_segment %in% c("OTB","MTB","LTB") &
  x$salithr == "sali_25" &
  x$tempthr == "temp_30" &
  x$thrtyp == "bothcnt",
]

x$date <- as.Date(x$date)
x$year <- as.integer(format(x$date, "%Y"))
x <- x[x$year >= 1998 & x$year <= 2022,]
x <- x[format(x$date, "%m-%d") != "02-29",]
if(!nrow(x)) stop("no eligible joint daily rows")

# Normalized non-leap day-of-year.
refyear <- 2001
x$md <- format(x$date, "%m-%d")
x$doy365 <- as.integer(format(as.Date(paste0(refyear,"-",x$md)), "%j"))
x$cnt <- as.logical(x$cnt)

window_days <- 42L
starts <- 1:(365L-window_days+1L)
core <- c("OTB","MTB","LTB")

summ <- vector("list", length(starts))

for(ii in seq_along(starts)){
  s <- starts[[ii]]
  e <- s + window_days - 1L
  w <- x[x$doy365 >= s & x$doy365 <= e,]

  # one row per station-year
  key <- interaction(w$bay_segment,w$station,w$year,drop=TRUE)
  split_idx <- split(seq_len(nrow(w)), key)
  sy <- lapply(split_idx, function(idx){
    z <- w[idx,]
    data.frame(
      bay_segment=z$bay_segment[[1]],
      station=as.character(z$station[[1]]),
      year=z$year[[1]],
      joint_days=sum(z$cnt,na.rm=TRUE),
      available_days=sum(!is.na(z$cnt)),
      stringsAsFactors=FALSE
    )
  })
  sy <- do.call(rbind,sy)
  sy <- sy[sy$available_days >= 35,]
  if(!nrow(sy)) next

  by <- lapply(core,function(b){
    z <- sy[sy$bay_segment==b,]
    if(!nrow(z)) return(c(frac=NA,mean_days=NA,n=0))
    c(
      frac=mean(z$joint_days>0),
      mean_days=mean(z$joint_days),
      n=nrow(z)
    )
  })
  names(by) <- core
  fr <- sapply(by,function(z) z[["frac"]])
  valid_fr <- sort(fr[is.finite(fr)],decreasing=TRUE)
  second_highest <- if(length(valid_fr)>=2) valid_fr[[2]] else NA_real_

  overall_frac <- mean(sy$joint_days>0)
  overall_mean <- mean(sy$joint_days)

  start_date <- as.Date("2001-01-01") + (s-1L)
  end_date <- as.Date("2001-01-01") + (e-1L)

  summ[[ii]] <- data.frame(
    start_doy=s,
    end_doy=e,
    start_md=format(start_date,"%m-%d"),
    end_md=format(end_date,"%m-%d"),
    second_highest_bay_nonzero_fraction=second_highest,
    overall_nonzero_fraction=overall_frac,
    overall_mean_joint_days=overall_mean,
    OTB_nonzero_fraction=fr[["OTB"]],
    MTB_nonzero_fraction=fr[["MTB"]],
    LTB_nonzero_fraction=fr[["LTB"]],
    OTB_station_years=by[["OTB"]][["n"]],
    MTB_station_years=by[["MTB"]][["n"]],
    LTB_station_years=by[["LTB"]][["n"]],
    stringsAsFactors=FALSE
  )
}
res <- do.call(rbind,summ)
res <- res[is.finite(res$second_highest_bay_nonzero_fraction),]

ord <- order(
  -res$second_highest_bay_nonzero_fraction,
  -res$overall_nonzero_fraction,
  -res$overall_mean_joint_days,
  res$start_doy
)
res <- res[ord,]
best <- res[1,]

# Additional year-level robustness for chosen window.
bw <- x[x$doy365 >= best$start_doy & x$doy365 <= best$end_doy,]
years <- sort(unique(bw$year))
year_rows <- lapply(years,function(y){
  yy <- bw[bw$year==y,]
  vals <- sapply(core,function(b){
    z <- yy[yy$bay_segment==b,]
    if(!nrow(z)) return(NA_real_)
    # fraction of available stations with at least one joint day in this window
    sp <- split(seq_len(nrow(z)), z$station)
    jd <- sapply(sp,function(idx) sum(z$cnt[idx],na.rm=TRUE))
    mean(jd>0)
  })
  data.frame(
    year=y,
    OTB_nonzero_station_fraction=vals[["OTB"]],
    MTB_nonzero_station_fraction=vals[["MTB"]],
    LTB_nonzero_station_fraction=vals[["LTB"]],
    bays_with_any_station_event=sum(vals>0,na.rm=TRUE),
    stringsAsFactors=FALSE
  )
})
yr <- do.call(rbind,year_rows)

# JSON without external packages.
esc <- function(s) gsub('"','\\\"',as.character(s),fixed=TRUE)
num <- function(x) ifelse(is.finite(x),sprintf("%.10g",x),"null")

topn <- head(res,10)
topjson <- sapply(seq_len(nrow(topn)), function(i){
  r <- topn[i,]
  paste0(
    '{"start_md":"',r$start_md,'","end_md":"',r$end_md,
    '","second_highest_bay_nonzero_fraction":',num(r$second_highest_bay_nonzero_fraction),
    ',"overall_nonzero_fraction":',num(r$overall_nonzero_fraction),
    ',"overall_mean_joint_days":',num(r$overall_mean_joint_days),
    ',"OTB_nonzero_fraction":',num(r$OTB_nonzero_fraction),
    ',"MTB_nonzero_fraction":',num(r$MTB_nonzero_fraction),
    ',"LTB_nonzero_fraction":',num(r$LTB_nonzero_fraction),'}'
  )
})

yr_any2 <- mean(yr$bays_with_any_station_event>=2,na.rm=TRUE)
yr_any3 <- mean(yr$bays_with_any_station_event>=3,na.rm=TRUE)

json <- paste0(
'{
  "schema":"tampa.event_stress_calendar_preflight_v1",
  "status":"calendar_selected_from_response_independent_exposure_climatology",
  "response_independent":true,
  "source":{
    "repository":"tbep-tech/temp-manu",
    "commit":"e5aaec93c7501fc38c63b615a89e68636b36421f",
    "path":"data/thralltrndat.RData",
    "git_blob_sha1":"f6518ea25685369057bfe92e71973ec04c57eac1",
    "years":[1998,2022]
  },
  "frozen_inputs":{
    "temperature_threshold_c":30,
    "salinity_threshold_ppt":25,
    "window_days":42,
    "core_bays":["OTB","MTB","LTB"]
  },
  "selection_rule":{
    "primary":"maximize second-highest bay-specific fraction of station-years with >=1 joint day",
    "tie_break_1":"maximize overall station-year nonzero fraction",
    "tie_break_2":"maximize overall mean joint days per station-year",
    "tie_break_3":"earliest calendar start",
    "rationale":"align calendar selection with the prospective variation gate requiring nonzero exposure in at least two bays while avoiding biological-response optimization"
  },
  "selected_window":{
    "start_md":"',best$start_md,'",
    "end_md":"',best$end_md,'",
    "second_highest_bay_nonzero_fraction":',num(best$second_highest_bay_nonzero_fraction),',
    "overall_nonzero_fraction":',num(best$overall_nonzero_fraction),',
    "overall_mean_joint_days":',num(best$overall_mean_joint_days),',
    "OTB_nonzero_fraction":',num(best$OTB_nonzero_fraction),',
    "MTB_nonzero_fraction":',num(best$MTB_nonzero_fraction),',
    "LTB_nonzero_fraction":',num(best$LTB_nonzero_fraction),',
    "historical_year_fraction_with_events_in_at_least_2_bays":',num(yr_any2),',
    "historical_year_fraction_with_events_in_all_3_bays":',num(yr_any3),'
  },
  "top_10_windows":[',paste(topjson,collapse=","),'],
  "decision_boundary":[
    "This preflight selects deployment season only; it does not alter the frozen 30 C or 25 ppt thresholds or 42-day duration.",
    "Daily GAM predictions are used for climatological calendar feasibility, not as substitutes for future node-scale <=15-minute exposure.",
    "The selected future deployment dates must use this month-day window unless field safety/logistics make the prospective study impossible; do not shift the window after observing TNC.",
    "If the future variation gate fails despite this calendar, classify the primary exposure non-estimable rather than retuning the calendar or thresholds."
  ]
}
')

dir.create(dirname(out),recursive=TRUE,showWarnings=FALSE)
writeLines(json,out)
cat(json,"
")
