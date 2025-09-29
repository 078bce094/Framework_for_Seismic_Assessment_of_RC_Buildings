# source /Users/niraj/x86_env/bin/activate 
import openseespy.opensees as ops

def MomentCurvature3D(secTag, axialLoad, DimBA, Cover, mu, numIncr, bendingAxis):
    # Estimate yield curvature (Assuming no axial load and only top and bottom steel)
    epsy = Fy_steel / E0_steel   # Steel yield strain
    eff_d = DimBA - Cover   # d -- from top cover to lower rebar center in tension
    Kaxis = epsy/(0.7 * eff_d)    # Approximate yield curvature (when only steel yields)

    maxK = Kaxis * mu  # Maximum curvature for analysis
    
    # Define two nodes at (0,0,0)
    ops.node(1, 0.0, 0.0, 0.0)
    ops.node(2, 0.0, 0.0, 0.0)

    if bendingAxis == 'z':
        # Bending about local y-axis (curvature about z-axis, rotation DOF 6)
        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ops.fix(2, 0, 1, 1, 1, 1, 0)
    elif bendingAxis == 'y':
        # Bending about local z-axis (curvature about y-axis, rotation DOF 5)
        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ops.fix(2, 0, 1, 1, 1, 0, 1)
    else:
        raise ValueError("Invalid bendingAxis. Choose 'y' or 'z'.")

    # element('zeroLengthSection', eleTag, *eleNodes, secTag, <'-orient', *vecx, *vecyp>, <'-doRayleigh', rFlag>)
    ops.element('zeroLengthSection', 1, 1, 2, secTag) # zeroLengthSection element

    # Define constant axial load only at node 2
    ops.timeSeries('Constant', 100)
    ops.pattern('Plain', 100, 100)
    ops.load(2, axialLoad, 0.0, 0.0, 0.0, 0.0, 0.0)

    # Define analysis parameters
    # integrator('LoadControl', incr, numIter=1, minIncr=incr, maxIncr=incr)

    ops.integrator('LoadControl', 0, 1, 0, 0)
    ops.system('SparseGeneral', '-piv')
    ops.test('EnergyIncr', 1e-9, 10)
    ops.numberer('Plain')
    ops.constraints('Plain')
    ops.algorithm('Newton')
    ops.analysis('Static')

    # Apply the constant axial load only and reset time to zero
    ops.analyze(1)
    ops.loadConst('-time', 0.0)

    # Define reference moment based on the bending axis
    ops.timeSeries('Linear', 101)
    ops.pattern('Plain',101, 101)

    if bendingAxis == 'z':
        disp_dof = 6 
    elif bendingAxis == 'y':
        disp_dof = 5
        
    if bendingAxis == 'z':
        ops.load(2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)  # Moment about z-axis
    elif bendingAxis == 'y':
        ops.load(2, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)  # Moment about y-axis

    dK = maxK / numIncr
    # integrator('DisplacementControl', nodeTag, dof, incr, numIter=1, dUmin=incr, dUmax=incr)
    ops.integrator('DisplacementControl', 2, disp_dof, dK, 1, dK, dK)

    # Section analysis one step at a time to record results
    moments = []
    curvatures = []

    for i in range(numIncr):
        ops.analyze(1)
        curvature = ops.nodeDisp(2, disp_dof)
        moment = ops.getLoadFactor(101)  # Load factor multiplied by unit moment
        curvatures.append(curvature)
        moments.append(moment)

    # Estimate yield curvature and yield moment
    yield_curvature = None
    yield_moment = None
    for c, m in zip(curvatures, moments):
        if c >= (Kaxis):
            yield_curvature = c
            yield_moment = m
            break

    # Ultimate moment and curvature (maximum moment value)
    ultimate_moment = max(moments)
    ultimate_index = moments.index(ultimate_moment)
    ultimate_curvature = curvatures[ultimate_index]

    return abs(yield_curvature), abs(ultimate_curvature), abs(yield_moment), abs(ultimate_moment)

from model_with_element_mass_infill import *