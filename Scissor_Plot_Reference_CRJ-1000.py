import numpy as np
import matplotlib.pyplot as plt
import math

c_w_root = 5.11
S = 77.4
S_net_net = S - (5.11*2.695) # 63.6 or so
Sh = 15.91
MAC = 3.28
b = 26.17  # span of wing
c_g = S / b  # mean geometric chord
A_w = b ** 2 / S
l_h = 35 - 17
VhV = 1
A_h = (8.54**2)/15.91
eta_w = 1
eta_h = 0.975
b_f = 2.695 # width of fuselage
h_f = 2.695
wing_sweep_half_chord_deg = 21.5
wing_sweep_quater_cord_deg = 25
wing_sweep_quater_cord_rad = wing_sweep_quater_cord_deg * math.pi / 180
tail_sweep_half_chord_deg = 25.8
l_fn = 17.23  # distance from nose of plane to where the leading edge of the main wing crosses the fuselage see slide 30
l_f = 36.57
l_n = -11.85  # distance from 1/4 MAC to end of Nacelle, should be negative in our case
b_n = 1.56  # nacelle width/diameter
a_cruise = 295 # speed of sound at cruise. m/s
a_ground = 343 #m/s
lamb = 0.263 #taper ratio, c_tip / c_root
xac_w = 0.35 # take from graph in slide afte getting beta
r = 1.38
m_tv = 0.308
Cm_0airfoil = -0.08
miu_1 = 0.24
miu_2 = 0.87
miu_3 =0.055
cpoc = 1.12
swfos = 0.65
CL0 = 1.25
Vt = 230.278 # cruise speed
V_app = 76.6 # approach speed
W_approach = (36968 * 9.81) # approach mass
CL_Ah_max = (W_approach/(0.5*1.225*(V_app**2)*S))
CL_landing = (W_approach/(0.5*1.225*(V_app**2)*S))
Clmax = CL_landing - (W_approach/(0.5*1.225*(Vt**2)*S))
print('delta_Clmax LOOK HERE', Clmax)
xac_wlanding = 0.325
SM = 0.05
CM_flap = -0.35
ShS1 = Sh/S

K_ea = (0.1124 + 0.1265 * wing_sweep_quater_cord_rad + 0.1766 * wing_sweep_quater_cord_rad ** 2 ) / (r ** 2) + (0.1024 / r) + 2

K_ea0 = (0.1124) / (r ** 2) + (0.1024 / r) + 2


def Cla_calc(Vt, sweep_half_chord_deg, A, eta, a):
    M = Vt / a
    beta = np.sqrt(1 - M ** 2)
    sweep_rad = math.radians(sweep_half_chord_deg)
    tan_sweep = math.tan(sweep_rad)

    num = 2 * np.pi * A
    den = 2 + math.sqrt(4 + (A * beta / eta) ** 2 * (1 + tan_sweep ** 2 / beta ** 2))
    Cla = num / den

    return Cla


def de_da(K_ea, K_ea0, r, m_tv, Vt, wing_sweep_half_chord_deg, A_w, eta, a):
    temp1 = K_ea/K_ea0
    temp2 = r / (r+m_tv)
    temp3 = 0.4876 / math.sqrt((r**2) + 0.6319 + (m_tv**2))
    temp4 = ((r**2) / ((r**2) + 0.7915 + 5.0734* (m_tv**2))) ** 0.3113
    temp5 = 1 - math.sqrt((m_tv**2)/ (1+(m_tv**2)) )
    temp6 = Cla_calc(Vt, wing_sweep_half_chord_deg, A_w, eta, a) / (math.pi * A_w)
    de_da = temp1 * (temp2 * temp3 + (1 + temp4) * temp5) * temp6
    return de_da



def Cla_Ah_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, a):
    Cla_w = Cla_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, a)
    ClaAh = (Cla_w * (S_net_net / S) * (1 + 2.15 * (b_f / b))) + ((np.pi / 2) * (b_f ** 2 / S))

    return ClaAh


def xac_f1_calc(b_f, h_f, l_fn, Vt, wing_sweep_half_chord_deg, A_w, eta_w, MAC, a):
    xac_f1 = - (1.8 * b_f * h_f * l_fn) / (Cla_Ah_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, a) * S * MAC)

    return xac_f1


def xac_f2_calc(lamb, b_f, c_g, b, wing_sweep_quater_cord_deg, MAC):
    sweep_rad = math.radians(wing_sweep_quater_cord_deg)
    tan_sweep = math.tan(sweep_rad)

    xac_f2 = (0.273 * b_f * c_g * (b - b_f) * tan_sweep) / ((1 + lamb) * (MAC ** 2) * (b + 2.15 * b_f))
    return xac_f2


def xac_wf_calc(xac_w, lamb, b_f, c_g, b, MAC, h_f, l_fn, Vt, wing_sweep_half_chord_deg, wing_sweep_quater_cord_deg,A_w, eta_w, a):
    xac_wf = (xac_w +
              xac_f1_calc(b_f, h_f, l_fn, Vt, wing_sweep_half_chord_deg, A_w, eta_w, MAC, a) +
              xac_f2_calc(lamb,b_f, c_g,b,wing_sweep_quater_cord_deg,MAC)
              )

    return xac_wf


def xac_n_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, b_n, l_n, a):
    xac_n = 2 * -2.5 * (b_n ** 2) * l_n / (S * MAC * Cla_Ah_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, a) )
    return xac_n


def xac_Ah_calc(xac_w, lamb, b_f, c_g, b, MAC, h_f, l_fn, Vt, wing_sweep_half_chord_deg,wing_sweep_quater_cord_deg, A_w,eta_w, b_n, l_n, a):

    xac_ah = xac_wf_calc(xac_w, lamb, b_f, c_g, b, MAC, h_f, l_fn, Vt, wing_sweep_half_chord_deg, wing_sweep_quater_cord_deg, A_w, eta_w, a) + xac_n_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, b_n, l_n, a)

    return xac_ah


def Cm_ac_w_calc(Cm_0airfoil, A_w, wing_sweep_quater_cord_rad):
    Cm_ac_w = Cm_0airfoil * ((A_w * (math.cos(wing_sweep_quater_cord_rad) ** 2)) / (A_w + 2 * math.cos(wing_sweep_quater_cord_rad)))
    return Cm_ac_w

def Cm_ac_fuse_calc(b_f,l_f, h_f, CL0, MAC, S, V_app, wing_sweep_half_chord_deg, A_w, eta_w, a):
    Cm_ac_fuse = -1.8 * (1 - ((2.5 * b_f)/(l_f))) * math.pi * b_f * h_f * l_f * CL0 / (4 * S * MAC * Cla_Ah_calc(V_app, wing_sweep_half_chord_deg, A_w, eta_w, a) )
    return Cm_ac_fuse

# def Cm_ac_flap_calc(miu_1, miu_2, miu_3,Clmax, cpoc, swfos, CL_landing, lamb, b_f, c_g, b, MAC, h_f, l_fn, V_app, wing_sweep_half_chord_deg, A_w,eta_w, b_n, l_n, a):
#     temp1 = -miu_1 * Clmax * cpoc
#     temp2 = (CL_landing + Clmax * (1 - swfos)) * (1/8) * cpoc * (cpoc - 1)
#     temp3 = 0.7 * ((A_w)/(1 + (2/A_w))) * miu_3 * Clmax * math.tan(wing_sweep_quater_cord_rad)
#     Cm_quater_flap = miu_2 * (temp1 - temp2) + temp3
#     Cm_ac_flap = Cm_quater_flap - CL_landing * (0.25 - xac_Ah_calc(xac_wlanding, lamb, b_f, c_g, b, MAC, h_f, l_fn, V_app, wing_sweep_half_chord_deg, wing_sweep_quater_cord_deg, A_w,eta_w, b_n, l_n, a))
#     return Cm_ac_flap

def Cm_ac_calc(Cm_0airfoil, A_w, wing_sweep_half_chord_deg, wing_sweep_quater_cord_rad,b_f,l_f, h_f, CL0, MAC, S, V_app, eta_w, miu_1, miu_2, miu_3,Clmax, cpoc, swfos, a, CL_landing, lamb, c_g, b, l_fn, b_n, l_n):
    Cm_ac = Cm_ac_w_calc(Cm_0airfoil, A_w, wing_sweep_quater_cord_rad) + Cm_ac_fuse_calc(b_f,l_f, h_f, CL0, MAC, S, V_app, wing_sweep_half_chord_deg, A_w, eta_w, a) + CM_flap
    return Cm_ac

########## Stability Parameters ##########
Cla_Ah_cruise = Cla_Ah_calc(Vt, wing_sweep_half_chord_deg, A_w, eta_w, a_cruise)
Cla_h_cruise = Cla_calc(Vt, tail_sweep_half_chord_deg, A_h, eta_h, a_cruise)
de_da = de_da(K_ea, K_ea0, r, m_tv, Vt, wing_sweep_half_chord_deg, A_w, eta_w, a_cruise)
xac_Ah_cruise = xac_Ah_calc(xac_w, lamb, b_f, c_g, b, MAC, h_f, l_fn, Vt, wing_sweep_half_chord_deg,wing_sweep_quater_cord_deg, A_w,eta_w, b_n, l_n, a_cruise)


########## Control Parameters ##########
CLa_Ah_approach = Cla_Ah_calc(V_app, wing_sweep_half_chord_deg, A_w, eta_w, a_ground)
xac_Ah_approach = xac_Ah_calc(xac_wlanding, lamb, b_f, c_g, b, MAC, h_f, l_fn, V_app, wing_sweep_half_chord_deg, wing_sweep_quater_cord_deg, A_w,eta_w, b_n, l_n, a_ground) # check that x_acw has to move
CL_Ah_max = (W_approach/(0.5*1.225*(V_app**2)*S))
CLh_max = -0.8  # check for adjustable tail
Cm_ac = Cm_ac_calc(Cm_0airfoil, A_w, wing_sweep_half_chord_deg, wing_sweep_quater_cord_rad,b_f,l_f, h_f, CL0, MAC, S, V_app, eta_w, miu_1, miu_2, miu_3,Clmax, cpoc, swfos, a_ground, CL_landing, lamb, c_g, b, l_fn, b_n, l_n)

####### CG Range #########
xcg_fwd1 = 0.309
xcg_aft1 = 0.749


###### Stability #########
gradient_stability = ((Cla_h_cruise / Cla_Ah_cruise) * (1 - de_da) * (l_h / MAC))
intercept_stability = xac_Ah_cruise - SM

###### Control #########
gradient_control = (CLh_max / CL_Ah_max) * (l_h / MAC)
intercept_control = (Cm_ac / CL_Ah_max) - xac_Ah_approach


print(f"xac_Ah_cruise:   {xac_Ah_cruise:.4f}")
print(f"xac_Ah_approach: {xac_Ah_approach:.4f}")
print(f"Cm_ac:           {Cm_ac:.4f}")
print(f"CL_Ah_max:       {CL_Ah_max:.4f}")
print(f"de_da:           {de_da:.4f}")
print(f"Cla_Ah_cruise:   {Cla_Ah_cruise:.4f}")
print(f"Cla_h_cruise:    {Cla_h_cruise:.4f}")
print(f"gradient_stab:   {gradient_stability:.4f}")
print(f"intercept_stab:  {intercept_stability:.4f}")
print(f"gradient_ctrl:   {gradient_control:.4f}")
print(f"intercept_ctrl:  {intercept_control:.4f}")
# -------------------

##### Building the lines ######
xcg_range = np.linspace(0, 1, 100)

ShS1_stability = xcg_range / gradient_stability - intercept_stability / gradient_stability
ShS1_neutral = xcg_range / gradient_stability - xac_Ah_cruise / gradient_stability

ShS1_control = xcg_range / gradient_control + intercept_control / gradient_control


###### Plotting #########

fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(xcg_range, ShS1_stability, 'b-', linewidth=2.0,
        label=f'Stability — cruise')
ax.plot(xcg_range, ShS1_control, 'r-', linewidth=2.0,
        label='Controllability — approach')
ax.plot(xcg_range, ShS1_neutral, 'b--', linewidth=1.5,
        label='Neutral stability (SM = 0)')

################ CG Range ##############
ax.axvline(xcg_fwd1, color='green', linestyle=':', linewidth=1.2, label=f'CG fwd  = {xcg_fwd1:.2f} MAC')
ax.axvline(xcg_aft1, color='green', linestyle=':', linewidth=1.2, label=f'CG aft  = {xcg_aft1:.2f} MAC')
ax.axvspan(xcg_fwd1, xcg_aft1, alpha=0.08, color='green', label='CG range')
ShS1 = np.round(ShS1, 3)
ax.axhline(y=ShS1, color='black', linestyle=':', linewidth=1.2, label=f'Current tail size = {ShS1}')


############### Plot axes and labels ############
ax.set_xlabel(r'$x_{cg}\;/\;\overline{c}$  (fraction of MAC)', fontsize=13)
ax.set_ylabel(r'$S_h\;/\;S$', fontsize=13)
ax.set_title('Scissor Plot — CRJ-1000 Reference Aircraft', fontsize=14, fontweight='bold')
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 0.5)
ax.grid(True, alpha=0.3)

ax.annotate('Controllable\nregion', xy=(0.10, 0.31), fontsize=10, color='red', alpha=0.5,
            ha='center', fontstyle='italic')
ax.annotate('Stable\nregion', xy=(0.9, 0.32), fontsize=10, color='blue', alpha=0.5,
            ha='center', fontstyle='italic')
ax.annotate('',
            xy=(xcg_fwd1, ShS1),      # The start point in data coordinates
            xytext=(xcg_aft1, ShS1),  # The end point in data coordinates
            arrowprops=dict(arrowstyle='<|-|>',
                            color='black',
                            lw=1.2),
            annotation_clip=False)
ax.plot([], [], color='black', linestyle='-', marker='|', label='CG Range')

plt.tight_layout()
plt.show()
