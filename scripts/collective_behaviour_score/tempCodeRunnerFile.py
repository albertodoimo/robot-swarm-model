e the R script (defines calculate_scores, loads libraries)
# ro.r.source("swaRmverse_compute_score.R")

# # Get the function
# calculate_scores = ro.globalenv["calculate_scores"]

# # Call it with the path to your CSV
# directory = "/home/adityamoger/Documents/GitHub/bat-swarm-model/data/raw/testing_group_dynamics/4/swarmverse_data_19_08.csv"
# result = calculate_scores(directory)  # returns an R list with names g_metr, data_df

# # result is an R ListVector — pull out each element by name
# r_g_metr = result.rx2("g_metr")
# r_pairwise_df = result.rx2("data_df")

# # Convert each to pandas
# with localconverter(ro.default_converter + pandas2ri.converter):
#     g_metr_df = ro.conversion.rpy2py(r_g_metr)
#     pairwise_df = ro.conversion.rpy2py(r_pairwise_df)

# print("Group metrics:")
# print(g_metr_df.head())

# print("Pairwise metrics:")
# print(pairwise_df.head())
