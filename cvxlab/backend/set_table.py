"""
set_table.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module provides the SetTable class for handling and manipulating Set tables 
in a structured format. It allows for managing Set tables with detailed logging 
and interaction with a SQLite database. The SetTable class integrates with 
pandas for data manipulation, providing tools to fetch, update, and manage 
data efficiently.
"""

import pandas as pd

from typing import Any, Dict, Iterator, List, Optional, Tuple
from cvxlab.constants import Constants
from cvxlab.log_exc.logger import Logger


class SetTable:
    """
    Generates and manipulates a Set tables with specific attributes and methods.

    This class encapsulates operations related to Set tables, such as fetching headers,
    filters, and maintaining data. It integrates with a logger for activity
    logging and uses a pandas DataFrame to handle the Set's data.

    Args:
        logger (Logger): Logger instance for logging activities.
        key_name (str): The key/name of the Set.
        **set_info: Arbitrary keyword arguments defining attributes of the Set,
            such as symbols, table names, etc.

    Attributes:
        logger (Logger): Logger instance for logging.
        name (Optional[str]): The name of the Set.
        table_name (Optional[str]): The name of the associated SQLite table.
        split_problem (bool): Indicates whether the Set defines multiple 
            numerical problems (namely, the Scenarios).
        description (Optional[str]): Description metadata for the Set.
        copy_from (Optional[str]): Name of another Set to copy values from.
        table_structure (Dict[str, Any]): Structure of the SQLite table for 
            data handling.
        table_headers (Dict[str, List[str]]): Headers of the SQLite table.
        table_filters (Dict[int, Any]): Filters applicable to the table.
        set_categories (Dict[str, Any]): Categories applicable to the Set.
        data (Optional[pd.DataFrame]): DataFrame containing the Set's data.
    """

    def __init__(
            self,
            logger: Logger,
            key_name: str,
            **set_info,
    ) -> None:
        """
        Initializes a SetTable instance with the Set's information.

        Args:
            logger (Logger): Logger instance for logging activities.
            key_name (str): The key/name of the set.
            **set_info: Arbitrary keyword arguments for set attributes.
        """
        self.logger = logger.get_child(__name__)

        self.name: Optional[str] = None
        self.table_name: Optional[str] = None

        self.split_problem: bool = False
        self.description: Optional[str] = None
        self.copy_from: Optional[str] = None

        self.table_structure: Dict[str, Any] = {}
        self.table_headers: Dict[str, List[str]] = {}
        self.table_filters: Dict[int, Any] = {}
        self.set_categories: Dict[str, Any] = {}
        self.data: Optional[pd.DataFrame] = None

        self.fetch_names(key_name)
        self.fetch_attributes(set_info)
        self.fetch_headers_and_filters()

    @property
    def set_name_header(self) -> str | None:
        """
        Returns the standard name header from the table headers based on 
        configuration constants.

        Returns:
            Optional[str]: The standard name header if available, otherwise None.
        """
        if self.table_headers is not None:
            return self.table_headers[Constants.Labels.NAME][0]
        return None

    @property
    def set_excel_file_headers(self) -> List | None:
        """
        Returns a list of headers formatted for use in Excel files.

        Returns:
            Optional[List[str]]: List of headers suitable for Excel, or None 
                if not defined.
        """
        if self.table_headers is not None:
            return [item[0] for item in list(self.table_headers.values())]
        return None

    @property
    def set_filters_dict(self) -> Dict[str, List[str]] | None:
        """
        Returns a dictionary of filter headers with their corresponding filter 
        values.

        Returns:
            Optional[Dict[str, List[str]]]: Dictionary where keys are filter 
                headers and values are lists of filter criteria, or None if not set.
        """
        if self.table_filters:
            return {
                filter_items['header']: filter_items['values']
                for filter_items in self.table_filters.values()
            }
        return None

    @property
    def set_filters_headers(self) -> Dict[int, str] | None:
        """
        Returns a mapping from filter index to their corresponding headers.

        Returns:
            Optional[Dict[int, str]]: Dictionary mapping filter indices to 
                headers, or None if not defined.
        """
        if self.table_filters:
            return {
                key: value['header']
                for key, value in self.table_filters.items()
            }
        return None

    @property
    def set_items(self) -> List[str] | None:
        """
        Returns a list of items in the data set based on the standard name header.

        Returns:
            Optional[List[str]]: List of item names from the data set, or None 
                if data is empty or header is undefined.
        """
        if self.data is not None:
            return list(self.data[self.set_name_header])
        return None

    def fetch_names(self, set_key: str) -> None:
        """
        Defines the Set's name and table name based on the provided key.

        Args:
            set_key (str): The key/name of the set.
        """
        prefix = Constants.Labels.SET_TABLE_NAME_PREFIX
        self.name = set_key
        self.table_name = prefix+set_key.upper()

    def fetch_attributes(self, set_info: dict) -> None:
        """
        Sets attributes on the instance from the provided dictionary, and 
        constructs the Set's table structure.

        Args:
            set_info (dict): Dictionary of attribute names and values for the Set.
        """
        col_name_suffix = Constants.Labels.COLUMN_NAME_SUFFIX
        filters_header = Constants.Labels.FILTERS
        name_header = Constants.Labels.NAME

        for key, value in set_info.items():
            if key != filters_header and value is not None:
                setattr(self, key, value)

        # column with name of set entries
        self.table_structure[name_header] = self.name + col_name_suffix

        # column with filter values
        if filters_header in set_info:
            self.table_structure[filters_header] = {}
            filters_info: dict = set_info[filters_header]

            if filters_info:
                for filter_key, filter_values in filters_info.items():
                    self.table_structure[filters_header][filter_key] = {
                        'header': self.name + '_' + filter_key,
                        'values': filter_values
                    }

    def fetch_headers_and_filters(self) -> None:
        """
        Initializes the table headers and filters based on the predefined table 
        structure.

        This method updates the instance's table_headers and table_filters attributes
        based on configuration constants. It extracts specific headers for name, filters,
        and aggregation from the table's structural definition, and sets them up for
        easy access throughout the class's methods.
        """
        name_key = Constants.Labels.NAME
        filters_key = Constants.Labels.FILTERS
        generic_field_type = Constants.Labels.GENERIC_FIELD_TYPE

        # Fetching filters
        self.table_filters = self.table_structure.get(filters_key, None)

        # Fetching table headers
        name_header = self.table_structure.get(name_key, None)
        filters_headers = {
            'filter_' + str(key): value['header']
            for key, value in self.table_structure.get(filters_key, {}).items()
        }

        self.table_headers = {
            key: [value, generic_field_type]
            for key, value in {name_key: name_header, **filters_headers}.items()
        }

    def __repr__(self) -> str:
        """
        Returns a string representation of the SetTable instance, excluding data 
        and logger.

        Returns:
            str: String representation of the SetTable instance.
        """
        output = ''
        for key, value in self.__dict__.items():
            if key in ('data', 'logger'):
                pass
            elif key != 'values':
                output += f'\n{key}: {value}'
            else:
                output += f'\n{key}: \n{value}'
        return output

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        """
        Iterates over the instance's attributes, excluding data and logger.

        Yields:
            Tuple[Any, Any]: Key-value pairs of the instance's attributes.
        """
        for key, value in self.__dict__.items():
            if key not in ('data', 'logger'):
                yield key, value
