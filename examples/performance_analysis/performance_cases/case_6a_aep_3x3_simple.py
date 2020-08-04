# Copyright 2020 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# See https://floris.readthedocs.io for documentation

# In the second case, simply time calls to calculate_wake

import time
import pickle
import itertools

import numpy as np

import floris.tools as wfct
import matplotlib.pyplot as plt


# PARAMETERS
recompute_baseline = True
show_layout = True
turn_off_gch = True

# Fixed parameters
N_row = 10


# Initialize the FLORIS interface fi
# For basic usage, the florice interface provides a simplified interface to
# the underlying classes
fi = wfct.floris_interface.FlorisInterface("../../example_input.json")

if turn_off_gch:
    fi.set_gch(False)

# Set to a 5 turbine case
D = fi.floris.farm.turbines[0].rotor_diameter
spc = 5
layout_x = []
layout_y = []
for i in range(N_row):
    for k in range(N_row):
        layout_x.append(i * spc * D)
        layout_y.append(k * spc * D)
N_turb = len(layout_x)

fi.reinitialize_flow_field(
    layout_array=(layout_x, layout_y), wind_direction=[270.0], wind_speed=[8.0]
)
fi.calculate_wake()

# Set up the wind rose assuming every wind speed and direction equaly likely
ws_list = np.arange(1, 26, 1)
wd_list = np.arange(0, 360, 5)
combined = np.array(list(itertools.product(ws_list, wd_list)))
ws_list = combined[:, 0]
wd_list = combined[:, 1]
num_cases = len(ws_list)
freq = np.ones_like(ws_list) / num_cases


# Compute and time the AEP calculation


# # Now check the timing
print("===START TEST===")
start = time.time()
power_result = fi.get_farm_AEP(wd_list, ws_list, freq)
end = time.time()
elapsed_time = end - start


# Report the timing
print("====RESULT====")
print("*** 3x3 AEP takes on average %.1f seconds" % (elapsed_time))
print("*** exact result in s -> %f" % elapsed_time)

# Now check if result has changed
if recompute_baseline:
    pickle.dump(power_result, open("result_case_6a.p", "wb"))
else:
    saved_result = pickle.load(open("result_case_6a.p", "rb"))

    power_difference = power_result - saved_result

    if np.max(np.abs(power_difference)) == 0.0:
        print("*** AEP result unchanged from baseline")

    else:
        print("xxx Power result has changed")
        percent_change = 100 * (power_result - saved_result) / saved_result
        print(
            "xxx Total power changed by %+.1f%% (%.1f -> %.1f)"
            % (percent_change, saved_result, power_result)
        )


if show_layout:
    # Plot and show
    # Get horizontal plane at default height (hub-height)
    hor_plane = fi.get_hor_plane()
    fig, ax = plt.subplots()
    wfct.visualization.visualize_cut_plane(hor_plane, ax=ax)
    plt.show()
