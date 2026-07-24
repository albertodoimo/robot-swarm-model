import sys

import pandas as pd

sys.path.append("./src")

from supporting_files.utilities import load_parameters

simulation_parameters = load_parameters(
    r"./src/supporting_files/temporal_masking_fn.csv"
)
dict_1 = pd.read_csv(r"./src/supporting_files/temporal_masking_fn.csv")
dict_2 = {}

for key in dict_1.keys()[1:]:
    dict_2[key] = dict_1[key].values

print(dict_1)
print(dict_2)
print(dict_2)
print(dict_2)
