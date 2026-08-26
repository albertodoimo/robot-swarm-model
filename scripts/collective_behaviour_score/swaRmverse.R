install.packages(c("gganimate"))
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

control_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/multirun/2026-08-25/18-31-17/0/0.csv"
treatment_dir <- "/home/adityamoger/Documents/GitHub/bat-swarm-model/multirun/2026-08-25/18-31-17/2/2.csv"

# Run calculations for each input
results_control <- calculate_scores(control_dir)
results_treatment <- calculate_scores(treatment_dir)

g_metr_control   <- results_control$g_metr      # Contains: pol (polarization)
data_df_control  <- results_control$data_df     # Contains: nnd (nearest neighbor distance)

g_metr_treatment  <- results_treatment$g_metr   # Contains: pol (polarization)
data_df_treatment <- results_treatment$data_df  # Contains: nnd (nearest neighbor distance)

# Add condition labels
data_df_control$condition <- "Control"
data_df_treatment$condition <- "Treatment"
g_metr_control$condition <- "Control"
g_metr_treatment$condition <- "Treatment"

# Combine datasets
combined_data_df <- rbind(data_df_control, data_df_treatment)
combined_g_metr <- rbind(g_metr_control, g_metr_treatment)

# Define consistent color scheme
condition_colors <- c("Control" = "blue", "Treatment" = "red")

# ---- Line Plot for NND (with legend) ----
p_line_nnd <- ggplot(combined_data_df, aes(x = t, y = nnd, color = condition)) + 
  geom_line() +
  scale_color_manual(values = condition_colors, name = "Condition") +
  labs(title = "Nearest Neighbor Distance (NND) Over Time",
       x = "Time",
       y = "NND") +
  theme_minimal()

p_line_nnd

# ---- Box Plot for NND (with legend) ----
p_box_nnd <- ggplot(combined_data_df, aes(x = condition, y = nnd, fill = condition)) +
  geom_boxplot() +
  scale_fill_manual(values = condition_colors, name = "Condition") +
  labs(title = "Nearest Neighbor Distance (NND) Comparison",
       x = "Condition",
       y = "NND") +
  theme_minimal()

p_box_nnd

# ---- Line Plot for Polarization (pol) (with legend) ----
p_line_pol <- ggplot(combined_g_metr, aes(x = t, y = pol_av, color = condition)) + 
  geom_line() +
  scale_color_manual(values = condition_colors, name = "Condition") +
  labs(title = "Polarization Over Time",
       x = "Time",
       y = "Polarization") +
  theme_minimal()

p_line_pol

# ---- Box Plot for Polarization (pol) (with legend) ----
p_violin_pol <- ggplot(combined_g_metr, aes(x = condition, y = pol, fill = condition)) +
  geom_violin() +
  scale_fill_manual(values = condition_colors, name = "Condition") +
  labs(title = "Polarization Comparison",
       x = "Condition",
       y = "Polarization") +
  theme_minimal()

p_violin_pol


p_overlay_nnd <- ggplot(combined_data_df, aes(x = t, y = nnd, color = factor(id))) +
  geom_line(alpha = 0.7) +
  facet_wrap(~ condition) +  # separate control vs treatment side-by-side
  labs(title = "NND Over Time by Individual",
       x = "Time",
       y = "NND",
       color = "Individual ID") +
  theme_minimal()

p_overlay_nnd
p_heatmap_nnd <- ggplot(combined_data_df, aes(x = t, y = factor(id), fill = nnd)) +
  geom_tile() +
  facet_wrap(~ condition, ncol = 1) +
  scale_fill_viridis_c(name = "NND") +
  labs(title = "NND Heatmap (Individual x Time)",
       x = "Time",
       y = "Individual ID") +
  theme_minimal()

p_heatmap_nnd

p_facet_box_nnd <- ggplot(combined_data_df, aes(x = condition, y = nnd, fill = condition)) +
  geom_boxplot() +
  facet_wrap(~ id, scales = "free_y") +
  scale_fill_manual(values = condition_colors, name = "Condition") +
  labs(title = "NND Distribution per Individual",
       x = "Condition",
       y = "NND") +
  theme_minimal() +
  theme(strip.text = element_text(size = 8),
        axis.text.x = element_blank())  # hide x labels since facet labels show id

p_facet_box_nnd

p_neighbor_timeline <- ggplot(combined_data_df, aes(x = t, y = factor(id), color = factor(nn_id))) +
  geom_point(size = 1) +
  facet_wrap(~ condition, ncol = 1) +
  labs(title = "Nearest Neighbor Identity Over Time",
       x = "Time",
       y = "Individual ID",
       color = "Nearest Neighbor ID") +
  theme_minimal()

p_neighbor_timeline

write.csv(g_metr_control, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/control_14_08.csv") 
write.csv(g_metr_treatment, file = "/home/adityamoger/Documents/GitHub/bat-swarm-model/scripts/collective_behaviour_score/treatment_14_08.csv") 

sampling_timestep <- 0.01
# ---- Control ----
new_species_metrics_control <- col_motion_metrics(data_df_control,
                                                  global_metrics = g_metr_control,
                                                  step2time = sampling_timestep,
                                                  verbose = TRUE,
                                                  speed_lim = NA,
                                                  pol_lim = NA
)

# ---- Treatment ----
new_species_metrics_treatment <- col_motion_metrics(data_df_treatment,
                                                    global_metrics = g_metr_treatment,
                                                    step2time = sampling_timestep,
                                                    verbose = TRUE,
                                                    speed_lim = NA,
                                                    pol_lim = NA
)

