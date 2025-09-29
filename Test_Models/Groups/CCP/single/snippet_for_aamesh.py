"""
The struts are modeled using truss element available in OpenSees Library. For its in-plane force-displacement envelope, the model proposed by Panagiotakos and Fardis [31] (Fig 7) has been adopted and implemented using uniaxial Hysteretic material available in OpenSees library. The constitutive law consists of four stages, a) initial elastic region of un-cracked infill, b) post linear elastic behaviour, specified by uncoupling of the frame and infill leading to decrease in stiffness, c) softening behaviour followed by maximum force, and d) attainment of constant axial residual strength starting at δu. To obtain the points in compression zone, the following governing equations are used,
 R1= Gm*tm*lmhm          R2= Em*tm*bmdm           R3= 0.5-10% of R1
Fy = fms*tm*lm	Fm =1.3*Fy	Fu = 5-10% of Fm
δy= FyR1	δm = δy + Fm*FyR2		δu=δm+ Fm*FuR3
where Gm, Em and fms are shear modulus, Young's modulus and failure stress of masonry infill as evaluated from diagonal compression test. While tm, lm, hm and dm are thickness, length, height and diagonal length of masonry infill respectively. The dimensions of equivalent strut is computed as per FEMA [33], according to which thickness of the strut is same as that of infill and width (bm) is given by,
​​bm = 0.175*(1*hcol)-0.4*rinf	1=[Eme*tinf*sin24Efe*Icol*hinf]0.25 
where hcol = center to center height of column between beams, hinf = hm, Efe = modulus of elasticity of frame material, Eme = Em, Icol = Moment of inertia of column perpendicular to the infill plane, Linf = lm, rinf = dm, tinf = tm and θ = tan-1(hm/lm) radians.
The values of Gm, Em, fms, R3 and Fu are adopted from Uprety and Suwal [2] as 1.171 GPa, 2300 MPa, 0.575 MPa, 10% of R1 and 10% of Fm respectively. For points in the tension zone, 1% value of corresponding point in compression is adopted, this helps in obtaining converging outputs with negligible response in tension [2]. The values of Hysteretic material pinchx, pinchy and beta were acquired from the calibrated model parameters of Noh et al. [32]. The other parameters include force and deformation values obtained from above Eqns. The effective thickness of infills has been adopted as 100mm. 
"""

"""
This infill is a replicated version of Rupesh Dai Paper.
I am sharing you the snippets form different py files, do define the parameters in your own way, I believe this code will act as good reference for you guys (I did it from scratch, hope you guys wouldn't have to)
"""

# source /Users/niraj/x86_env/bin/activate 
import numpy as np
import openseespy.opensees as ops
import matplotlib.pyplot as plt

fc = -15.0
Ec = 5000 * (-fc)**0.5  # Concrete Elastic Modulus (the term in sqr root in Mpa)

bay_width_X = 4500. 
bay_width_Y = 2600.  # bay width Y >= bay width X
bay_width_Z = 3200.

Beam_1_y = 325.0
Beam_1_z = 230.0
Beam_1_Cover = 30.0

Col_1_y = 230.0
Col_1_z = 230.0
Col_1_Cover = 23.0

# -----------------------------------------------------------------------

hys_Mat_tag_Y = 5

def calculate_strut_width(hys_Mat_tag, dim_perp, dim_along, bayWidth_along):
    h_col = bay_width_Z - Beam_1_y
    h_inf = bay_width_Z - Beam_1_y
    E_fe = Ec
    E_me = 2300.0 # Mpa Modulus of elasticity of masonary
    I_col = dim_perp * (dim_along ** 3) / 12
    L_inf = bayWidth_along - dim_along
    t_inf = 100.0 # mm thickness of masonary wall

    r_inf = np.sqrt(h_inf**2 + L_inf**2)     # diagonal length of infill panel
    theta = np.atan(h_inf / L_inf)           # angle θ whose tangent is the height-to-length aspect ratio
    lambda_1 = ((E_me * t_inf * np.sin(2 * theta)) / (4 * E_fe * I_col * h_inf))**(1/4)
    bm = 0.175 * (lambda_1 * h_col)**(-0.4) * r_inf   # width of the equivalent strut
    
    Em = 2300.0    # MPa
    Gm = 1.171e3   # MPa 
    fms = 0.575    # MPa

    tm = t_inf
    lm = L_inf
    hm = h_inf
    dm = r_inf

    R1 = Gm * tm * lm / hm
    R2 = Em * tm * bm / dm
    R3 = 0.1 * R1

    Fy = fms * tm * lm 
    Fm = 1.3 * Fy
    Fr = 0.1 * Fm

    del_y = Fy / R1
    del_m = del_y + (Fm - Fy) / R2
    del_u = del_m + (Fm - Fr) / R3
    
    strut_area = t_inf * bm
    strut_length = ((bayWidth_along ** 2) + (bay_width_Z ** 2)) ** (1/2)

    cFy, cFu, cFr = -Fy / strut_area, -Fm / strut_area, - Fr / strut_area
    cdeltay, cdeltau, cdeltar = -del_y / strut_length, -del_m / strut_length, -del_u / strut_length
    tFy, tFu, tFr = -0.01 * cFy, -0.01 * cFu, -0.01 * cFr
    tdeltay, tdeltau, tdeltar = -0.01 * cdeltay, -0.01 * cdeltau, -0.01 * cdeltar

    pinchx, pinchy, beta = 0.9, 0.1, 0.1

    ops.uniaxialMaterial("Hysteretic", hys_Mat_tag, *[tFy, tdeltay], *[tFu, tdeltau], *[tFr, tdeltar], *[cFy, cdeltay], *[cFu, cdeltau], *[cFr, cdeltar], pinchx, pinchy, 0.0, 0.0, beta)
    
    return tdeltar, cdeltar, strut_area
  
tdeltarY, cdeltarY, strut_areaY = calculate_strut_width(hys_Mat_tag_Y, Col_1_z, Col_1_y, bay_width_Y)    

# -----------------------------------------------------------------------

hys_Mat_tag = [hys_Mat_tag_Y]

for Mat_tag in hys_Mat_tag:
    ops.testUniaxialMaterial(Mat_tag)

    # Define strain history
    strain_values_hys = np.concatenate([
    np.linspace(0, tdeltarY * 1.2, 100),
    np.linspace(0, cdeltarY * 1.2, 100)])

    stress_hys = []
    strain_hys = []

    # Obtain stress values for each strain value
    for eps in strain_values_hys:
        ops.setStrain(eps)
        stress = ops.getStress()
        strain = ops.getStrain()
        stress_hys.append(stress)
        strain_hys.append(strain)

    # Plotting
    plt.figure()
    plt.plot(strain_hys, stress_hys)
    plt.title('Hysteretic Material Stress-Strain Curve')
    plt.xlabel('Strain')    
    plt.ylabel('Stress')
    plt.axhline(0, color='red', linewidth=0.8)  # horizontal axis
    plt.axvline(0, color='red', linewidth=0.8)  # vertical axis
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------

def infill_along_Y():
    for i in range(NplaneX):
        startX = i + 1
        endX = i + 1

        if startX not in (1, NplaneX):
            startZ = 1
            endZ = startZ + 1
            for j in range(NplaneY - 1):
                startY = j + 1
                endY = startY + 1

                startNode1 = startX * 100 + startY * 10 + startZ
                endNode1 = endX * 100 + endY * 10 + endZ
                strutTag1 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ

                startNode2 = startX * 100 + startY * 10 + endZ
                endNode2 = endX * 100 + endY * 10 + startZ
                strutTag2 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + endZ * 10 + startZ

                ops.element('Truss', strutTag1, *[startNode1, endNode1], strut_areaY, hys_Mat_tag_Y)
                ops.element('Truss', strutTag2, *[startNode2, endNode2], strut_areaY, hys_Mat_tag_Y)

        # if startX in (1, NplaneX):
        for k in range(1, NplaneZ - 1):
            startZ = k + 1
            endZ = startZ + 1
            for j in range(NplaneY - 1):
                startY = j + 1
                endY = startY + 1

                startNode1 = startX * 100 + startY * 10 + startZ
                endNode1 = endX * 100 + endY * 10 + endZ
                strutTag1 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ

                startNode2 = startX * 100 + startY * 10 + endZ
                endNode2 = endX * 100 + endY * 10 + startZ
                strutTag2 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + endZ * 10 + startZ

                ops.element('Truss', strutTag1, *[startNode1, endNode1], strut_areaY, hys_Mat_tag_Y)
                ops.element('Truss', strutTag2, *[startNode2, endNode2], strut_areaY, hys_Mat_tag_Y)

# if infillIncusion == 0:
#     print('NO infills applied...')
# elif infillIncusion == 2:
#     print('Infills applied along Y Direction...')
#     infill_along_Y()  # if time history is done in Y direction
# else:
#     print('ERROR infill Direction...')