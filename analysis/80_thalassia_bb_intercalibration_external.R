#!/usr/bin/env Rscript
# Frozen-source, response-independent survey intercalibration audit.
# Does not access Tampa TNC, future BB outcome, or any focal ecological-response model.
# Upstream reports: tbep-tech/seagrasstransect-training-reports
# Commit: 9b90538998a0707ddafc13075c1b4715e5fb3290
# Blob: 0335f81880001524541dc66083be9a02b77daa95
#
# Training 'Site' means a shared calibration quadrat, NOT a long-term meter mark.

source_commit <- "9b90538998a0707ddafc13075c1b4715e5fb3290"
source_blob <- "0335f81880001524541dc66083be9a02b77daa95"
url <- paste0(
  "https://raw.githubusercontent.com/tbep-tech/seagrasstransect-training-reports/",
  source_commit, "/data/trndat.rda"
)
outdir <- "results/generated_tnc_baseline_calibration"
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
temp <- tempfile(fileext = ".rda")
options(timeout = max(120, getOption("timeout")))
download.file(url, temp, mode = "wb", quiet = TRUE)
actual_blob <- trimws(system2("git", c("hash-object", temp), stdout = TRUE))
stopifnot(length(actual_blob) == 1, identical(actual_blob, source_blob))

e <- new.env(parent = emptyenv())
objects <- load(temp, envir = e)
stopifnot("trndat" %in% objects)
d <- as.data.frame(e$trndat)
needed <- c("yr", "Site", "grpact", "Species", "var", "aveval")
stopifnot(all(needed %in% names(d)))
d <- d[as.character(d$Species) == "Thalassia" &
         as.character(d$var) == "Abundance" &
         as.integer(as.character(d$yr)) %in% 2024:2026, needed, drop = FALSE]
if (nrow(d) == 0) stop("No exact Thalassia abundance training records")
d$yr <- as.integer(as.character(d$yr))
d$Site <- as.character(d$Site)
d$grpact <- as.character(d$grpact)
d$bb <- suppressWarnings(as.numeric(as.character(d$aveval)))
bb_classes <- c(0, 0.1, 0.5, 1, 2, 3, 4, 5)
d$cat <- vapply(d$bb, function(x) {
  if (!is.finite(x)) return(NA_integer_)
  hits <- which(abs(bb_classes - x) < 1e-7)
  if (length(hits) != 1L) return(NA_integer_)
  as.integer(hits[1] - 1L)
}, integer(1))
if (anyNA(d$cat)) stop("Unexpected BB categories: do not coerce or invent mapping")
keys <- paste(d$yr, d$Site, d$grpact, sep = "|")
if (anyDuplicated(keys)) stop("Duplicate year/site/group: not independent ratings")
if (!all(2024:2026 %in% unique(d$yr))) stop("Expected complete 2024-2026 year set")

rows <- list()
idx <- 0L
for (yr in 2024:2026) {
  by_site <- split(d[d$yr == yr, , drop = FALSE], d$Site[d$yr == yr])
  for (s in names(by_site)) {
    one <- by_site[[s]]
    if (nrow(one) < 2L) next
    vals <- one$cat
    pairs <- utils::combn(seq_along(vals), 2L)
    for (j in seq_len(ncol(pairs))) {
      a <- vals[pairs[1L, j]]; b <- vals[pairs[2L, j]]
      idx <- idx + 1L
      rows[[idx]] <- data.frame(
        year = yr, site = s,
        category_difference = abs(a - b),
        detection_disagreement = as.integer(xor(a == 0L, b == 0L))
      )
    }
  }
}
if (!length(rows)) stop("No independent group pairs on same training quadrats")
pairs <- do.call(rbind, rows)

summaries <- lapply(2024:2026, function(yr) {
  yrpairs <- pairs[pairs$year == yr, , drop = FALSE]
  if (!nrow(yrpairs)) stop(paste("No paired estimates in year", yr))
  data.frame(
    year = yr,
    training_quadrats_with_two_or_more_groups = length(unique(yrpairs$site)),
    number_of_group_pairs = nrow(yrpairs),
    exact_BB_category_agreement = mean(yrpairs$category_difference == 0L),
    within_one_category_agreement = mean(yrpairs$category_difference <= 1L),
    mean_absolute_category_difference = mean(yrpairs$category_difference),
    median_absolute_category_difference = stats::median(yrpairs$category_difference),
    group_pair_presence_zero_disagreement = mean(yrpairs$detection_disagreement),
    stringsAsFactors = FALSE
  )
})
result <- do.call(rbind, summaries)
utils::write.csv(result, file.path(outdir, "thalassia_bb_intercalibration_2024_2026.csv"), row.names = FALSE)
writeLines(c(
  "MEASUREMENT_LAYER_ONLY / NOT_A_CAUSAL_EFFECT / NOT_A_TAMPA_FUTURE_OUTCOME",
  paste("source_commit:", source_commit),
  paste("verified_upstream_git_blob:", source_blob),
  "8 raw BB values -> ordinal ranks 0 to 7, without treating ordinal distance as percent cover",
  "Comparisons are between agencies at same training quadrat; no independent true value",
  "Pair observations within site/year are dependent. Descriptive agreement only.",
  "Training quadrats may not represent difficult sparse Thalassia permanent-meter-mark observations.",
  "Missing species records are not assumed to be zeros. Zero disagreement only for explicit zeros.",
  "Interagency calibration variation is not a complete bound on latent meadow-state measurement error."
), file.path(outdir, "claim_boundary.txt"))
unlink(temp)
print(result, row.names = FALSE)
cat("PASS: pinned source verified; aggregate within-quadrat disagreement only\n")
