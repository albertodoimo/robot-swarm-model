install.packages("theme_ipsum")
library(swaRmverse)
library(ggplot2)
# raw <- read.csv(system.file("swarmverse_data.csv", package = "trackdf"))
raw<-read.csv("/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/attraction_loudest_sound/sustained_sounds/20_bats/2_control/swarmverse_data_control_2.csv")
# raw <- raw[!raw$ignore, ]
head(raw)

data_df <- set_data_format(raw_x = raw$x,
                            raw_y = raw$y, 
                            raw_t=raw$frame, 
                            raw_id=raw$id, 
                            origin = "2026-08-3 12:00:21", 
                            period = "0.01S", 
                            tz= "America/New_York")


head(data_df)
is_geo <- FALSE
data_dfs <- add_velocities(data_df,
                           geo = is_geo,
                           verbose = TRUE,
                           parallelize = FALSE
                           ) ## A list of dataframes

print(paste("Velocity information added for", length(data_dfs), "sets."))

sampling_timestep <- 0.01
time_window <- 1 # seconds
smoothing_time_window <- time_window / sampling_timestep

g_metr <- group_metrics_per_set(data_list = data_dfs,
                               mov_av_time_window = smoothing_time_window,
                               step2time = sampling_timestep,
                               geo = is_geo,
                               parallelize = FALSE
                               )
summary(g_metr)
head(g_metr)
data_df <- pairwise_metrics(data_list = data_dfs,
                            geo = is_geo,
                            verbose = TRUE,
                            parallelize = FALSE,
                            add_coords = FALSE # could be set to TRUE if the relative positions of neighbors are needed 
                            )
tail(data_df)

new_species_metrics <- col_motion_metrics(data_df,
                                           global_metrics = g_metr,
                                           step2time = sampling_timestep,
                                           verbose = TRUE,
                                           speed_lim = NA,
                                           pol_lim = NA
)
summary(new_species_metrics)
write.csv(new_species_metrics) # OR R object
write.csv(new_species_metrics, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/pathfile_control.csv") 
write.csv(g_metr, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/control_global_metrics.csv")

head(new_species_metrics)

ggplot(g_metr, aes(x=t, y=pol)) +
  geom_line( color="#69b3a2", size=2, alpha=0.9, linetype=2) +
  ggtitle("Evolution of something")



calculate_scores <- function(directory){
  raw <- read.csv(directory)
  
  data_df <- set_data_format(raw_x = raw$x,
                             raw_y = raw$y, 
                             raw_t=raw$frame, 
                             raw_id=raw$id, 
                             origin = "2026-08-3 12:00:21", 
                             period = "0.01S", 
                             tz= "America/New_York")
  
  is_geo <- FALSE
  
  data_dfs <- add_velocities(data_df,
                             geo = is_geo,
                             verbose = TRUE,
                             parallelize = FALSE
  ) ## A list of dataframes
  
  print(paste("Velocity information added for", length(data_dfs), "sets."))
  
  sampling_timestep <- 0.01
  time_window <- 1 # seconds
  smoothing_time_window <- time_window / sampling_timestep
  
  g_metr <- group_metrics_per_set(data_list = data_dfs,
                                  mov_av_time_window = smoothing_time_window,
                                  step2time = sampling_timestep,
                                  geo = is_geo,
                                  parallelize = FALSE
  )
  data_df <- pairwise_metrics(data_list = data_dfs,
                             geo = is_geo,
                             verbose = TRUE,
                             parallelize = FALSE,
                             add_coords = FALSE # could be set to TRUE if the relative positions of neighbors are needed 
  )
  return(data_df)
  
}

control_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/working_attraction_model/6_control/swarmverse_data_14_08_control.csv"
treatment_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/working_attraction_model/6/swarmverse_data_14_08_treatment.csv"

g_metr_control <- calculate_scores(control_dir)
g_metr_treatment <- calculate_scores(treatment_dir)

p <- ggplot() + geom_line(data=g_metr_treatment, aes(x=t, y=nnd, z=id), color= "red") + 
  geom_line(data=g_metr_control, aes(x=t, y=nnd, z=id), color = "blue")

p
