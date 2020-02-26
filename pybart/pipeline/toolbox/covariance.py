import numpy as np

def matCov(MatEpoch, ERP_Template_Target):
    All_MatCov = []
    # Concatenate each epoch with mean of targets epochs
    for i, epoch in enumerate(MatEpoch):
        # MATRICE DE COV
        MatCov = covariances_EP(epoch, ERP_Template_Target)

        # Rempli deux listes avec les matrices
        All_MatCov.append(MatCov)

    # Convert la liste en matrice
    MatCovAll = np.array(All_MatCov)
    return MatCovAll

def covariances_EP(X, P):
    """Covariances between two matrix"""
    return np.cov(np.concatenate((X, P), axis=0))