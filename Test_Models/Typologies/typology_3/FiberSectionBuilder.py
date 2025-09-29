import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import numpy as np

# secTag = int(secTag)
# sec_name = name(string)
# len_y = float(len_y) || depth
# len_z = float(len_z) || width
# cover = float(cover) || cover
# nfCore_y = int(nfCore_y) || number of fibers in the core patch in local y direction
# nfCore_z = int(nfCore_z) || number of fibers in the core patch in local z direction
# nfCover_y = int(nfCover_y) || number of fibers in the cover patches with long sides || to y
# nfCover_z = int(nfCover_z) || number of fibers in the cover patches with long sides || to z
# nBT = int(nBT) || no. of longitudinal-reinforcement bars on top layer || to z
# nBM = int(nBM) || no. of longitudinal-reinforcement bars on mid layer || to z
# nBI = int(nBI) || no. of longitudinal-reinforcement bars on mid layer || to y
# nBB = int(nBB) || no. of longitudinal-reinforcement bars on bottom layer || to z
# aBT = float(aBT) || area of top layer bars || to z
# aBM = float(aBM) || area of mid layer bars || to z
# aBI = float(aBI) || area of mid layer bars || to y
# aBB = float(aBB) || area of bottom layer bars || to z
# coreMatTag = int(coreMatTag) || material tag for concrete core
# coverMatTag = int(coverMatTag) || material tag for concrete cover
# steelMatTag = int(steelMatTag) || material tag for steel reinforcement

def Section(secTag, sec_name, len_y, len_z, cover, nfCore_y, nfCore_z, nfCover_y, nfCover_z, nBT, nBM, nBI, nBB, aBT, aBM, aBI, aBB, coreMatTag, coverMatTag, steelMatTag):

    y1 = len_y / 2.0
    z1 = len_z / 2.0
    c = cover

    # section('Fiber', secTag, '-GJ', GJ)
    # patch('rect', matTag, numSubdivY, numSubdivZ, *crdsI, *crdsJ)
    # patch('quad', matTag, numSubdivIJ, numSubdivJK, *crdsI, *crdsJ, *crdsK, *crdsL)
    # layer('straight', matTag, numFiber, areaFiber, *start, *end)

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
    opsv.fib_sec_list_to_cmds(fiber_section)
    # matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']
    # opsv.plot_fiber_section(fiber_section, matcolor=matcolor)
    # plt.title(title_of_section)
    # plt.axis('equal')
    # plt.show()
    return fiber_section