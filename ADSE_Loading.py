from ADSE_Tables import aircraft, MAC, X_LEMAC, MTOW, cargo_weight_fore, cargo_weight_aft, cargo_cg_aft_upt, cargo_cg_fore_upt
import numpy as np
import matplotlib.pyplot as plt

cg_MAC_0 = aircraft.cog_mac
weight_0 = aircraft.weight

def new_cg(original_cg, original_weight, position_list, added_weight):
    """
    Input for distances is % MAC
    """
    cg_list = np.array([original_cg])
    mass_list = np.array([original_weight])
    ctr = 0

    for x,y in zip(position_list, added_weight):
        new_position = (cg_list[ctr]*mass_list[ctr] + x*y) / (mass_list[ctr] + y)
        cg_list = np.append(cg_list, new_position)
        mass_list = np.append(mass_list, mass_list[ctr]+y)
        ctr += 1

    # Reverse Loading

    cg_list_rev = np.array([original_cg])
    mass_list_rev = np.array([original_weight])
    position_list_rev = np.flip(position_list)
    added_weight_rev = np.flip(added_weight)
    ctr = 0

    for x,y in zip(position_list_rev, added_weight_rev):
        new_position = (cg_list_rev[ctr]*mass_list_rev[ctr] + x*y) / (mass_list_rev[ctr] + y)
        cg_list_rev = np.append(cg_list_rev, new_position)
        mass_list_rev = np.append(mass_list_rev, mass_list_rev[ctr]+y)
        ctr += 1

    final_cg = cg_list[-1]
    final_mass = mass_list[-1]

    return cg_list, mass_list, cg_list_rev, mass_list_rev, final_cg, final_mass

# Cargo Loading

cargo_mass_calcfor = 3565*5.26 / (5.26+14.41) # 3565 at max ZFW or 1230 at max fuel # Confirmed
#cargo_mass_calcfor = cargo_weight_fore
cargo_mass_calcaft = 3565*14.41 / (5.26+14.41) # 3565 at max ZFW or 1230 at max fuel # Confirmed
#cargo_mass_calcaft = cargo_weight_aft
cargo_pos_list = ( np.array([11.85,29.95]) - X_LEMAC ) / MAC * 100 # Confirmed
#cargo_pos_list = ( np.array([cargo_cg_fore_upt,cargo_cg_aft_upt]) - X_LEMAC ) / MAC * 100 # Updated Confirmed

cargo_added_mass_list = np.array([cargo_mass_calcfor, cargo_mass_calcaft])

front_crg_x, front_crg_y, back_crg_x, back_crg_y, final_crg_cg, final_mass_crg = new_cg(cg_MAC_0, weight_0, cargo_pos_list, cargo_added_mass_list)

# Passenger Loading

front_row_x = 7.02 # Confirmed
#rear_row_x = 27.323 # Confirmed
rear_row_x = 24.95 # Updated value rows removed Confirmed
pass_mass = 84 # Confirmed
pass_num_per_load = 50 # Confirmed
#pass_num_per_load = 45 # Confirmed Updated

passenger_pos_list = (np.linspace(front_row_x, rear_row_x, pass_num_per_load) - X_LEMAC )/ MAC * 100
passenger_mass_list = pass_mass * np.ones_like(passenger_pos_list)

front_pass_x1, front_pass_y1, back_pass_x1, back_pass_y1, final_pass_cg1, final_pass_mass1 = new_cg(final_crg_cg, final_mass_crg, passenger_pos_list, passenger_mass_list)
front_pass_x2, front_pass_y2, back_pass_x2, back_pass_y2, final_pass_cg2, final_pass_mass2 = new_cg(final_pass_cg1, final_pass_mass1, passenger_pos_list, passenger_mass_list)

# Fuel Loading

fuel_pos_list = ( np.array([19.714]) - X_LEMAC ) / MAC * 100 # Confirmed
fuel_mass_list = np.array([6486]) # MTOW - MZFW 6486 or 8822
#fuel_mass_list = np.array([3805]) # Updated Confirmed

front_fuel_x, front_fuel_y, *_ = new_cg(final_pass_cg2, final_pass_mass2, fuel_pos_list, fuel_mass_list)

fig, ax = plt.subplots(figsize=(10, 6))

# Collect all CG values across all loading sequences
all_cg = np.concatenate([front_crg_x, back_crg_x, front_pass_x1, back_pass_x1, front_pass_x2, back_pass_x2, front_fuel_x])
cg_min = all_cg.min()
cg_max = all_cg.max()

# Max/min CG lines
ax.axvline(cg_min, color="black", linestyle=":", linewidth=1.5, label=f"CG Min: {cg_min:.1f}% MAC")
ax.axvline(cg_max, color="black", linestyle=":",  linewidth=1.5, label=f"CG Max: {cg_max:.1f}% MAC")

ax.plot(front_pass_x1, front_pass_y1, color="green", marker="s",
        markersize=2, markevery=3, linewidth=1.2)

ax.plot(front_pass_x2, front_pass_y2, color="purple", marker="s",
        markersize=2, markevery=3, linewidth=1.2)

ax.plot(back_pass_x1, back_pass_y1, color="brown", marker="s",
        markersize=2, markevery=3, linewidth=1.2)

ax.plot(back_pass_x2, back_pass_y2, color="orange", marker="s",
        markersize=2, markevery=3, linewidth=1.2)

ax.plot(front_crg_x, front_crg_y, color="blue",  marker="x")
ax.plot(back_crg_x,  back_crg_y,  color="black",  marker="x", linestyle="--")

# Ground Limits

margin = 0.02
cgg_cntr_limit = (((21.2 - ( (21.2 - 2.4) * 0.08*MTOW ) / MTOW ) * (1-margin) - X_LEMAC) / MAC) * 100
cgg_cg_limit = ((21.2 - X_LEMAC) * (1-margin) / MAC) * 100

ax.axhline(y=MTOW, color="red", linewidth=1.5, linestyle="--")
ax.text(ax.get_xlim()[1], MTOW, "MTOW", color="red",
        va="bottom", ha="right", fontsize=9)

ax.plot(front_fuel_x, front_fuel_y, color="red",  marker="x")

ax.set_xlabel("CG Position [% MAC]")
ax.set_ylabel("Mass [kg]")
ax.set_title("CG Envelope")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()

print(f"Most forward cg: {cg_min}")
print(f"Most aft cg: {cg_max}")
