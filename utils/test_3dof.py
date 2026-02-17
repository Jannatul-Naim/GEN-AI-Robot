from ConstrainedIK3DOF import ConstrainedIK3DOF
from Planar3DOFArm import Planar3DOFArm

ik = ConstrainedIK3DOF()
arm_plot = Planar3DOFArm()

solutions = ik.solve_z(20, 0)

if len(solutions) > 0:
    x1, x2 = solutions[0]
    t1, t2, t3 = ik.expand_to_full_angles(x1, x2)
    arm_plot.set_angles(t1, t2, t3)