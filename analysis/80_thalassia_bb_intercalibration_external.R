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
        category_difference = abs(a - b)
      )
    }
  }
}
if (!length(rows)) stop("No independent group pairs on same training quadrats")
pairs <- do.call(rbind, rows)

# Pair summaries describe all possible agency comparisons, not independent replicates.
# Use each *quadrat/year* as one equally weighted unit in the primary description.
site_parts <- split(pairs, paste(pairs$year, pairs$site, sep = "::"))
by_quadrat <- do.call(rbind, lapply(site_parts, function(a) {
  data.frame(
    year = a$year[1L], site = a$site[1L],
    number_of_group_pairs = nrow(a),
    exact_agreement = mean(a$category_difference == 0L),
    within_one_agreement = mean(a$category_difference <= 1L),
    mean_abs_rank_difference = mean(a$category_difference),
    stringsAsFactors = FALSE
  )
}))
row.names(by_quadrat) <- NULL
stopifnot(nrow(by_quadrat) >= 3L)
source_records_per_year <- vapply(2024:2026, function(y) sum(d$yr == y), integer(1))
explicit_zero_per_year <- vapply(2024:2026, function(y) sum(d$yr == y & d$cat == 0L), integer(1))

summaries <- lapply(2024:2026, function(yr) {
  yrpairs <- pairs[pairs$year == yr, , drop = FALSE]
  sites <- by_quadrat[by_quadrat$year == yr, , drop = FALSE]
  if (!nrow(yrpairs) || nrow(sites) < 2L)
    stop(paste("Insufficient independent training quadrats in year", yr))
  if(sum(sites$number_of_group_pairs) != nrow(yrpairs))
    stop("Site aggregation lost or duplicated comparison pairs")
  data.frame(
    year = yr,
    original_focal_abundance_records = source_records_per_year[as.character(yr)],
    explicit_zero_records = explicit_zero_per_year[as.character(yr)],
    independent_training_quadrats = nrow(sites),
    dependent_group_pairs = nrow(yrpairs),
    equal_quadrat_exact_agreement = mean(sites$exact_agreement),
    equal_quadrat_within_one_agreement = mean(sites$within_one_agreement),
    equal_quadrat_mean_abs_rank_difference = mean(sites$mean_abs_rank_difference),
    quadrat_exact_agreement_min = min(sites$exact_agreement),
    quadrat_exact_agreement_max = max(sites$exact_agreement),
    pair_weighted_exact_agreement = mean(yrpairs$category_difference == 0L),
    pair_weighted_within_one_agreement = mean(yrpairs$category_difference <= 1L),
    pair_weighted_mean_abs_rank_difference = mean(yrpairs$category_difference),
    presence_absence_disagreement = NA_real_,
    detection_estimability = "NOT_ESTIMABLE_FOCAL_RECORDS_ONLY",
    stringsAsFactors = FALSE
  )
})
result <- do.call(rbind, summaries)
utils::write.csv(result, file.path(outdir, "thalassia_bb_intercalibration_2024_2026.csv"), row.names = FALSE)
utils::write.csv(by_quadrat,
                 file.path(outdir, "thalassia_bb_intercalibration_by_quadrat_2024_2026.csv"),
                 row.names = FALSE)
writeLines(c(
  "MEASUREMENT_LAYER_ONLY / NOT_A_CAUSAL_EFFECT / NOT_A_TAMPA_FUTURE_OUTCOME",
  paste("source_commit:", source_commit),
  paste("verified_upstream_git_blob:", source_blob),
  "8 raw BB values -> ordinal ranks 0 to 7, not percent cover",
  "Inference unit is the original calibration quadrat-year, not a group pair",
  "Equal-quadrat summaries are primary descriptions; pair-weighted summaries are sensitivity",
  "Only 5-6 independent quadrats per year; no nominal pair-level p values or CIs",
  "Presence/absence interobserver disagreement is NOT ESTIMABLE: focal Thalassia abundance records are filtered, and unreported species cannot be treated as zero",
  "Intercalibration quadrats may not represent sparse permanent-meter-mark meadow observations",
  "Group-agreement is not an independent true value or a calibration of latent biological-state error",
  "No TNC association, future ecological response or mechanistic inference tested"
), file.path(outdir, "claim_boundary.txt"))
unlink(temp)
print(result, row.names = FALSE)
cat("PASS: pinned source verified; independent quadrat-weighted measurement audit\n")
