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
                             raw_t = raw$frame, 
                             raw_id = raw$id, 
                             origin = "2026-08-3 12:00:21", 
                             period = "0.01S", 
                             tz = "America/New_York")
  
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
  
  pairwise_df <- pairwise_metrics(data_list = data_dfs,
                                  geo = is_geo,
                                  verbose = TRUE,
                                  parallelize = FALSE,
                                  add_coords = FALSE # could be set to TRUE if the relative positions of neighbors are needed 
  )
  
  # Return both outputs as a named list
  return(list(g_metr = g_metr, data_df = pairwise_df))
  
}

control_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/testing_group_dynamics/4_control/swarmverse_data_19_08_control.csv"
treatment_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/testing_group_dynamics/4/swarmverse_data_19_08.csv"

# Run calculations for each input
results_control <- calculate_scores(control_dir)
results_treatment <- calculate_scores(treatment_dir)

# Unpack into separate named variables
g_metr_control   <- results_control$g_metr
data_df_control  <- results_control$data_df

g_metr_treatment  <- results_treatment$g_metr
data_df_treatment <- results_treatment$data_df

# Plot using g_metr (group metrics)
p <- ggplot() + 
  geom_line(data = g_metr_treatment, aes(x = t, y = pol), color = "red") + 
  geom_line(data = g_metr_control, aes(x = t, y = pol), color = "blue")

p

g_metr_control$condition <- "Control"
g_metr_treatment$condition <- "Treatment"

# Combine both datasets into one dataframe for easy plotting
combined_g_metr <- rbind(g_metr_control, g_metr_treatment)

# Create the box plot
p_box <- ggplot(combined_g_metr, aes(x = condition, y = pol, fill = condition)) +
  geom_boxplot() +
  scale_fill_manual(values = c("Control" = "blue", "Treatment" = "red")) +
  labs(title = "Nearest Neighbor Distance (NND) Comparison",
       x = "Condition",
       y = "pol") +
  theme_minimal() +
  theme(legend.position = "none")

p_box

write.csv(g_metr_control, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/control_14_08.csv") 
write.csv(g_metr_treatment, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/treatment_14_08.csv") 
