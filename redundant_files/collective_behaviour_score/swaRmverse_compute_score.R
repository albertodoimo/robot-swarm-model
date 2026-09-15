required_pkgs <- c("swaRmverse", "arrow", "ggplot2")

for (pkg in required_pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}


library(arrow)
library(swaRmverse)


calculate_scores <- function(directory){
  raw <- read.csv(directory)
  
  data_df <- set_data_format(raw_x = raw$x, raw_y = raw$y, raw_t = raw$frame, raw_id = raw$id,
                              origin = "2026-08-3 12:00:21", period = "0.01S", tz = "America/New_York")
  
  is_geo <- FALSE
  data_dfs <- add_velocities(data_df, geo = is_geo, verbose = TRUE, parallelize = FALSE)
  
  sampling_timestep <- 0.01
  smoothing_time_window <- 1 / sampling_timestep
  
  g_metr <- group_metrics_per_set(data_list = data_dfs, mov_av_time_window = smoothing_time_window,
                                   step2time = sampling_timestep, geo = is_geo, parallelize = FALSE)
  
  pairwise_df <- pairwise_metrics(data_list = data_dfs, geo = is_geo, verbose = TRUE,
                                   parallelize = FALSE, add_coords = FALSE)
  
  list(g_metr = g_metr, data_df = pairwise_df)
}

args <- commandArgs(trailingOnly = TRUE)
input_csv <- args[1]
out_dir <- dirname(input_csv)

result <- calculate_scores(input_csv)
write_parquet(result$g_metr, file.path(out_dir, "g_metr.parquet"))
write_parquet(result$data_df, file.path(out_dir, "pairwise.parquet"))