import numpy as np

# Groups

class Component:

    def __init__(self, name, weight_pct_eow, x_cg):
        """
        Args:
            name          : Component name
            weight_pct_eow: Weight as % of EOW
            x_cg          : CG position from nose
        """
        self.name = name
        self.weight_pct_eow = weight_pct_eow
        self.x_cg = x_cg  # global reference

    def cg_lemac(self, x_lemac, mac):
        return (self.x_cg - x_lemac) / mac * 100 #Returns CG as % MAC measured from LEMAC

    def __repr__(self):
        return f"Component('{self.name}', {self.weight_pct_eow}% EOW, x={self.x_cg}m)"


class ComponentGroup:

    def __init__(self, name, OEW):
        self.name = name
        self.components = []
        self.OEW = OEW

    def add(self, component):
        self.components.append(component)
        return self

    # weight
    @property
    def total_weight(self):
        return sum(c.weight_pct_eow for c in self.components) * self.OEW / 100

    # CG global
    @property
    def x_cg(self):
        return (
            sum(c.weight_pct_eow * (OEW/100) * c.x_cg for c in self.components)
            / (self.total_weight)
        )

    # CG LEMAC
    @property
    def cg_lemac(self, x_lemac, mac):
        return (self.x_cg - x_lemac) / mac * 100 #Group CG as % MAC measured from LEMAC

    def __repr__(self):
        return (
            f"ComponentGroup('{self.name}', "
            f"{self.total_weight:.1f}% EOW)"
        )

class Aircraft:
    def __init__(self, OEW):
        self.component_groups = []
        self.component_groups_cg = []
        self.OEW = OEW

    def add(self, component_group, component_group_cg):
        self.component_groups.append(component_group)
        self.component_groups_cg.append(component_group_cg)
        return self

    @property
    def cog(self):
        return (
            sum(g.total_weight * cg for g, cg in zip(self.component_groups, self.component_groups_cg))
            / sum(g.total_weight for g in self.component_groups)
        )

    @property
    def cog_mac(self):
        return (self.cog - X_LEMAC) / MAC * 100

    @property
    def weight(self):
        return sum(g.total_weight for g in self.component_groups) + 0.188*OEW # Account for MISC

#  AIRCRAFT PARAMETERS

X_LEMAC = 19.209   # m from nose CONFIRMED
MAC     = 3.480   # m CONFIRMED
OEW = 23_188  # kg CONFIRMED
MTOW = 41640 # kg CONFIRMED

# Design Modifications

updated_wing = 19.7 * 0.91 # Still uses old OEW to be compatible # Confirmed
updated_fuselage = 35 * 0.93 # Still uses old OEW to be compatible # Confirmed
battery_weight_fore_perOEW = 100 * 2025 / OEW # Confirmed
battery_weight_aft_perOEW = 100 * 2475 / OEW # Confirmed
bat_cg_fore_upt = 9.89 + 0.5 * ((1.3/5.26) * (12.73 + 1.07-9.89)) # Confirmed
bat_cg_aft_upt = 27.86 + 4.17 - 0.5 * ((1.6/14.41) * (4.17)) # Confirmed
 
cargo_weight_fore = 3566 * (5.26-1.3) / (5.26-1.3 + 14.41 - 1.6) # Confirmed
cargo_weight_aft = 3566 * (14.41-1.6) / (5.26-1.3 + 14.41 - 1.6) # Confirmed
cargo_cg_fore_upt = (9.89 + ((1.3/5.26) * (12.73 + 1.07-9.89)) + (12.73+1.07)) / 2 # Confirmed
cargo_cg_aft_upt = ( 27.86 + (27.86+4.17 - (1.6/14.41) * (4.17)) ) / 2 # Confirmed

updated_fuel_mass = MTOW - 26709 - 90 * 84 - 3566 # Confirmed

wing_shift = 1

# Wing Group
wing_group = ComponentGroup("Wing Group", OEW) # Confirmed
wing_group.add(Component("Wing", 19.7, 20.89)) # Confirmed
#wing_group.add(Component("Wing (Updated)", updated_wing, wing_shift*20.89)) # Confirmed
wing_group.add(Component("Main Landing Gear", 5.8, 21.2)) # Confirmed

# Fuselage Group
fuselage_group = ComponentGroup("Fuselage Group", OEW) # Confirmed
fuselage_group.add(Component("Fuselage", 35.0, 17.188)) # Confirmed
#fuselage_group.add(Component("Fuselage (Updated)", updated_fuselage, 17.1879)) # Confirmed
fuselage_group.add(Component("Nose Landing Gear", 0.8, 2.4)) # Confirmed
fuselage_group.add(Component("Cockpit Systems", 2.3, 2.97)) # Confirmed
fuselage_group.add(Component("Propulsion System (incl. Nacelles)", 13.3, 30.16)) # Confirmed
fuselage_group.add(Component("Horizontal Tail", 2.5, 37.36)) # Confirmed
fuselage_group.add(Component("Vertical Tail", 1.8, 34.80)) # Confirmed
#fuselage_group.add(Component("Battery (Fore)", battery_weight_fore_perOEW, 11.85)) 
#fuselage_group.add(Component("Battery (Aft)", battery_weight_aft_perOEW, 29.95))

# Aircraft

aircraft = Aircraft(OEW)
aircraft.add(fuselage_group, fuselage_group.x_cg)
aircraft.add(wing_group, wing_group.x_cg)

#  EMPTY OPERATIVE CONFIGURATION (full aircraft)

if __name__ == "__main__":
    print(f"Aircraft CG from Nose: {aircraft.cog:.21f} [m]")
    print(f"Aircraft CG from X_LEMAC: {aircraft.cog_mac:.2f} [% MAC]")
    print(f"Aircraft Total Weight {aircraft.weight:.1f} [kg]")
    print(wing_group.x_cg, fuselage_group.x_cg)

    # Design Modifications

    print(f"Updated Wing Weight: {updated_wing * OEW / 100}")
    print(f"Updated Fuselage Weight: {updated_fuselage * OEW / 100}")
    print(f"New Cargo Fore Weight: {cargo_weight_fore}")
    print(f"New Cargo Aft Weight: {cargo_weight_aft}")
    print(f"New Fuel Mass: {updated_fuel_mass}")
    print(f"New Cargo Fore CG: {cargo_cg_fore_upt}")
    print(f"New Cargo Aft CG: {cargo_cg_aft_upt}")
    print(f"New Batt Fore CG: {bat_cg_fore_upt}")
    print(f"New Batt Aft CG: {bat_cg_aft_upt}")
