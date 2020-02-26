import numpy as np
from .riemann import distance_riemann

def compute_rTNT(MatCov_Trial, mean_MatCov_Target, mean_MatCov_NoTarget):
    All_rTNT = []
    for i, epoch in enumerate(MatCov_Trial):
        dT = distance_riemann(epoch, mean_MatCov_Target)
        dNT = distance_riemann(epoch, mean_MatCov_NoTarget)
        All_rTNT.append(np.log(dT/dNT))

    All_rTNT = np.array(All_rTNT)

    # MOYENNES des rTNT
    Mu_rTNT = np.mean(All_rTNT)

    # Variance des rTNT
    Var_rTNT = np.var(All_rTNT)

    return Mu_rTNT, Var_rTNT, All_rTNT
