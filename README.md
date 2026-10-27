---
# Dynamic Model of Cocktail Party Nightmare
 Implementing a dynamic model of the cocktail party nightmare problem :)
---

## Installation of environment

Use the environment_cocktail_3.yml alongside conda in order to install all the pre-requistite packages needed to run these simulations. This can be come running;
> conda env create -f environment_cocktail_3.yml

---
## Parameters of the model 

Parameters crucial for the simulation are described in this file. Details about the units are also provided. Search the repo for the specific parameter in order to find out how it is implemented. 

### 1. Parameters related to sound propagation:

1. "SOUND_SPEED": Speed of sound in S.I. units (m/s)
2. "AIR_ABSORPTION": Sound energy absorbed by the medium (dB/m). This is only place where sound frequency range of the bat calls matter within the scope of the model, all sounds are assumed to be of the same frequency of this given absorption. Change this based on the average sound frequency of the bat being modelled. 
3. "REFLECTION_LOSS": Target strength of objects in the simulation, unless otherwise specified (dB SPL). This corresponds to the loss in intensity of sound when it reflects off any object. 
4. "REFLECTION_LOSS_WALL":  Target strength of wall panels in the simulation, unless otherwise specified (dB SPL). This corresponds to the loss in intensity of sound when it reflects off wall panels. Refer to 3.3 for more details about wall panels. 
### 2. Parameters related to simulation time:
1. "SIM_DURATION": Duration for which the simulation needs to be run (s)
2. "TIME_STEP": Step size of each iteration over which computations happen (s). This is the minimum time resolution of the simulation.
3. "FRAME_RATE": Frame rate of the output video (fps)
### 3. Parameters related to the arena and plotting: 
1. "ARENA_WIDTH": Width of the rectangular arena in which bats fly. (m)
2. "ARENA_LENGTH": Length of the rectangular arena in which bats fly. (m)
3. "WALL_RESOLUTION": Resolution of the wall panels (m). Walls only generate echoes from discrete points, this parameter sets the gap between these "echo-generating" points. 
4. "CLEANUP_INTERVAL": Number of iterations after which the agents throw away information stored in local memory. This is done while ensuring that bat decisions aren't affected.
5. "CLEANUP_PLOT_DATA": Periodicity with which the simulation information is stored. This is done in order to ensure that RAM doesn't overload.
6. "OBSTACLE_COUNT": Number of random obstacles to place in the arena. 
7. "OBSTACLE_RADIUS": Radius of each random obstacle (m).
8. "ARENA_TYPE": Type of arena to be used. Options are "BOUNDED" and "OPEN".
### Parameters related to bats:
1. "NUM_BATS": Number of bats in the simulation. 
2. "BAT_SPEED": Speed of the bat (m/s).
3. "BAT_FAST_SPEED": Speed of the bat when it decides to fly faster (m/s).
4. "BAT_RADIUS": Radius of the bat (m).
5. "CALL_DURATION": Duration of the bat call (s). We model FM bats, and hence duration corresponds to the time duration of a **single** call sweep.
6. "CALL_RATE": Frequency of the bat calls (Hz). We model FM bats, and hence frequency corresponds to the rate of emission of sweeps.
7. "CALL_RATE_FAST": Frequency of the bat calls when it decides to call faster (Hz). We model FM bats, and hence frequency corresponds to the rate of emission of sweeps.
8. "EMITTED_SPL": The sound pressure level at which the bat emits the call. (@1 m re 20muPa)
9. "HEARING_SPL": Minimum sound pressure level of a sound required for a bat to detect a sound. (dB SPL) 
10. "PROPENSITY_TO_CHANGE_DIRECTION": Probability that the bat randomly changes its direction. This is only allowed to happen once a call. Usually turned off in the simulation, but is a useful control.
11. "NOISE_IN_CALL_RATE": Noise in call rate (ms). Bat calls are not uniform i.e. 10 Hz call rate does not correspond to 100ms interval between two calls because it is noisy. This parameter handles the noise in the call rate. Noise modelled as a uniform distribution between +/- the value of the parameter.
12. "CALL_DIRECTIONALITY": Directionality factor of the bat call. Bat call intensity falls off with angle, with the highest intensity in the front of the bat and lowest immediately behind it.  
13. "HEARING_DIRECTIONALITY": Directionality factor of the bat's hearing. The same sound is perceived differently based on the angle at which the bat listens to it, highest if it arrives immediately in front of the bat and lowest if it comes from behind.
14. "BAT_ROTATION_SPEED": Rotation speed of the bat (degrees/s)
15. "HEARING_ANGLE_THRESHOLD": Angle of hearing range of the bat (degrees) Sounds outside +/- angle of hearing range from the front of the bat are not heard by the bat. 
16. "SPATIAL_REFERENCE_FRAME": Spatial reference frame w.r.t. which the agent stores information. At the moment there are two implementations of this, "allocentric" and "egocentric". In *egocentric*, information about detected sounds is stored w.r.t. bats direction when it initially heard the sound. In *allocentric*, the information is stored w.r.t. an arbitrary/ random direction which is fixed for the whole duration of the simulation. 
17. "BEHAVIOUR_RULE":  Controller of choice. There are two options at the moment, "avoid-loudest-sound" and "consistency".
18. "KILL_MOVEMENT": *Do you really want to kill an innocent bat (Bool)?!*  Kills the bat's movement thus making it stationary. There is great demand in the market to use dead bats as jammers. :(
### Parameters related to bat signal perception 
1. "IMPLEMENT_SNR": Yes to implement signal to noise ratio based paradigm of sound detection (Bool). Refer to *r"./dynamic_model/utilities/snr_implementation.py"* for more details.
2. "MINIMUM_SOUND_DETECTION_FRACTION": Minimum fraction of the focal sound profile that needs to be above the total masking profile in order to be considered as detected. Refer to *r"./dynamic_model/utilities/snr_implementation.py"* for more details.
### Parameters related to bat behaviour :
1. "TIME_DELAY_FOR_DIRECTION_CHANGE": Time post call after which bat makes a movement decision (s). Information collected during this time is used to make the decision, depending on controller of choice. 
2. "INCLUDE_DIRECT_SOUNDS_IN_RESPONSE":  Yes to include direct sounds in response, else false (Bool). Bats might be capable of telling apart, from the spectral properties, direct sounds of other bats from echoes.
3. "TIME_DELAY_THRESHOLD_FOR_REPULSION":  The maximum delay after call emission a response inducing sound can have in order to elicit a repulsion response in bat (s).

### Parameters related to avoid-loudest-sound controller :
1. "SPL_THRESHOLD_FOR_ATTRACTION": Minimum SPL of loudest sound needed to elicit a attractive maneuver (dB SPL).
2. "SPL_THRESHOLD_FOR_REPULSION":  Minimum SPL of loudest sound needed to elicit a repulsive maneuver (dB SPL).

### Parameters related to consistency controller :
1. "BAT_RADIAL_RESOLUTION": Minimum time difference between two sounds needed for the bat to perceive them as two different sounds (s). 
2. "BAT_ANGULAR_RESOLUTION": Minimum angular separation between two sounds needed for the bat to perceive them as two different sounds (degrees).
3. "MEMORY_WINDOW_FOR_CONSISTENCY": Number of calls over which movement decision is integrated over. Think of this as a moving window, i.e., if the value of this parameter was x, decision after the i-th call occurs after integrating information obtained from (i-x)-th call to i-th call. 
4. "CONVERT_GRIDS+TO_ONE_HOT_?": Yes if you want sound information to be converted to one hot encoding every call, no if you want to normalize based on the total number of sounds (Bool). 
5. "NUMBER_OF_CONSISTENT_IPIS_FOR_MOVEMENT":  Minimum number of calls over which information needs to be heard in order to be considered for response. 
---

## How to run one instance of the simulation
1. Initialize your parameters.
    ./src/paramsets/ contains a set of example paramset files. Fill in your desired parameter values into the cells of the csv file. Be sure to stick to S.I. units while entering parameters. 

2. Change directories in the ./src/simulation_and_plotting/simulation.py file
    change the OUTPUT_DIR (directory where the output is to be saved) and the PARAMETER_FILE_DIR (directory of the parameter file)

3. Run the ./src/simulation_and_plotting/simulation.py file
    this runs one instance of the simulation. 

4. Change directories in the plotter.py or single_bat_plotter.py file
    change the OUTPUT_DIR (directory where the output of the simulation is saved) and SAVE_SIMULATION (False if animation need not be saved, else is the directory where the animation needs to be saved)

5. Run ./src/simulation_and_plotting/plotter.py or ./src/simulation_and_plotting/single_bat_plotter.py depending on the required type of animation and an animation will pop out as a window after it is processed! If a directory was specfied in SAVE_SIMULATION, video is rendered and stored as well.
---

## How to run for varying parameters
1. Run ./src/supporting_files/make_common_parameters.py to generate the template parameter file. This parameter file is stored in ./src/paramsets/common_parameters.csv and contains the defalt values of all the parameters.
2. An example to generate multiple paramsets is given in ./src/paramsets/effect_of_group_size/make_paramset_effect_of_group_size.py. This can be modified for your specific use case.
3. In order to run the simulation over the newly generated parameter files, head to ./src/simulation_multiple_parameters.py and change the following variables
    1. PARAM_DIR - the directory of the folder containing all the paraameter files you wish to run the simulation over
    2. N_RUNS - the numbr of runs each parameter file needs to be run for.
    3. DATA_STORAGE_DIR - the directory where data from all the simulation runs need to be stored. 
    4. MAX_WORKERS - if you wish to limit the number of cores assigned to running the simulation then set this to the desired number. If left blank, the max possible number of cores will be used.

## Implementation of intelligent movement 

1. You attract to "close" objects. However, if object is too close, you repel. 
2. Distance to an object is measured based on the intensity of sound. It uses intensity as a proxy for distance, self echoes are not treated differently. 
3. You only respond to the loudest sound that you receive, X seconds after your call. 
4. Attraction and Repuslion response strengths are linear (w spl). 
    - Say you attract to spls above 93 db and repel sounds above 98 db. The repulsion linear response scales from 93 to 98, with maximum allowed angle change being $\pm$ 0 degree at 93db and $\pm$ 180 degree at 98 dB.
5. Fixed angular speed of 6000 deg/s, 2015 vanderelst et al
6. 