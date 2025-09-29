# source /Users/niraj/x86_env/bin/activate

from model_with_element_mass_infill import *

# --------------------------------------------------------------------------------
# Gravity Analysis 
# --------------------------------------------------------------------------------
if rigidDiaphragm == 1:
    ops.constraints('Transformation')
else:
    ops.constraints('Plain')

ops.numberer('RCM')
ops.system('BandGen')
ops.test('NormDispIncr', 1e-8, 10)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.001)
ops.analysis('Static')

ops.analyze(1)

ops.loadConst('-time', 0.0)  # Set the time to zero an hold the loads constant

# --------------------------------------------------------------------------------
# Plotting Mode Shapes and Deformed Shape
# --------------------------------------------------------------------------------
def ModeShapesPlot():
    opsv.plot_defo()
    plt.title("Deformed Shape")

    opsv.plot_mode_shape(1)
    plt.title("Mode 1")

    opsv.plot_mode_shape(2)
    plt.title("Mode 2")

    opsv.plot_mode_shape(3)
    plt.title("Mode 3")

    opsv.plot_mode_shape(4)
    plt.title("Mode 4")

    opsv.plot_mode_shape(5)
    plt.title("Mode 5")

    plt.show()

# ModeShapesPlot()