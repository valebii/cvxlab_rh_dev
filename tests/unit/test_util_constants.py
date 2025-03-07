"""
test_util_functions.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module contains tests for the functions in the 'esm.support.util_functions' 
module.
"""


import pytest
import pandas as pd
import numpy as np

from cvxlab.support.util_constants import *


def test_tril():
    """
    Test the tril function.
    This function tests the tril function with valid and invalid input, and 
    checks if the function correctly generates a lower triangular matrix with 
    ones and handles invalid input.
    """

    # valid input
    matrix = tril((3, 1))
    expected_matrix = np.array([
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 1]
    ])
    assert np.array_equal(matrix, expected_matrix)

    # valid input
    matrix = tril((1, 1))
    expected_matrix = np.array([[1.]])
    assert np.array_equal(matrix, expected_matrix)

    # invalid input
    with pytest.raises(TypeError):
        tril('not an integer')

    with pytest.raises(TypeError):
        tril(-1)

    with pytest.raises(ValueError):
        tril((-10, 1))


def test_identity_rcot():
    """
    Test the identity_rcot function.
    This function tests the identity_rcot function with valid and invalid 
    input, and checks if the function correctly generates a special identity 
    matrix and handles invalid input.
    """

    # valid input
    df = pd.DataFrame({
        'rows': ['a', 'b', 'c'],
        'cols': ['x', 'y', 'z']
    })
    rows_order = ['a', 'b', 'c']
    cols_order = ['x', 'y', 'z']
    matrix = identity_rcot(df, rows_order, cols_order)
    expected_matrix = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])
    assert np.array_equal(matrix, expected_matrix)

    # valid input with reordered rows and columns
    df = pd.DataFrame({
        'rows': ['a', 'b', 'b', 'c', 'c'],
        'cols': ['x', 'y1', 'y2', 'z1', 'z2']
    })
    rows_order = ['c', 'a', 'b']
    cols_order = ['z2', 'z1', 'y2', 'y1', 'x']
    matrix = identity_rcot(df, rows_order, cols_order)
    expected_matrix = np.array([
        [1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0]
    ])
    assert np.array_equal(matrix, expected_matrix)

    # valid input with all rows having the same value
    df = pd.DataFrame({
        'rows': ['a', 'a', 'a'],
        'cols': ['x1', 'x2', 'x3']
    })
    rows_order = ['a']
    cols_order = ['x1', 'x2', 'x3']
    matrix = identity_rcot(df, rows_order, cols_order)
    expected_matrix = np.array([[1, 1, 1]])
    assert np.array_equal(matrix, expected_matrix)

    # invalid input: not a dataframe
    with pytest.raises(ValueError):
        identity_rcot('not a dataframe', [], [])

    # invalid input: missing 'rows' and 'cols' columns
    with pytest.raises(ValueError):
        df = pd.DataFrame({
            'not_rows': ['a', 'b', 'c'],
            'not_cols': ['x', 'y', 'z']
        })
        identity_rcot(df, [], [])

    # invalid input: rows_order not fully represented
    with pytest.raises(ValueError):
        df = pd.DataFrame({
            'rows': ['a', 'b'],
            'cols': ['x', 'y']
        })
        rows_order = ['a', 'b', 'c']  # 'c' is not in 'rows'
        cols_order = ['x', 'y']
        identity_rcot(df, rows_order, cols_order)

    # invalid input: cols_order not fully represented
    with pytest.raises(ValueError):
        df = pd.DataFrame({
            'rows': ['a', 'b'],
            'cols': ['x', 'y']
        })
        rows_order = ['a', 'b']
        cols_order = ['x', 'y', 'z']  # 'z' is not in 'cols'
        identity_rcot(df, rows_order, cols_order)


def test_arange():
    """
    Test the arange function.
    This function tests the 'arange' function with valid and invalid input, 
    and checks if the function correctly generates a reshaped array and 
    handles invalid input.
    """

    # valid input
    array = arange((2, 3), 1, 'F')
    expected_array = np.array([
        [1, 3, 5],
        [2, 4, 6]
    ])
    assert np.array_equal(array, expected_array)

    # valid input
    array = arange((2, 3), 1, 'C')
    expected_array = np.array([
        [1, 2, 3],
        [4, 5, 6]
    ])
    assert np.array_equal(array, expected_array)

    # valid input
    expected_array = np.array([[1, 2, 3]])
    array1 = arange((1, 3), 1, 'C')
    assert np.array_equal(array1, expected_array)
    array2 = arange((1, 3), 1, 'F')
    assert np.array_equal(array2, expected_array)

    # invalid input
    with pytest.raises(ValueError):
        arange('not an iterable', 1, 'F')

    with pytest.raises(ValueError):
        arange((2, 3), 'not an integer', 'F')

    with pytest.raises(ValueError):
        arange((2, 3), 1, 'not C or F')
