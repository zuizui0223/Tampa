#!/usr/bin/env Rscript
# Response-independent Tampa transect geometry registry.
#
# Uses the public tbeptools line dataset that was also used by the pinned
# obis-example conversion to derive transect bearings. No biological response
# is opened here.

TBEPCOMMIT <- "921ef0cfb75218c8c14e9812057ba88fa10be44c"
TRNLNS_URL <- paste0(
  "https://raw.githubusercontent.com/tbep-tech/tbeptools/",
  TBEPCOMMIT, "/data/trnlns.RData"
)
STRLOCS_COMMIT <- "6c567beff95ea04f0e397101befb49d5233ace8f"
STRLOCS_URL <- paste0(
  "https://raw.githubusercontent.com/tbep-tech/obis-example/",
  STRLOCS_COMMIT, "/data/strlocs.rda"
)

args <- commandArgs(trailingOnly = TRUE)
out <- if (length(args)) args[[1]] else "results/generated_bare_control_preflight/transect_geometry_registry.csv"
dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)

tmp1 <- tempfile(fileext = ".RData")
tmp2 <- tempfile(fileext = ".rda")
download.file(TRNLNS_URL, tmp1, mode = "wb", quiet = TRUE)
download.file(STRLOCS_URL, tmp2, mode = "wb", quiet = TRUE)

e1 <- new.env(parent = emptyenv())
load(tmp1, envir = e1)
if (!exists("trnlns", envir = e1, inherits = FALSE)) stop("trnlns object missing")
trnlns <- get("trnlns", envir = e1)

e2 <- new.env(parent = emptyenv())
load(tmp2, envir = e2)
if (!exists("strlocs", envir = e2, inherits = FALSE)) stop("strlocs object missing")
strlocs <- get("strlocs", envir = e2)

initial_bearing <- function(lon1, lat1, lon2, lat2) {
  p1 <- lat1*pi/180
  p2 <- lat2*pi/180
  dl <- (lon2-lon1)*pi/180
  y <- sin(dl)*cos(p2)
  x <- cos(p1)*sin(p2) - sin(p1)*cos(p2)*cos(dl)
  b <- atan2(y,x)*180/pi
  ((b + 180) %% 360) - 180
}

rows <- list()
k <- 1L

for (i in seq_len(nrow(trnlns))) {
  site <- as.character(trnlns$Site[[i]])
  g <- trnlns$geometry[[i]]
  xy <- unclass(g)
  if (is.list(xy) && length(xy) == 1) xy <- xy[[1]]
  xy <- as.matrix(xy)
  if (nrow(xy) < 2 || ncol(xy) < 2) stop(paste("bad line geometry", site))
  lon1 <- as.numeric(xy[1,1]); lat1 <- as.numeric(xy[1,2])
  lon2 <- as.numeric(xy[2,1]); lat2 <- as.numeric(xy[2,2])
  b <- if ("bearing" %in% names(trnlns) && is.finite(as.numeric(trnlns$bearing[[i]]))) {
    as.numeric(trnlns$bearing[[i]])
  } else {
    initial_bearing(lon1,lat1,lon2,lat2)
  }
  rows[[k]] <- data.frame(
    node_short=site,
    start_longitude=lon1,
    start_latitude=lat1,
    bearing_deg=b,
    geometry_source="tbeptools_trnlns",
    source_commit=TBEPCOMMIT,
    stringsAsFactors=FALSE
  )
  k <- k + 1L
}

# strlocs is the explicit fallback used by obis-example for transects not
# covered by trnpts/trnlns. Prefer trnlns whenever both exist.
for (i in seq_len(nrow(strlocs))) {
  site <- as.character(strlocs$transect[[i]])
  if (site %in% vapply(rows, function(x) x$node_short[[1]], character(1))) next
  rows[[k]] <- data.frame(
    node_short=site,
    start_longitude=as.numeric(strlocs$longitude[[i]]),
    start_latitude=as.numeric(strlocs$latitude[[i]]),
    bearing_deg=as.numeric(strlocs$bearing[[i]]),
    geometry_source="obis_strlocs_fallback",
    source_commit=STRLOCS_COMMIT,
    stringsAsFactors=FALSE
  )
  k <- k + 1L
}

reg <- do.call(rbind, rows)
reg <- reg[!duplicated(reg$node_short),]
reg <- reg[order(reg$node_short),]

if (any(!is.finite(reg$start_longitude)) ||
    any(!is.finite(reg$start_latitude)) ||
    any(!is.finite(reg$bearing_deg))) {
  stop("non-finite geometry registry value")
}

write.csv(reg, out, row.names = FALSE, quote = TRUE)
cat(sprintf("geometry registry rows: %d\n", nrow(reg)))
cat(sprintf("tbeptools lines: %d; fallback points: %d\n",
            sum(reg$geometry_source=="tbeptools_trnlns"),
            sum(reg$geometry_source=="obis_strlocs_fallback")))
