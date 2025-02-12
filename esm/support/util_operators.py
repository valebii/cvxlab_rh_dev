"""
util_functions.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module provides various utility functions that are defined to support 
complex calculations in symbolic problems and generation of constants values,
such as generating special matrices, reshaping arrays, and calculating matrix 
inverses.
"""

from typing import Optional
import numpy as np
import cvxpy as cp


def power(
        base: cp.Parameter | cp.Expression,
        exponent: cp.Parameter | cp.Expression,
) -> cp.Parameter:
    """
    Calculates the element-wise power of the base, provided an exponent. 
    Either base or exponent can be a scalar.

    Parameters:
        base (cp.Parameter | cp.Expression): The base for the power operation. 
            The corresponding value can be a scalar or a 1-D numpy array.
        exponent (cp.Parameter | cp.Expression): The exponent for the power 
            operation. The corresponding value can be a scalar or a 1-D numpy array.

    Returns:
        cp.Parameter: A new parameter with the same shape as the input parameters, 
            containing the result of the power operation.

    Raises:
        TypeError: If the base and exponent are not both instances of cvxpy 
            Parameter or Expression.
        ValueError: If the base and exponent do not have the same shape and 
            neither is a scalar. If the base and exponent are not numpy arrays.
            If the base and exponent include non-numeric values.
    """

    if not isinstance(base, cp.Parameter | cp.Expression) or \
            not isinstance(exponent, cp.Parameter | cp.Expression):
        raise TypeError(
            "Arguments of power method must be cvxpy Parameter or Expression.")

    if base.shape != exponent.shape:
        if base.is_scalar() or exponent.is_scalar():
            pass
        else:
            raise ValueError(
                "Base and exponent must have the same shape. In case of "
                "different shapes, one must be a scalar. "
                f"Shapes -> base: {base.shape}, exponent: {exponent.shape}.")

    base_val: np.ndarray = base.value
    exponent_val: np.ndarray = exponent.value

    if not isinstance(base.value, np.ndarray) or \
            not isinstance(exponent.value, np.ndarray):
        raise ValueError("Base and exponent must be numpy arrays.")

    if not (
        np.issubdtype(base.value.dtype, np.number) and
        np.issubdtype(exponent.value.dtype, np.number)
    ):
        raise ValueError("Base and exponent must be numeric.")

    power = np.power(base_val, exponent_val)
    return cp.Parameter(shape=power.shape, value=power)


def matrix_inverse(matrix: cp.Parameter | cp.Expression) -> cp.Parameter:
    """
    Calculates the inverse of a square matrix.

    Args:
        matrix (cp.Parameter | cp.Expression): The matrix to calculate the 
        inverse of.

    Returns:
        cp.Parameter: The inverse of the input matrix.

    Raises:
        TypeError: If the passed item is not a cvxpy Parameter or Expression.
        ValueError: If the passed matrix values are None, or if the passed 
            item is not a matrix, or if the passed item is not a square 
            matrix, or if the passed matrix is singular and cannot be inverted.
    """
    if not isinstance(matrix, (cp.Parameter, cp.Expression)):
        raise TypeError("Passed item must be a cvxpy Parameter or Expression.")

    matrix_val: np.ndarray = matrix.value

    if matrix_val is None:
        raise ValueError("Passed matrix values cannot be None.")

    if not isinstance(matrix_val, np.ndarray) or len(matrix_val.shape) != 2:
        raise ValueError("Passed item is not a matrix.")

    if matrix_val.shape[0] != matrix_val.shape[1]:
        raise ValueError("Passed item is not a square matrix.")

    try:
        inverse = np.linalg.inv(matrix_val)
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "Passed matrix is singular and cannot be inverted.") from exc

    return cp.Parameter(shape=matrix_val.shape, value=inverse)


def shift(
        set_length: cp.Constant,
        shift_value: cp.Parameter,
) -> cp.Parameter:
    """
    Generate a square matrix of specified dimension, with all zeros except a
    diagonal of ones that is shifted with respect to the main diagonal by a 
    specified shift_value. A positive shift_value results in a downward shift, 
    while a negative shift_value results in an upward shift. If shift_value is 0, 
    identity matrix is returned.

    Parameters:
        dimension (Tuple[int]): The dimension of the matrix row/col.
        shift_value (int): (scalar) the number of positions to shift the diagonal.

    Returns:
        np.ndarray: A square matrix with a diagonal of ones downward shifted by 
            the specified shift_value.

    Raises:
        ValueError: If passed dimension is not greater than zero.
        TypeError: If passed dimension is not an iterable containing integers.
    """
    if not isinstance(set_length, cp.Constant) or \
            not isinstance(shift_value, cp.Parameter):
        raise TypeError(
            "Passed set_length must be a cvxpy Constant, "
            "shift_value must be a cvxpy Parameter.")

    # extract values from cvxpy parameters
    set_length: np.ndarray = set_length.value
    shift_value: np.ndarray = shift_value.value

    # checks
    if set_length is None or shift_value is None:
        raise ValueError(
            "Values assigned to set_length and shift_value cannot be None.")

    if not isinstance(set_length, np.ndarray) or \
            not isinstance(shift_value, np.ndarray):
        raise TypeError(
            "Values Set length and shift value must be numpy arrays.")

    err_msg = []

    # WARNING: set_length and shift_value must be scalars
    if not set_length.size == 1:
        err_msg.append(
            "Set length must be a scalar. "
            f"Passed dimension: '{set_length.shape}'.")

    if not shift_value.size == 1:
        err_msg.append(
            "Shift value must be a scalar. "
            f"Passed dimension: '{shift_value.shape}'.")

    if err_msg:
        raise ValueError("\n".join(err_msg))

    # define shift_matrix
    sl: int = int(set_length[0, 0])
    sv: int = int(shift_value[0, 0])
    matrix = np.eye(N=sl, k=-sv)

    return cp.Parameter(shape=(sl, sl), value=matrix)


def annuity(
        period_length: cp.Parameter,
        tech_lifetime: cp.Parameter,
        interest_rate: Optional[cp.Parameter] = None,
) -> cp.Parameter:
    """ 
    Calculate the annuity factor for a given period length, lifetime, and
    interest rate. The annuity factor is used to calculate the present value of
    an annuity, which is a series of equal payments made at regular intervals.

    Parameters:
        period_length (cp.Parameter): The length of the period for which the
            annuity factor is calculated.
            lifetime (cp.Parameter): The total number of periods over which the
            annuity is paid.
            interest_rate (cp.Parameter): The interest rate used to discount the
            annuity payments.

    Returns:
        cp.Parameter: The annuity factor calculated based on the input parameters.
    """
    if not isinstance(period_length, cp.Parameter) or \
            not isinstance(tech_lifetime, cp.Parameter):
        raise TypeError(
            "Period length and lifetime must be cvxpy Parameters.")

    if interest_rate is not None and not isinstance(interest_rate, cp.Parameter):
        raise TypeError("Interest rate must be a cvxpy Parameter.")

    # extract and check values from period_length and lifetime cvxpy parameters
    pl: np.ndarray = period_length.value
    lt: np.ndarray = tech_lifetime.value

    if pl is None or lt is None:
        raise ValueError(
            "Values assigned to period_length and lifetime cannot be None.")

    if not len(pl) == 1:
        raise ValueError(
            f"Period length must be a scalar. Passed shape: '{pl.shape}'.")

    if not len(lt) == 1:
        raise ValueError(
            f"Lifetime must be a scalar. Passed dimension: '{len(lt)}'.")

    pl = pl[0][0]
    lt = lt[0][0]

    # extract and check values from interest_rate cvxpy parameter
    if interest_rate is not None:
        ir: np.ndarray = interest_rate.value
    else:
        ir: np.ndarray = np.zeros([1, pl])

    if not 1 in ir.shape:
        raise ValueError(
            f"Interest rate must be a vector. Passed dimension: '{len(ir)}'.")

    if ir.size != pl:
        raise ValueError(
            "Interest rate vector must have size equal to period length."
            f"Passed interest rate size: '{ir.size}'; period length: '{pl}'.")

    if ir.shape[0] != 1:
        ir = ir.T

    # calculate annuity matrix
    annuity = np.zeros((pl, pl))

    for row in range(pl):
        for col in range(pl):
            if col > row:
                continue
            elif (row - col) < lt:
                if ir[0, col] == 0:
                    annuity[row, col] = 1/lt
                else:
                    _ir = ir[0, col]
                    annuity[row, col] = _ir*(1 + _ir)**lt / ((1 + _ir)**lt - 1)

    return cp.Parameter(shape=(pl, pl), value=annuity)


def weibull_distribution(
        scale_factor: cp.Parameter,
        shape_factor: cp.Parameter,
        range_vector: cp.Constant,
        dimensions: int,
        rounding: int = 2,
) -> cp.Parameter:
    """
    Generates a Weibull probability density function configured either as a 
    one-dimensional vector or a two-dimensional matrix, based on specified 
    dimensions. This function primarily uses parameters from 'cvxpy' to enable 
    integration with optimization tasks and 'numpy' for handling numerical 
    operations.

    Parameters:
        scale_factor (cp.Parameter): A cvxpy Parameter object containing a 
            scalar value representing the scale parameter (λ) of the Weibull 
            distribution. This value must be positive.
        shape_factor (cp.Parameter): A cvxpy Parameter object containing a 
            scalar value representing the shape parameter (k) of the Weibull 
            distribution. Typically, this value must be positive to define the 
            distribution correctly.
        range_vector (cp.Constant): A cvxpy Constant object that includes an 
            array of values over which the Weibull PDF is computed. The range 
            should be a one-dimensional array of non-negative values.
        dimensions (int): Determines the output dimension of the Weibull PDF:
            1 for a vector output,
            2 for a matrix output where each subsequent column is a downward 
                rolled version of the Weibull PDF vector.
        rounding (int, optional): Number of decimal places to which the 
            computed Weibull PDF values are rounded. Defaults to 2.

    Returns:
        cp.Parameter: A cvxpy Parameter object that contains the Weibull PDF 
            in the specified dimension (vector or matrix). This can be 
            directly used in further cvxpy optimizations.

    Raises:
        ValueError: If any of the input parameters (scale_factor, shape_factor,
            or range_vector) is None, or if their contained values do not meet 
            the expected requirements (e.g., non-scalar for scale or shape 
            factors, or if dimensions is not 1 or 2).
    """
    if not isinstance(scale_factor, cp.Parameter) or \
            not isinstance(shape_factor, cp.Parameter) or \
            not isinstance(range_vector, cp.Constant):
        raise TypeError(
            "scale_factor and shape_factor must be cvxpy.Parameters, "
            "range_vector must be cvxpy.Constant.")

    # extract values from cvxpy parameters
    sc: np.ndarray = scale_factor.value
    sh: np.ndarray = shape_factor.value
    rx: np.ndarray = range_vector.value

    # checks
    if sc is None or sh is None or rx is None:
        raise ValueError(
            "Values assigned to scale_factor, shape_factor and range_vector "
            "cannot be None.")

    if not isinstance(sc, np.ndarray) or \
            not isinstance(sh, np.ndarray) or \
            not isinstance(rx, np.ndarray):
        raise TypeError(
            "Scale factor, shape factor, and range must be numpy arrays.")

    err_msg = []

    # WARNING: non è possibile avere sc e sh funzioni del tempo (rx)
    if not len(sc) == 1:
        err_msg.append(
            "Weibull scale factor must be a scalar. "
            f"Passed dimension: '{len(sc)}'.")

    if not len(sh) == 1:
        err_msg.append(
            "Weibull shape factor must be a scalar. "
            f"Passed dimension: '{len(sh)}'.")

    if dimensions not in [1, 2]:
        err_msg.append(
            "Output of Weibull distribution must be '1' (vector) "
            f"or 2 (matrix). Passed value: '{dimensions}'")

    if not isinstance(rounding, int) or rounding < 0:
        err_msg.append(
            "Rounding parameter must be an integer greater than or equal to zero."
        )

    if err_msg:
        raise ValueError("\n".join(err_msg))

    # defining Weibull function range
    weib_range = int(sc[0, 0]) * 2
    if weib_range <= len(rx):
        weib_range = len(rx)

    rx_weib = np.arange(1, weib_range+1).reshape((weib_range, 1))

    weib_dist = sh/sc * (rx_weib/sc)**(sh-1) * np.exp(-((rx_weib/sc)**sh))
    weib_dist = np.round(weib_dist, rounding)

    # re-scale weib_dist to get the sum equal to 1
    weib_dist /= np.sum(weib_dist)

    # reshape weib_dist to match the lenght of range
    weib_dist = weib_dist[:len(rx)]

    # generates a vector of Weibull probability distribution
    if dimensions == 1:
        weib_parameter = cp.Parameter(shape=(len(rx), 1))
        weib_parameter.value = weib_dist

    # generates a matrix of Weibull probability distribution
    # each column of the matrix is the original vector rolled down
    # WARNING: per implementare un lifetime che varia di anno in anno, bisogna
    # ricalcolare weib_dist ogni anno!
    elif dimensions == 2:
        weib_parameter = cp.Parameter(shape=(len(rx), len(rx)))
        weib_dist_matrix = np.zeros((len(rx), len(rx)))

        for i in range(len(rx)):
            weib_dist_rolled = np.roll(weib_dist, i)
            weib_dist_rolled[:i] = 0
            weib_dist_matrix[:, i] = weib_dist_rolled.flatten()

        weib_parameter.value = weib_dist_matrix

    return weib_parameter
