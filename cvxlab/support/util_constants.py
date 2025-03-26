"""
util_functions.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module provides various utility functions that are defined to support 
complex calculations in symbolic problems and generation of constants values,
such as generating special matrices, reshaping arrays, and calculating matrix 
inverses.
"""

from typing import Iterable, Tuple
import numpy as np
import pandas as pd


def tril(dimension: Tuple[int]) -> np.array:
    """
    Generate a square matrix with ones in the lower triangular region
    (including the diagonal) and zeros elsewhere.

    Parameters:
        dimension (Tuple[int]): The dimension of the matrix row/col.

    Returns:
        np.ndarray: A square matrix with ones in the lower triangular region 
            and zeros elsewhere.

    Raises:
        ValueError: If passed dimension is not greater than zero.
        TypeError: If passed dimension is not an iterable containing integers.
    """
    if not isinstance(dimension, Tuple) and not \
            all(isinstance(i, int) for i in dimension):
        raise TypeError(
            "Passed dimension must be a tuple containing integers.")

    if any(i < 0 for i in dimension):
        raise ValueError(
            "Passed dimension must be integers greater than zero.")

    if len(dimension) != 2 or not any(i == 1 for i in dimension):
        raise ValueError(
            "Passed dimension must have at least one element equal to 1 (it "
            "must represent a vector.")

    size = max(dimension)
    matrix = np.tril(np.ones((size, size)))
    np.fill_diagonal(matrix, 1)

    return matrix


def identity_rcot(
        related_dims_map: pd.DataFrame,
        rows_order: list[str],
        cols_order: list[str],
) -> np.ndarray:
    """
    Generate a special identity matrix from a map of columns and rows items 
    provided by a 'related_dims_map' dataframe. 

    Parameters:
        related_dims_map: pandas DataFrame containing rows and corresponding
            columns items.

    Returns:
        numpy ndarray containing the special identity matrix.

    Raises:
        ValueError: If 'related_dims_map' is not a DataFrame or if it does not 
            contain 'rows' and 'cols' columns.
    """
    if not isinstance(related_dims_map, pd.DataFrame):
        raise ValueError("'related_dims_map' must be a pandas DataFrame.")

    if not {'rows', 'cols'}.issubset(related_dims_map.columns):
        raise ValueError(
            "'related_dims_map' must contain 'rows' and 'cols' columns labels.")

    error_list = []
    if not set(rows_order).issubset(related_dims_map['rows']):
        error_list.append("'rows_order' do not match 'related_dims_map.rows'.")
    if not set(cols_order).issubset(related_dims_map['cols']):
        error_list.append("'cols_order' do not match 'related_dims_map.cols'.")
    if error_list:
        raise ValueError("\n".join(error_list))

    related_dims_map['value'] = 1

    pivot_df = related_dims_map.pivot_table(
        index='rows',
        columns='cols',
        values='value',
        aggfunc='sum'
    ).fillna(0).astype(int)

    pivot_df_reordered = pivot_df.reindex(
        index=rows_order,
        columns=cols_order,
        fill_value=0
    )

    return pivot_df_reordered.values


def arange(
        shape_size: Iterable[int],
        start_from: int = 1,
        order: str = 'F',
) -> np.ndarray:
    """
    Generate a reshaped array with values ranging from 'start_from' to 
    'start_from + total_elements'.

    Parameters:
        shape_size (Iterable[int]): The shape of the output array.
        start_from (int, optional): The starting value for the range. 
            Defaults to 1.
        order (str, optional): The order of the reshaped array. 
            Defaults to 'F'.

    Returns:
        np.ndarray: The reshaped array with values ranging from 'start_from' 
            to 'start_from + total_elements'.

    Raises:
        ValueError: If 'shape_size' is not an iterable of integers, 
            'start_from' is not an integer, or 'order' is not a string.
        ValueError: If 'order' is not 'C' or 'F'.
    """
    if not isinstance(shape_size, Iterable) or \
            not all(isinstance(i, int) for i in shape_size):
        raise ValueError("'shape_size' must be an iterable of integers.")

    if not isinstance(start_from, int):
        raise ValueError("'start_from' must be an integer.")

    if not isinstance(order, str):
        raise ValueError("'order' must be a string.")

    if order not in ['C', 'F']:
        raise ValueError("'order' must be either 'C' or 'F'.")

    total_elements = np.prod(shape_size)
    values = np.arange(start_from, start_from+total_elements)
    reshaped_array = np.reshape(a=values, newshape=shape_size, order=order)

    return reshaped_array
