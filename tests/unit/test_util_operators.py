"""
test_util_functions.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module contains tests for the functions in the 'esm.support.util_functions' 
module.
"""


from math import exp
import pytest
import numpy as np

from cvxlab.support.util_operators import *


def test_power():
    # scalar base and exponent
    base = cp.Parameter(shape=(1,), value=np.array([2]))
    exponent = cp.Parameter(shape=(1,), value=np.array([3]))
    result = power(base, exponent)
    assert np.allclose(result.value, np.array([8]))

    # scalar base and vector exponent
    base = cp.Parameter(shape=(1,), value=np.array([2]))
    exponent = cp.Parameter(shape=(3,), value=np.array([1, 2, 3]))
    result = power(base, exponent)
    assert np.allclose(result.value, np.array([2, 4, 8]))

    # vector base and scalar exponent
    base = cp.Parameter(shape=(3,), value=np.array([1, 2, 3]))
    exponent = cp.Parameter(shape=(1,), value=np.array([2]))
    result = power(base, exponent)
    assert np.allclose(result.value, np.array([1, 4, 9]))

    # vector base and exponent
    base = cp.Parameter(shape=(1, 3), value=np.array([[1, 2, 3]]))
    exponent = cp.Parameter(shape=(1, 3), value=np.array([[1, 2, 3]]))
    result = power(base, exponent)
    assert np.allclose(result.value, np.array([1, 4, 27]))

    # mismatched shapes
    base = cp.Parameter(shape=(1, 3), value=np.array([[1, 2, 3]]))
    exponent = cp.Parameter(shape=(1, 2), value=np.array([[1, 2]]))
    with pytest.raises(ValueError):
        power(base, exponent)


def test_matrix_inverse():
    """
    Test the matrix_inverse function.
    This function tests the matrix_inverse function with valid and invalid 
    input, and checks if the function correctly calculates the inverse of a 
    matrix and handles invalid input.
    """

    # valid input
    matrix = cp.Parameter((2, 2), value=np.array([[4, 7], [2, 6]]))
    inverse = matrix_inverse(matrix)
    expected_inverse = np.array([[0.6, -0.7], [-0.2, 0.4]])
    assert np.allclose(inverse.value, expected_inverse)

    # invalid input
    with pytest.raises(TypeError):
        matrix_inverse('not a cvxpy Parameter or Expression')

    with pytest.raises(ValueError):
        matrix_inverse(cp.Parameter((2, 2)))

    with pytest.raises(ValueError):
        matrix_inverse(cp.Parameter((2,), value=np.array([1, 2])))

    with pytest.raises(ValueError):
        matrix_inverse(
            cp.Parameter((2, 3), value=np.array([[1, 2, 3], [4, 5, 6]])))

    with pytest.raises(ValueError):
        matrix_inverse(
            cp.Parameter((2, 2), value=np.array([[1, 2], [2, 4]])))


def test_shift():

    # invalid arguments type
    with pytest.raises(TypeError):
        shift(set_length=1, shift_values=1)

    # invalid arguments shapes
    with pytest.raises(ValueError):
        shift(
            set_length=cp.Constant(value=np.array([[2]])),
            shift_values=cp.Parameter(
                shape=((1, 2, 3)), value=np.array([[1, 2, 3]]))
        )

    # Scalar shift tests
    shift_list = [0, 1, 3, -2, -5]
    for value in shift_list:
        shift_matrix = shift(
            set_length=cp.Constant(value=np.array([[10]])),
            shift_values=cp.Parameter(shape=(1, 1), value=np.array([[value]])),
        )
        assert np.array_equal(shift_matrix.value, np.eye(10, k=-value))

    # Vector shift tests
    set_length = cp.Constant(value=np.array([[5]]))

    # Example shift vectors and expected results
    test_cases = [
        (np.array([[0, -1, 2, 0, -2]]),  # shift_values
         np.array([
             [1, 1, 0, 0, 0],  # col 0: no shift
             [0, 0, 0, 0, 0],  # col 1: shift up (-1) → appears at row 0
             [0, 0, 0, 0, 1],  # col 2: shift down (2) → appears at row 4
             [0, 0, 0, 1, 0],  # col 3: no shift
             [0, 0, 1, 0, 0],  # col 4: shift up (-2) → appears at column 2
         ])),

        (np.array([[1, 1, 1, 1, 1]]),
         np.array([
             [0, 0, 0, 0, 0],   # Main diagonal shifted down by 1
             [1, 0, 0, 0, 0],
             [0, 1, 0, 0, 0],
             [0, 0, 1, 0, 0],
             [0, 0, 0, 1, 0],
         ])),

        (np.array([[-1, -1, -1, -1, -1]]),
         np.array([
             [0, 1, 0, 0, 0],   # Main diagonal shifted up by 1
             [0, 0, 1, 0, 0],
             [0, 0, 0, 1, 0],
             [0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0],
         ])),
    ]

    for shift_values, expected_matrix in test_cases:
        shift_matrix = shift(
            set_length=set_length,
            shift_values=cp.Parameter(shape=(1, 5), value=shift_values)
        )
        assert np.array_equal(shift_matrix.value, expected_matrix), \
            f"Failed for shift_values: {shift_values}"


def test_weibull_distribution():
    """
    Test the weibull_distribution function.
    This function tests the weibull_distribution function with valid and 
    invalid input, and checks if the function correctly calculates the Weibull 
    PDF and handles invalid input.
    """

    scale_param = cp.Parameter(shape=(1, 1), value=np.array([[1.5]]))
    shape_param = cp.Parameter(shape=(1, 1), value=np.array([[2.0]]))
    range_vals = cp.Constant(value=np.array([[0, 1, 2, 3, 4, 5]]).T)

    # valid input for mono-dimensional Weibull PDF
    weib_dist = weibull_distribution(
        scale_factor=scale_param,
        shape_factor=shape_param,
        range_vector=range_vals,
        dimensions=1)
    expected_output = np.array([[0.62, 0.33, 0.05, 0., 0., 0.]]).T
    assert np.allclose(weib_dist.value, expected_output, atol=0.01)

    # valid input bi-dimensional Weibull PDF
    weib_dist = weibull_distribution(
        scale_factor=scale_param,
        shape_factor=shape_param,
        range_vector=range_vals,
        dimensions=2)
    expected_output = np.array([
        [0.62, 0., 0., 0., 0., 0.],
        [0.33, 0.62, 0., 0., 0., 0.],
        [0.05, 0.33, 0.62, 0., 0., 0.],
        [0., 0.05, 0.33, 0.62, 0., 0.],
        [0., 0., 0.05, 0.33, 0.62, 0.],
        [0., 0., 0., 0.05, 0.33, 0.62]
    ])
    assert np.allclose(weib_dist.value, expected_output, atol=0.01)

    # invalid input
    with pytest.raises(TypeError):
        weibull_distribution('not cvxpy parameter', shape_param, range_vals, 1)

    with pytest.raises(TypeError):
        weibull_distribution(scale_param, 'not cvxpy parameter', range_vals, 1)

    with pytest.raises(TypeError):
        weibull_distribution(scale_param, shape_param, 'not cvxpy constant', 1)

    with pytest.raises(ValueError):
        scale_param = cp.Parameter(shape=(1, 2), value=np.array([[1.5, 2.]]))
        weibull_distribution(scale_param, shape_param, range_vals, 1)

    with pytest.raises(ValueError):
        shape_param = cp.Parameter(shape=(1, 2), value=np.array([[2., 3.]]))
        weibull_distribution(scale_param, shape_param, range_vals, 1)

    with pytest.raises(ValueError):
        weibull_distribution(scale_param, shape_param, range_vals, 3)
