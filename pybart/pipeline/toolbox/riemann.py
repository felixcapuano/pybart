import numpy as np
from pyriemann.utils.base import expm, invsqrtm, logm, sqrtm
from scipy.linalg import eigvalsh


def distance_riemann(A, B):
    """Riemannian distance between two covariance matrices A and B.
    
    .. math::
      d = {\left( \sum_i \log(\lambda_i)^2 \\right)}^{-1/2}

    where :math:`\lambda_i` are the joint eigenvalues of A and B
    :param A: First covariance matrix
    :param B: Second covariance matrix
    :returns: Riemannian distance between A and B
    """
    return np.sqrt((np.log(eigvalsh(A, B))**2).sum())

def _get_sample_weight(sample_weight, data):
    """Get the sample weights.
    If none provided, weights init to 1. otherwise, weights are normalized.
    """
    if sample_weight is None:
        sample_weight = np.ones(data.shape[0])
    if len(sample_weight) != data.shape[0]:
        raise ValueError("len of sample_weight must be equal to len of data.")
    sample_weight /= np.sum(sample_weight)
    return sample_weight

def mean_riemann(covmats, tol=10e-9, maxiter=50, init=None, sample_weight=None):
    """Return the mean covariance matrix according to the Riemannian metric.
    The procedure is similar to a gradient descent minimizing the sum of
    riemannian distance to the mean.

    .. math::
      \mathbf{C} = \\arg\min{(\sum_i \delta_R ( \mathbf{C} , \mathbf{C}_i)^2)}  # noqa

    :param covmats: Covariance matrices set, Ntrials X Nchannels X Nchannels
    :param tol: the tolerance to stop the gradient descent
    :param maxiter: The maximum number of iteration, default 50
    :param init: A covariance matrix used to initialize the gradient descent. If None the Arithmetic mean is used
    :param sample_weight: the weight of each sample
    :returns: the mean covariance matrix
    """
    # init
    sample_weight = _get_sample_weight(sample_weight, covmats)
    Nt, Ne, Ne = covmats.shape
    if init is None:
        C = np.mean(covmats, axis=0)
    else:
        C = init
    k = 0
    nu = 1.0
    tau = np.finfo(np.float64).max
    crit = np.finfo(np.float64).max
    # stop when J<10^-9 or max iteration = 50
    while (crit > tol) and (k < maxiter) and (nu > tol):
        k = k + 1
        C12 = sqrtm(C)
        Cm12 = invsqrtm(C)
        J = np.zeros((Ne, Ne))

        for index in range(Nt):
            tmp = np.dot(np.dot(Cm12, covmats[index, :, :]), Cm12)
            J += sample_weight[index] * logm(tmp)

        crit = np.linalg.norm(J, ord='fro')
        h = nu * crit
        C = np.dot(np.dot(C12, expm(nu * J)), C12)
        if h < tau:
            nu = 0.95 * nu
            tau = h
        else:
            nu = 0.5 * nu

    return C
