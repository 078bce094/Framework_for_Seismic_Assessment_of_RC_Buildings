from Materials import *
from FiberSectionBuilder import *

ops.wipe()
ops.model('BasicBuilder', '-ndm', 3, '-ndf', 6)

def area(diameter):
    return (np.pi * diameter ** 2) / 4.0

import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["figure.figsize"] = (10, 6)
import numpy as np

def Section(secTag, sec_name, len_y, len_z, cover, nfCore_y, nfCore_z, nfCover_y, nfCover_z, nBT, nBM, nBI, nBB, aBT, aBM, aBI, aBB, coreMatTag, coverMatTag, steelMatTag):

    y1 = len_y / 2.0
    z1 = len_z / 2.0
    c = cover

    fiber_section = [['section', 'Fiber', secTag, '-GJ', 1.0e6],
                     ['patch', 'rect', coreMatTag, nfCore_y, nfCore_z, c - y1, c - z1, y1 - c, z1 - c], # core
                     ['patch', 'quad', coverMatTag, nfCover_y, 2, *[-y1,-z1], *[y1,-z1], *[y1-c,-z1+c], *[-y1+c,-z1+c]], # right side cover
                     ['patch', 'quad', coverMatTag, nfCover_y, 2, *[-y1+c,z1-c], *[y1-c,z1-c], *[y1,z1], *[-y1,z1]],  # left side cover
                     ['patch', 'quad', coverMatTag, 2, nfCover_z, *[-y1,-z1], *[-y1+c,-z1+c], *[-y1+c,z1-c], *[-y1,z1]],  # bottom side cover
                     ['patch', 'quad', coverMatTag, 2, nfCover_z, *[y1-c,-z1+c], *[y1,-z1], *[y1,z1], *[y1-c,z1-c]]]  # top side cover
    
    if nBT > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBT, aBT, y1 - c, z1 - c, y1 - c, c - z1]) # top layer
    if nBM > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBM, aBM, 0.0, z1 - c, 0.0, c - z1]) # mid layer
    if nBI > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBI, aBI, -y1 + c, 0.0, y1 - c, 0.0]) # mid layer perpinducular to y
    if nBB > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBB, aBB, - y1 + c, z1 - c, - y1 + c, c - z1]) # bottom layer
    
    title_of_section = sec_name
    # opsv.fib_sec_list_to_cmds(fiber_section)
    matcolor = ['tab:blue', 'lightgrey', 'tab:blue', 'w', 'w', 'w']
    opsv.plot_fiber_section(fiber_section, matcolor=matcolor)
    # plt.title(title_of_section)
    # Add arrows to indicate locations of materials
    ax = plt.gca()
    # Arrow for longitudinal Steel02 rebar (top right bar)
    ax.annotate('Steel02 Rebar', xy=(-88, 87.5), xytext=(-135, 87.5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.7, headwidth=5),
                fontsize=12, color='black', ha='left', va='center')
    # Arrow for confined Concrete02 (core)
    ax.annotate('Confined Concrete02 fiber', xy=(-42, 15), xytext=(-135, 15),
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.7, headwidth=5),
                fontsize=12, color='black', ha='left', va='center')
    # Arrow for unconfined Concrete02 (cover, top edge)
    ax.annotate('Unconfined Concrete02 fiber', xy=(-104.5, 45), xytext=(-135, 45),
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.7, headwidth=5),
                fontsize=12, color='black', ha='left', va='center')
    # Remove border lines from the plot
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
    return fiber_section

# Column Type 1
Col_1_sec_name = 'Col Type 1 Section'
nBT_Col_1 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
nBM_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
nBI_Col_1 = 2       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
nBB_Col_1 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
aBT_Col_1 = area(12.0)         # area of top layer bars || to local z axis
aBM_Col_1 = area(10.0)         # area of mid layer bars || to local z axis
aBI_Col_1 = area(10.0)         # area of mid layer bars || to local y axis
aBB_Col_1 = area(12.0)         # area of bottom layer bars || to local z axis
nfCore_y_Col_1 = 6      # number of fibers in the core patch in local y axis
nfCore_z_Col_1 = 6      # number of fibers in the core patch in local z axis
nfCover_y_Col_1 = 6     # number of fibers in the cover patches with long sides || to local y axis
nfCover_z_Col_1 = 6     # number of fibers in the cover patches with long sides || to local z axis

Col_1_y = 230.0
Col_1_z = 230.0
Col_1_Cover = 27.0

Section (1, Col_1_sec_name,
            Col_1_y, Col_1_z, Col_1_Cover, 
            nfCore_y_Col_1, nfCore_z_Col_1, 
            nfCover_y_Col_1, nfCover_z_Col_1, 
            nBT_Col_1, nBM_Col_1, nBI_Col_1, nBB_Col_1,
            aBT_Col_1, aBM_Col_1, aBI_Col_1, aBB_Col_1, 
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)
