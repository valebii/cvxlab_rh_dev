"""
util.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module contains a collection of utility functions designed to assist with 
managing and manipulating data within the context of model generation and 
operation in the package. These functions include file management, data 
validation, dataframe manipulation, dictionary operations, and specific support 
functions that enhance the interoperability of data structures used throughout 
the application.

These utilities are critical in handling the data integrity and consistency 
required for successful model operation, providing robust tools for data 
manipulation and validation.
"""

import itertools as it
import numpy as np
import pandas as pd

from collections.abc import Iterable
from copy import deepcopy
from typing import Dict, List, Any, Literal, Optional, Tuple

from cvxlab.support import util_text


def validate_selection(
        valid_selections: Iterable[str],
        selection: str,
        ignore_case: bool = False,
) -> None:
    """
    Validates if a provided selection is within a list of valid selections.

    Args:
        valid_selections (List[str]): A list containing all valid selections.
        selection (str): The selection to validate.
        ignore_case (bool): If True, ignores the case of the selection. 
            Works only with string selections. Default is False.

    Returns:
        None: This function only performs validation and does not return any value.

    Raises:
        ValueError: If the selection is not found within the list of valid selections.
        ValueError: If no valid selections are available.
        ValueError: If ignore_case is True but the selections are not strings.
    """
    if not valid_selections:
        raise ValueError("No valid selections are available.")

    if ignore_case:
        if all(isinstance(item, str) for item in valid_selections):
            valid_selections = [item.lower() for item in valid_selections]
            selection = selection.lower()
        else:
            raise ValueError(
                "Ignore case option is only available for string selections.")

    if selection not in valid_selections:
        raise ValueError(
            "Invalid selection. Please choose one "
            f"of: {', '.join(valid_selections)}.")


def items_in_list(
        items: List,
        control_list: Iterable,
) -> bool:
    """
    Checks if all items in a list are present in a control list.

    Args:
        items (List): The list of items to check.
        control_list (Iterable): The iterable to check against.

    Returns:
        bool: True if all items are present in the list to check, False otherwise.

    Raises:
        TypeError: If either 'items' or 'list_to_check' is not iterable.
        ValueError: If 'list_to_check' is empty.
    """
    if not isinstance(items, list):
        raise TypeError(
            "'items' must be of type list. Passed "
            f"type: {type(items).__name__}; "
        )
    if not isinstance(control_list, Iterable):
        raise TypeError(
            "'list_to_check' must be iterable. Passed "
            f"type: {type(control_list).__name__}; "
        )

    control_set = set(control_list)
    if not control_set:
        raise ValueError("The control_list must not be empty.")

    if not items:
        return False

    return all(item in control_list for item in items)


def get_user_confirmation(message: str) -> bool:
    """
    Prompts the user to confirm an action via command line input.

    Args:
        message (str): The message to display to the user.

    Returns:
        bool: True if the user confirms the action, False otherwise.
    """
    response = input(f"{message} (y/[n]): ").lower()
    return response == 'y'


def find_dict_depth(item: dict) -> int:
    """
    Determines the depth of a nested dictionary.

    Args:
        item (dict): The dictionary for which the depth is calculated.

    Returns:
        int: The maximum depth of the dictionary.

    Raises:
        TypeError: If the passed argument is not a dictionary.
    """
    if not isinstance(item, dict):
        raise TypeError(
            "Passed argument must be a dictionary. "
            f"{type(item).__name__} was passed instead.")

    if not item:
        return 0

    return 1 + max(
        find_dict_depth(v) if isinstance(v, dict) else 0
        for v in item.values()
    )


def generate_dict_with_none_values(item: dict) -> dict:
    """
    Converts all values in a nested dictionary to None, maintaining the structure 
    of the dictionary.

    Args:
        item (dict): The dictionary to be converted.

    Returns:
        dict: A new dictionary with the same keys but all values set to None.

    Raises:
        TypeError: If the passed argument is not a dictionary.
    """
    if not isinstance(item, dict):
        raise TypeError(
            "Passed argument must be a dictionary. "
            f"{type(item).__name__} was passed instead.")

    dict_keys = {}
    for key, value in item.items():
        if isinstance(value, dict):
            dict_keys[key] = generate_dict_with_none_values(value)
        else:
            dict_keys[key] = None

    return dict_keys


def pivot_dict(
        data_dict: Dict,
        keys_order: Optional[List] = None,
) -> Dict:
    """
    Converts a dictionary of lists into a nested dictionary, optionally 
    ordering keys.

    Args:
        data_dict (Dict): The dictionary to be pivoted.
        order_list (Optional[List]): An optional list specifying the order of 
            keys for pivoting.

    Returns:
        Dict: A nested dictionary with keys from the original dictionary and 
            values as dictionaries.

    Raises:
        TypeError: If 'data_dict' is not a dictionary or 'keys_order' is not 
            a list.
        ValueError: If 'keys_order' does not correspond to the keys of 
            'data_dict'.
    """

    if not isinstance(data_dict, dict):
        raise TypeError(
            "Argument 'data_dict' must be a dictionary. "
            f"{type(data_dict).__name__} was passed instead."
        )

    if keys_order is not None and not isinstance(keys_order, list):
        raise TypeError(
            "Argument 'keys_order' must be a list or None. "
            f"{type(keys_order).__name__} was passed instead."
        )

    def pivot_recursive(keys, values):
        if not keys:
            return {value: None for value in values}
        else:
            key = keys[0]
            remaining_keys = keys[1:]
            return {item: pivot_recursive(remaining_keys, values)
                    for item in data_dict[key]}

    if keys_order:
        if not isinstance(keys_order, list):
            raise TypeError("Argument 'keys_order' must be a list.")
        if not set(keys_order) == set(data_dict.keys()):
            raise ValueError(
                "Items in keys_order do not correspond to keys of "
                "passed dictionary.")

        keys = keys_order
    else:
        keys = list(data_dict.keys())

    values = list(data_dict[keys[-1]])
    return pivot_recursive(keys[:-1], values)


def dict_cartesian_product(
        data_dict: Dict[Any, List[Any]],
        include_dict_keys: bool = True,
) -> List[Dict[Any, Any] | List[Any]]:
    """
    Generates a list of dictionaries or lists representing the cartesian 
    product of dictionary values.

    Args:
        data_dict (Dict[Any, List[Any]]): The dictionary to be used for the 
            cartesian product. The keys are any hashable type, and the values 
            are lists of elements to be combined.
        include_dict_keys (bool): If True, includes dictionary keys in the 
            resulting dictionaries. If False, returns lists of values only. 
            Default is True.

    Returns:
        List[Dict[Any, Any] | List[Any]]: A list of dictionaries or lists 
            representing the cartesian product of dictionary values. Each 
            dictionary contains one combination of the input values with the 
            corresponding keys, or each list contains one combination 
            of the input values without keys.

    Raises:
        TypeError: If 'data_dict' is not a dictionary or 'include_dict_keys' 
            is not a boolean.
    """
    if not isinstance(data_dict, dict):
        raise TypeError(
            "Argument 'data_dict' must be a dictionary. "
            f"{type(data_dict).__name__} was passed instead."
        )
    if not isinstance(include_dict_keys, bool):
        raise TypeError(
            "Argument 'include_dict_keys' must be a boolean. "
            f"{type(include_dict_keys).__name__} was passed instead."
        )

    if not data_dict:
        return []

    combinations = it.product(*data_dict.values())

    if not include_dict_keys:
        return [list(combination) for combination in combinations]

    return [
        dict(zip(data_dict.keys(), combination))
        for combination in combinations
    ]


def unpivot_dict_to_dataframe(
        data_dict: Dict[str, List[str]],
        key_order: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Converts a nested dictionary into a DataFrame by performing a cartesian 
    product of dictionary values.

    Args:
        data_dict (Dict[str, List[str]]): The dictionary to be unpivoted.
        key_order (Optional[List[str]]): Order of keys for the resulting DataFrame.
            default is None, so the order of keys in the dictionary is used.

    Returns:
        pd.DataFrame: A DataFrame resulting from the cartesian product of 
            dictionary values.

    Raises:
        TypeError: If 'data_dict' is not a dictionary or 'key_order' is not 
            a list.
        ValueError: If 'key_order' does not correspond to the keys of 
            'data_dict'.
    """
    if not isinstance(data_dict, dict):
        raise TypeError(
            "Argument 'data_dict' must be a dictionary. "
            f"{type(data_dict).__name__} was passed instead."
        )

    if key_order is not None and not isinstance(key_order, list):
        raise TypeError(
            "Argument 'key_order' must be a list or None. "
            f"{type(key_order).__name__} was passed instead."
        )

    if key_order and all([isinstance(item, List) for item in key_order]):
        key_order = [item[0] for item in key_order]

    if key_order:
        common_keys = set(key_order).intersection(set(data_dict.keys()))

        if not common_keys:
            raise ValueError(
                "No common keys between 'key_order' and 'data_dict'.")

        data_dict_to_unpivot = {key: data_dict[key] for key in key_order}

    else:
        data_dict_to_unpivot = data_dict
        key_order = list(data_dict_to_unpivot.keys())

    cartesian_product = list(it.product(*data_dict_to_unpivot.values()))

    unpivoted_data_dict = pd.DataFrame(
        data=cartesian_product,
        columns=key_order,
    )

    return unpivoted_data_dict


def add_item_to_dict(
        dictionary: dict,
        item: dict,
        position: int = -1,
) -> dict:
    """
    Add a given item to a specific position in a dictionary.

    Args:
        dictionary (dict): The dictionary to be modified.
        item (dict): The dictionary item to be added.
        position (int, optional): The position in the original dictionary where 
        the item should be added. If not provided, the function adds the item 
        at the end of the original dictionary. Default is -1.

    Raises:
        TypeError: If either 'dictionary' or 'item' is not of 'dict' type.
        ValueError: If 'position' is not within the range of -len(dictionary) to 
            len(dictionary).

    Returns:
        dict: A new dictionary with the item inserted at the specified position. 
            The order of the items is preserved.

    Note:
        This function requires Python 3.7 or later, as it relies on the fact that 
        dictionaries preserve insertion order as of this version.
    """

    if not all(isinstance(arg, dict) for arg in [dictionary, item]):
        raise TypeError("Passed argument/s not of 'dict' type.")

    if not isinstance(position, int):
        raise TypeError("Passed position argument must be of 'int' type.")

    if not -len(dictionary) <= position <= len(dictionary):
        raise ValueError(
            "Invalid position. Position must be "
            f"within {-len(dictionary)} and {len(dictionary)}")

    items = list(dictionary.items())
    item_list = list(item.items())

    for i in item_list:
        items.insert(position, i)

    return dict(items)


def merge_series_to_dataframe(
        series: pd.Series,
        dataframe: pd.DataFrame,
        position: Literal[0, -1] = 0,
) -> pd.DataFrame:
    """
    Merge a given 'series' with a 'dataframe' at the specified position.
    It repeats each value of the series as a new column of the dataframe.
    Final dataframe has a number of column of initial dataframe plus the number
    of items of the series.

    Args:
    - series (pd.Series): The series to be merged.
    - dataframe (pd.DataFrame): The dataframe to merge with.
    - position (Literal[0, -1], optional): The position at which to merge the series.
        0 indicates merging at the beginning, and -1 indicates merging at the end.
        Defaults to 0.

    Returns:
    pd.DataFrame: The merged dataframe.
    """
    if series.empty or dataframe.empty:
        raise ValueError("Both series and dataframe must be non-empty.")

    series_to_df = pd.concat(
        objs=[series]*len(dataframe),
        axis=1,
    ).transpose().reset_index(drop=True)

    objs = [series_to_df, dataframe]

    if position == -1:
        objs = objs[::-1]

    return pd.concat(objs=objs, axis=1)


def check_dataframes_equality(
        df_list: List[pd.DataFrame],
        skip_columns: Optional[List[str]] = None,
        cols_order_matters: bool = False,
        rows_order_matters: bool = False,
        homogeneous_num_types: bool = True,
) -> bool:
    """
    Check the equality of multiple DataFrames while optionally skipping 
    specified columns. The function can also ignore the order of columns
    and rows in the DataFrames.

    Args:
        df_list (List[pd.DataFrame]): A list of Pandas DataFrames to compare.
        skip_columns (List[str], optional): A list of column names to skip 
            during comparison.
        cols_order_matters (bool, optional): If set to False, two dataframes
            with same columns in different orders are still identified as equal.
        rows_order_matters (bool, optional): If set to False, two dataframes
            with same rows in different orders are still identified as equal. 

    Returns:
        bool: True if all DataFrames are equal, False otherwise.

    Raises:
        ValueError: If any column in skip_columns is not present in all 
            DataFrames.
    """
    df_list_copy = deepcopy(df_list)

    if skip_columns:
        all_columns_set = set().union(*(df.columns for df in df_list_copy))
        if not set(skip_columns).issubset(all_columns_set):
            raise ValueError(
                "One or more items in 'skip_columns' argument are never "
                "present in any dataframe.")

        for dataframe in df_list_copy:
            dataframe.drop(columns=skip_columns, errors='ignore', inplace=True)

    # Convert all numeric values to float64 for consistent comparisons
    if homogeneous_num_types:
        df_list_copy = [
            df.apply(pd.to_numeric, errors='ignore')
            for df in df_list_copy
        ]

    shapes = set(df.shape for df in df_list_copy)
    if len(shapes) > 1:
        return False

    columns = set(tuple(sorted(df.columns)) for df in df_list_copy)
    if len(columns) > 1:
        return False

    if not cols_order_matters:
        df_list_copy = [df.sort_index(axis=1) for df in df_list_copy]

    if not rows_order_matters:
        df_list_copy = [
            df.sort_values(df.columns.tolist()).reset_index(drop=True)
            for df in df_list_copy
        ]

    first_df = df_list_copy[0]
    return all(first_df.equals(df) for df in df_list_copy[1:])


def check_dataframe_columns_equality(
    df_list: List[pd.DataFrame],
    skip_columns: Optional[List[str]] = None,
) -> bool:
    """
    Check the equality of column headers in multiple DataFrames while 
    optionally skipping specified columns.

    Args:
        df_list (List[pd.DataFrame]): A list of Pandas DataFrames to compare.
        skip_columns (List[str], optional): A list of column names to skip 
            during comparison.

    Returns:
        bool: True if all DataFrames have the same set of columns, False otherwise.

    Raises:
        ValueError: If df_list is empty or any DataFrame in df_list has no columns.
    """
    if not df_list:
        raise ValueError("Passed list must not be empty.")

    if any(not isinstance(df, pd.DataFrame) for df in df_list):
        raise TypeError("Passed list must include only Pandas DataFrames.")

    if skip_columns is not None:
        modified_df_list = [
            dataframe.drop(columns=skip_columns, errors='ignore')
            for dataframe in df_list
        ]
    else:
        modified_df_list = df_list

    columns_list = [set(df.columns) for df in modified_df_list]

    first_columns = columns_list[0]
    return all(columns == first_columns for columns in columns_list[1:])


def add_column_to_dataframe(
        dataframe: pd.DataFrame,
        column_header: str,
        column_values: Any = None,
        column_position: Optional[int] = None,
) -> bool:
    """
    Inserts a new column into the provided DataFrame at the specified 
    position or at the end if no position is specified, only if the column
    does not already exist.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame to which the column 
            will be added.
        column_header (str): The name/header of the new column.
        column_values (Any, optional): The values to be assigned to the new 
            column. If not provided, the column will be populated with 
            NaN values.
        column_position (int, optional): The index position where the new 
            column will be inserted. If not provided, the column will be 
            inserted at the end. Default to None.

    Returns:
        bool: True if the column was added, False if the column already exists.

    Raises:
        TypeError: If column_header is not string or dataframe is not a Pandas
            DataFrame.
        ValueError: If the column_position is greater than the current number 
            of columns or if the column_header is empty, or if the legth of the
            passed column does not match the number of rows of the DataFrame.
    """
    if not isinstance(column_header, str):
        raise TypeError("Passed column header must be of type string.")

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "Passed dataframe argument must be a Pandas DataFrame.")

    if column_header in dataframe.columns:
        return False

    if column_position is not None and column_position > len(dataframe):
        raise ValueError(
            "Passed column_position is greater than the number of columns "
            "of the dataframe.")

    if column_position is None:
        column_position = len(dataframe.columns)

    if column_values and \
            len(column_values) != dataframe.shape[0]:
        raise ValueError(
            "Passed column_values length must match the number or rows"
            "of the DataFrame.")

    dataframe.insert(
        loc=column_position,
        column=column_header,
        value=column_values,
    )

    return True


def substitute_dict_keys(
        source_dict: Dict[str, Any],
        key_mapping_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Substitute the keys in source_dict with the values from key_mapping.
    Raises an error if a value in key_mapping does not exist as a key in 
    source_dict.

    Args:
        source_dict (dict): A dictionary whose keys need to be substituted.
        key_mapping (dict): A dictionary containing the mapping of original 
            keys to new keys.

    Returns:
        dict: A new dictionary with substituted keys.

    Raises:
        TypeError: If passed arguments are not dictionaries.
        ValueError: If a value from key_mapping is not a key in source_dict.
    """
    if not isinstance(source_dict, dict) or \
            not isinstance(key_mapping_dict, dict):
        raise TypeError("Passed arguments must be of dictionaries.")

    substituted_dict = {}
    for key, new_key in key_mapping_dict.items():
        if key not in source_dict:
            raise ValueError(
                f"Key '{key}' from key_mapping is not found in source_dict.")
        substituted_dict[new_key] = source_dict[key]
    return substituted_dict


def fetch_dict_primary_key(
        dictionary: Dict[str, Any],
        second_level_key: str | int,
        second_level_value: Any,
) -> str | int:
    """
    Fetches the primary key from a dictionary based on a second-level key-value
    pair. If the second-level key-value pair is not found, returns None.

    Args:
        dictionary (Dict[str, Any]): The dictionary to search.
        second_level_key (str | int): The key to search for in the second level.
        second_level_value (Any): The value to search for in the second level.

    Returns:
        str | int: The primary key of the dictionary where the second-level 
            key-value pair is found, or None if not found.

    Raises: 
        TypeError: If dictionary is not a dictionary.
    """
    if not isinstance(dictionary, dict):
        raise TypeError("Passed dictionary must be a dictionary.")

    for primary_key, value in dictionary.items():
        if isinstance(value, dict) and \
                value.get(second_level_key) == second_level_value:
            return primary_key
    return None


def filter_dataframe(
        df_to_filter: pd.DataFrame,
        filter_dict: Dict[str, List[str]],
        reset_index: bool = True,
        reorder_cols_based_on_filter: bool = False,
        reorder_rows_based_on_filter: bool = False,
) -> pd.DataFrame:
    """
    Filters a DataFrame based on a dictionary identifying dataframe columns 
    and the related items to be filtered.

    Args:
        df_to_filter (pd.DataFrame): The DataFrame to filter.
        filter_dict (dict): A dictionary where keys are dataframe column names 
            and values are lists of strings that the filtered dictionary 
            columns will include.
        reset_index (bool, Optional): If True, resets the index of the filtered 
            DataFrame. Default to True.
        reorder_cols_based_on_filter (bool, Optional): If True, reorder the filtered
            dataframe columns according to the order of parsed dictionary
            keys. Default to False.
        reorder_rows_based_on_filter (bool, Optional): If True, reorder the filtered
            dataframe rows according to the order of parsed dictionary
            values. Default to False.

    Returns:
        pd.DataFrame: A DataFrame filtered based on the specified column 
            criteria.

    Raises:
        ValueError: If df_to_filter is not a DataFrame, if filter_dict is not 
            a dictionary, or if any key in filter_dict is not a column in 
            df_to_filter.
    """
    if not isinstance(df_to_filter, pd.DataFrame):
        raise ValueError("Passed df_to_filter must be a Pandas DataFrame.")

    if not isinstance(filter_dict, dict):
        raise ValueError("Passed filter_dict must be a dictionary.")

    for key in filter_dict.keys():
        if key not in df_to_filter.columns:
            raise ValueError(
                f"Key '{key}' in filter_dict is not a DataFrame column.")

    # filter dataframe based on filter_dict
    mask = pd.Series([True] * len(df_to_filter))

    for column, values in filter_dict.items():
        mask = mask & df_to_filter[column].isin(values)

    filtered_df = df_to_filter[mask].copy()

    # optionally reorder columns based on filter_dict keys
    if reorder_cols_based_on_filter:
        filter_keys = list(filter_dict.keys())
        other_keys = [
            col
            for col in df_to_filter.columns
            if col not in filter_keys
        ]
        new_columns_order = filter_keys + other_keys
        filtered_df = filtered_df[new_columns_order]

    # optionally reorder rows based on filter_dict values
    if reorder_rows_based_on_filter:
        df_order = unpivot_dict_to_dataframe(filter_dict)
        sort_key = pd.Series(
            range(len(df_order)),
            index=pd.MultiIndex.from_frame(df_order)
        )
        filtered_df['sort_key'] = filtered_df.set_index(
            list(filter_dict.keys())
        ).index.map(sort_key.get)
        filtered_df.sort_values('sort_key', inplace=True)
        filtered_df.drop(columns='sort_key', inplace=True)

    if reset_index:
        filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def compare_dicts_ignoring_order(
        iterable: Iterable[Dict[str, List[Any]]]
) -> bool:
    """
    Compares any number of dictionaries to see if they are the same, ignoring 
    the order of items in the lists which are the values of the dictionaries.

    Args:
        iterable (Iterable[Dict[str, List[Any]]]): An iterable of dictionaries 
            to compare.

    Returns:
        bool: True if all dictionaries are the same (ignoring order of list 
            items), False otherwise.

    Raises:
        ValueError: If dicts is not an iterable, or if any value in dicts is 
            not a dictionary.
    """
    try:
        iter(iterable)
    except TypeError:
        raise ValueError("'iterable' argument must be an iterable.")

    for value in iterable:
        if not isinstance(value, dict):
            raise ValueError(
                "Each item in 'iterable' must be a dictionary.")

    iterable = list(iterable)
    if len(iterable) < 2:
        return True

    reference = iterable[0]
    ref_keys = set(reference.keys())

    for d in iterable[1:]:
        if set(d.keys()) != ref_keys:
            return False
        for key in ref_keys:
            if sorted(d[key]) != sorted(reference[key]):
                return False

    return True


def find_non_allowed_types(
        dataframe: pd.DataFrame,
        allowed_types: Tuple,
        target_col_header: str,
        return_col_header: Optional[str] = None,
        allow_none: bool = False,
) -> List:
    """
    Find rows in a DataFrame where the value in a specified column is not of 
    an allowed type.

    Args:
        dataframe (pd.DataFrame): The DataFrame to check.
        allowed_types (Tuple[type]): The types that are allowed for the target 
            column values.
        target_col_header (str): The name of the column to check.
        return_col_header (Optional[str]): The name of the column to return. 
            If None, return list of items in the target_col_header with non-allowed
            types.
        allow_none (bool): Whether to allow None values. Default is False.

    Returns:
        List: The list of values in the return column for rows where the target 
            column is not of an allowed type, or items in the target column 
            with non-allowed types.

    Raises:
        ValueError: If dataframe is not a DataFrame, if target_col_header or 
            return_col_header is not a column in dataframe, or if allowed_types 
            is not a tuple.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError("Passed 'dataframe' argument must be a DataFrame.")
    if not isinstance(allowed_types, tuple):
        raise ValueError("Passed 'allowed_types' argument must be a tuple.")
    if target_col_header not in dataframe.columns:
        raise ValueError(
            f"'{target_col_header}' is not a column in dataframe.")
    if return_col_header and return_col_header not in dataframe.columns:
        raise ValueError(
            f"'{return_col_header}' is not a column in dataframe.")

    def is_non_allowed(row):
        value = row[target_col_header]
        if pd.isna(value):
            return not allow_none
        return not isinstance(value, allowed_types)

    non_allowed_rows = dataframe.apply(is_non_allowed, axis=1)

    if return_col_header:
        return dataframe.loc[non_allowed_rows, return_col_header].tolist()

    return dataframe.loc[non_allowed_rows, target_col_header].tolist()


def find_dict_keys_corresponding_to_value(
        dictionary: Dict[Any, Any],
        target_value: Any,
) -> Optional[Any]:
    """
    This function finds all keys in a dictionary that correspond to 
    a given value.

    Parameters:
        dictionary (Dict[Any, Any]): The dictionary to search.
        target_value (Any): The value to find.

    Returns:
        List[Any]: The keys corresponding to the target value. If the value 
            is not found, returns an empty list.
    """
    if not isinstance(dictionary, dict):
        raise TypeError(
            "Passed 'dictionary' argument must be a dictionary."
            f"{type(dictionary).__name__} was passed instead.")

    return [
        key for key, value in dictionary.items()
        if value == target_value
    ]


def calculate_values_difference(
        value_1: float,
        value_2: float,
        relative_difference: bool = True,
        modules_difference: bool = False,
        ignore_nan: bool = False,
) -> float:
    """
    Calculate the difference between two values.

    Parameters:
        value_1 (float): The first value.
        value_2 (float): The second value.
        relative_difference (bool): If True, calculate the relative difference. 
            Default is True.
        modules_difference (bool): If True, calculate the module of difference 
            (either absolute or relative). Default is False.
        ignore_nan (bool): If True, ignore non-numeric values. 
            Default is False.

    Returns:
        float: The calculated difference. If both values are non-numeric 
            and ignore_nan_values is True, nothing is returned.
    """
    if not isinstance(value_1, float | int) or \
            not isinstance(value_2, float | int):
        if not ignore_nan:
            raise ValueError("Passed values must be of numeric type.")
        else:
            return

    if modules_difference:
        difference = abs(value_1 - value_2)
        reference = abs(value_2)
    else:
        difference = value_1 - value_2
        reference = value_2

    if relative_difference:

        if difference == 0:
            return 0

        if reference == 0:
            return float('inf')

        return difference / reference

    else:
        return difference


def remove_empty_items_from_dict(
        dictionary: Dict,
        empty_values: List = [None, 'nan', 'None', 'null', '', 'NaN', [], {}],
) -> Dict:
    """
    Recursively removes keys with empty values from a dictionary.

    Args:
        dictionary (Dict): The dictionary to clean.

    Returns:
        Dict: A new dictionary with all keys that had empty values removed.

    Raises:
        TypeError: If the passed argument is not a dictionary.
    """
    empty_values_list = [None, 'nan', 'None', 'null', '', 'NaN', [], {}]

    if not isinstance(dictionary, dict):
        raise TypeError(
            "Passed argument must be a dictionary. "
            f"{type(dictionary).__name__} was passed instead")

    if not [value for value in empty_values if value in empty_values_list]:
        raise ValueError(
            "Passed empty_values tuple must include at least one type of the "
            f"default empty values {empty_values_list}.")

    def _remove_items(d: Dict) -> Dict:
        cleaned_dict = {}

        for key, value in d.items():
            if isinstance(value, dict):
                nested = _remove_items(value)
                if nested:
                    cleaned_dict[key] = nested
            elif value not in empty_values:
                cleaned_dict[key] = value

        return cleaned_dict

    return _remove_items(dictionary)


def merge_dicts(
        dicts_list: List[Dict],
        unique_values: bool = False,
) -> Dict[str, List[Any]]:
    """
    Merges a list of dictionaries into a single dictionary.

    - If a key appears in multiple dictionaries, its values are combined into a list.
    - If `unique_values` is True, ensures values are unique per key.

    Args:
        dicts_list (List[Dict[str, Any]]): A list of dictionaries to merge.
        unique_values (bool): If True, ensures unique values per key. Default is False.

    Returns:
        Dict[str, List[Any]]: A merged dictionary with keys combined and values in lists.
    """
    merged = {}

    for dictionary in dicts_list:
        if dictionary is None:
            dictionary = {}

        for key, value in dictionary.items():

            if value is None:
                continue

            if not isinstance(value, Iterable) or \
                    isinstance(value, (str, bytes)):
                value = [value]

            if key not in merged:
                merged[key] = list(value) if not unique_values else set(value)

            else:
                if unique_values:
                    merged[key].update(value)  # Use set to avoid duplicates
                else:
                    merged[key].extend(value)  # Allow duplicates

    return {key: list(values) for key, values in merged.items()}


def pivot_dataframe_to_data_structure(
    data: pd.DataFrame,
    primary_key: Optional[str | int] = None,
    secondary_key: Optional[str | int] = None,
    merge_dict: bool = False,
    skip_process_str: bool = False,
) -> dict:

    data_structure = {}
    primary_key = primary_key or data.columns[0]

    if primary_key not in data.columns:
        raise ValueError(
            f"Primary key '{primary_key}' not found in DataFrame columns.")

    for _, row in data.iterrows():
        key = row[primary_key]

        if key not in data_structure:
            data_structure[key] = {}

        inner_dict = {}
        for column in data.columns:
            if column == primary_key:
                continue

            if column == secondary_key:
                break

            value = row[column]
            if value is not None:
                if not skip_process_str:
                    inner_dict[column] = util_text.process_str(value)
                else:
                    inner_dict[column] = value

        if merge_dict:
            data_structure[key] = merge_dicts(
                [data_structure[key], inner_dict])
        else:
            data_structure[key] = inner_dict

    if secondary_key:
        if secondary_key not in data.columns:
            raise ValueError(
                f"Secondary key '{secondary_key}' not found in DataFrame columns.")

        secondary_key_index = data.columns.get_loc(secondary_key)
        secondary_keys_list = data.columns[secondary_key_index:]

        for _, row in data.iterrows():
            outern_key = row[primary_key]
            inner_key = row[secondary_key]

            data_structure[outern_key].setdefault(secondary_key, {})

            inner_dict = {}

            for column in secondary_keys_list:
                if column == secondary_key:
                    continue

                value = row[column]
                if value is not None:
                    inner_dict[column] = util_text.process_str(value)

            data_structure[outern_key][secondary_key][inner_key] = inner_dict

    if None in data_structure:
        return data_structure[None]

    return data_structure


def transform_dict_none_to_values(dictionary: Dict, none_to: Any) -> Dict:
    """ 
    Parse dictionary values, and in case such values are None transform them
    to value_to.
    """
    if not isinstance(dictionary, Dict):
        raise TypeError(f"Dict type expected, '{type(dictionary)}' passed.")

    result = {}

    for key, value in dictionary.items():
        if value is None:
            result[key] = none_to
        else:
            result[key] = value

    return result


def is_sparse(array: np.ndarray, threshold: float) -> bool:
    """
    Checks if a numpy ndarray can be considered sparse based on a given threshold.

    Parameters:
        array (np.ndarray): The numpy array to check.
        threshold (float): The proportion of zero elements required to consider
            the array as sparse.

    Returns:
        bool: True if the array is sparse, False otherwise.
    """
    total_elements = array.size
    zero_elements = np.count_nonzero(array == 0)
    proportion_zero = zero_elements / total_elements

    if proportion_zero == 1:
        return False
    elif proportion_zero >= threshold:
        return True
    else:
        return False
