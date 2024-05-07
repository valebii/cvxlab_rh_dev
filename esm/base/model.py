"""
model.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module defines the Model class, a comprehensive framework designed to 
facilitate the management of complex data processing and optimization tasks 
within a modeling environment.

The Model class provides functionalities for SQLite database management, 
numerical optimization using CVXPY, and visualization through Power BI reporting. 

The primary focus of this module is to streamline operations across database 
interactions, data file management, numerical problem formulation, and result 
visualization, making it suitable for applications in scientific computing, 
economic modeling, or any domain requiring robust data analysis and visualization 
capabilities.

The Model class integrates various components such as logging, file management, 
and core functionalities, ensuring a cohesive workflow from data input to 
report generation. It supports both the creation of new data structures and the 
utilization of existing datasets, allowing for flexible model configurations 
based on user-defined settings.
"""

from pathlib import Path
from typing import Any, Dict

from esm.constants import Constants
from esm.log_exc import exceptions as exc
from esm.log_exc.logger import Logger
from esm.support.dotdict import DotDict
from esm.support.file_manager import FileManager
from esm.support.pbi_manager import PBIManager
from esm.base.core import Core


class Model:
    """
    Class representing a modeling environment that handles SQLite data 
    generation and processing, database interactions, numerical optimization 
    model generation and handling with CVXPY, and PowerBi report generation 
    for visualizing and inspecting exogenous and endogenous data. 

    This class initializes with a configuration for managing directories, 
    logging, and file management for a specific model. It also sets up various
    components including a logger, file manager, and core functionalities.

    Attributes:
        logger (Logger): An instance of Logger to handle logging across the class.
        files (FileManager): An instance of FileManager to manage file operations.
        settings (DotDict): A dictionary-like object storing configurations such as 
            model name, file paths, and operational flags.
        paths (DotDict): A dictionary-like object storing the paths for model 
            directories and associated files.
        core (Core): An instance of Core that manages the core functionality 
            of the model.
        pbi_tools (PBIManager): An instance of PBIManager to manage Power BI 
            report interactions.

    Parameters of settings attribute:
        model_dir_name (str): Name of the directory for the model (and name of 
            the model itself).
        main_dir_path (str): Path to the main directory where the model 
            directory will be located.
        use_existing_data (bool, optional): Flag to indicate whether to use 
            existing data files and SQLite database. Defaults to False.
        multiple_input_files (bool, optional): Flag to indicate whether 
            multiple input files are expected. Defaults to False.
        log_level (str, optional): Determines the logging level ('info' by 
            default).
        log_format (str, optional): Specifies the format of the logs 
            ('minimal' by default).
        sets_xlsx_file (str, optional): The Excel file name containing 
            settings. Defaults to 'sets.xlsx'.
        input_data_dir (str, optional): Sub-directory for input data. 
            Defaults to 'input_data'.
        input_data_file (str, optional): Name of the Excel file used for 
            input data. Defaults to 'input_data.xlsx'.
        sqlite_database_file (str, optional): Name of the SQLite database file. 
            Defaults to 'database.db'.
        sqlite_database_foreign_keys (bool, optional): Whether to enforce 
            foreign key constraints in SQLite. Defaults to True.
        powerbi_report_file (str, optional): Name of the Power BI report file. 
            Defaults to 'dataset.pbix'.

    Raises:
        ValueError: If any critical configurations are invalid or not found.
        FileNotFoundError: If necessary files are not found in the specified paths.
    """

    def __init__(
            self,
            model_dir_name: str,
            main_dir_path: str,
            use_existing_data: bool = False,
            multiple_input_files: bool = False,
            log_level: str = 'info',
            log_format: str = 'minimal',
            sets_xlsx_file: str = 'sets.xlsx',
            input_data_dir: str = 'input_data',
            input_data_file: str = 'input_data.xlsx',
            sqlite_database_file: str = 'database.db',
            sqlite_database_foreign_keys: bool = True,
            powerbi_report_file: str = 'dataset.pbix',
    ) -> None:

        self.logger = Logger(
            logger_name=str(self),
            log_level=log_level.upper(),
            log_format=log_format,
        )

        self.logger.debug(f"'{self}' object initialization...")
        self.logger.info(
            f"Generating '{model_dir_name}' pyESM model instance.")

        self.files = FileManager(logger=self.logger)

        self.settings = DotDict({
            'model_name': model_dir_name,
            'use_existing_data': use_existing_data,
            'multiple_input_files': multiple_input_files,
            'sets_xlsx_file': sets_xlsx_file,
            'input_data_dir': input_data_dir,
            'input_data_file': input_data_file,
            'sqlite_database_file': sqlite_database_file,
            'sqlite_database_foreign_keys': sqlite_database_foreign_keys,
            'powerbi_report_file': powerbi_report_file,
        })

        model_dir_path = Path(main_dir_path) / model_dir_name
        self.paths = DotDict({
            'model_dir': model_dir_path,
            'input_data_dir': model_dir_path / input_data_dir,
            'sets_excel_file': model_dir_path / sets_xlsx_file,
            'sqlite_database': model_dir_path / sqlite_database_file,
            'pbi_report': model_dir_path / powerbi_report_file,
        })

        self.validate_model_dir()

        self.core = Core(
            logger=self.logger,
            files=self.files,
            settings=self.settings,
            paths=self.paths,
        )

        if self.settings['use_existing_data']:
            self.load_model_coordinates()
            self.initialize_problems()

        self.pbi_tools = PBIManager(
            logger=self.logger,
            settings=self.settings,
            paths=self.paths,
        )

        self.logger.debug(f"'{self}' object initialized.")

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name}'

    def validate_model_dir(self) -> None:
        """
        This method checks if the model directory and all the required setup 
        files exist. It uses the 'dir_files_check' method from the 'files' 
        object to perform the check. 

        Returns:
            None
        """
        setup_files: Dict[int, str] = Constants.get('_SETUP_FILES')

        # modify to check if all necessary items are there in case of use existing data
        if self.files.dir_files_check(
            dir_path=self.paths['model_dir'],
            files_names_list=list(setup_files.values()),
        ):
            self.logger.info(
                'Model directory and required setup files validated.')

    def load_model_coordinates(self) -> None:
        """
        Loads sets data and variable coordinates to the Model.Index.
        If the 'use_existing_data' setting is True, it loads existing sets 
        data and variable coordinates provided by SQLite database.
        Otherwise, it loads new sets data and variable coordinates to 
        Model.Index.
        Based on Model settings, SQLite tables foreign keys can be enabled.

        Raises:
            FileNotFoundError: If the sets_xlsx_file specified in the 
            settings is missing and 'use_existing_data' is True.

        Return:
            None
        """
        if self.settings['use_existing_data']:
            self.logger.info(
                'Loading existing sets data and variable coordinates to Index.')
        else:
            self.logger.info(
                'Loading new sets data and variable coordinates to Index.')

        try:
            self.core.index.load_sets_data_to_index(
                excel_file_name=self.settings['sets_xlsx_file'],
                excel_file_dir_path=self.paths['model_dir']
            )
        except FileNotFoundError as e:
            msg = f"'{self.settings['sets_xlsx_file']}' file missing. " \
                "Set 'use_existing_data' to False to generate a new settings file."
            self.logger.error(msg)
            raise exc.SettingsError(msg) from e

        self.core.index.load_coordinates_to_data_index()
        self.core.index.load_all_coordinates_to_variables_index()
        self.core.index.filter_coordinates_in_variables_index()
        self.core.index.map_vars_aggregated_dims()

        if self.settings['sqlite_database_foreign_keys']:
            self.core.index.fetch_foreign_keys_to_data_tables()

    def initialize_blank_data_structure(self) -> None:
        """
        Initializes the blank data structure for the model: create blank 
        SQLite database with set tables and data tables, and fills the latter
        SQLite tables with sets information. Finally, it created blank excel 
        input data files.
        If the SQLite database already exists, it gives the option to erase it 
        and generate a new one, or to work with the existing SQLite database.

        Returns:
            None
        """
        sqlite_db_name = self.settings['sqlite_database_file']

        if self.settings['use_existing_data']:
            self.logger.info(
                "Relying on existing SQLite database and input excel file/s.")
            return

        if Path(self.paths['sqlite_database']).exists():
            self.logger.info(f"Database '{sqlite_db_name}' already exists.")

            erased = self.files.erase_file(
                dir_path=self.paths['model_dir'],
                file_name=sqlite_db_name,
                force_erase=False,
                confirm=True,
            )

            if erased:
                self.logger.info(
                    f"Erasing SQLite database '{sqlite_db_name}'. Generating "
                    "new database and excel input file/s.")
            else:
                self.logger.info(
                    f"Relying on existing SQLite database '{sqlite_db_name}' "
                    "and on existing input excel file/s.")
                return
        else:
            self.logger.info(
                f"Generating new SQLite database '{sqlite_db_name}' and "
                "input excel file/s.")

        self.core.database.create_blank_sqlite_database()
        self.core.database.load_sets_to_sqlite_database()
        self.core.database.generate_blank_sqlite_data_tables()
        self.core.database.sets_data_to_sql_data_tables()
        self.core.database.generate_blank_data_input_files()

    def load_exogenous_data_to_sqlite_database(
            self,
            operation: str = 'update',
            force_overwrite: bool = False,
    ) -> None:
        """
        Loads input (exogenous) data to the SQLite database. 

        Args:
            operation (str, optional): The operation to perform on the 
                database. Defaults to 'update'.
            force_overwrite (bool, optional): Whether to force overwrite 
                existing data. Defaults to False.
        """
        self.logger.info('Loading input data to SQLite database.')

        self.core.database.load_data_input_files_to_database(
            operation=operation,
            force_overwrite=force_overwrite,
        )
        # TO BE COMPLETED (automatically filling blank data)
        self.core.database.empty_data_completion(operation)

    def initialize_problems(
            self,
            force_overwrite: bool = False,
    ) -> None:
        """
        Initializes numerical problems in the Model instance. Specifically, the
        method initializes variables, fed data to exogenous variables, and
        generates numerical problems based on the symbolic formulation.

        Args:
            force_overwrite (bool, optional): If True, forces the overwrite 
            of existing numerical problems. Used for testing purpose. Defaults 
            to False.

        Return:
            None
        """
        self.logger.info(
            'Loading symbolic problem, initializing numerical problems.')

        self.core.initialize_problems_variables()
        self.core.data_to_cvxpy_exogenous_vars()
        self.core.define_numerical_problems(force_overwrite)

    def run_model(
        self,
        solver: str = 'SCIPY',
        verbose: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Solve numerical problems defined by the model instance.

        Parameters:
            solver (str): The solver to use for solving numerical problems. 
                Defaults to 'SCIPY'.
            verbose (bool): Whether to print verbose output during the model 
                run. Defaults to True.
            **kwargs: Additional keyword arguments to be passed to the solver.

        Returns:
            None
        """
        self.logger.info('Running numerical model.')

        self.core.solve_numerical_problems(
            solver=solver,
            verbose=verbose,
            **kwargs
        )

    def load_results_to_database(
        self,
        operation: str = 'update'
    ) -> None:
        """
        Loads the endogenous model results to a SQLite database. 

        Args:
            operation (str, optional): The operation to perform on the database.
                Defaults to 'update'.

        Returns:
            None
        """
        self.logger.info(
            'Exporting endogenous model results to SQLite database.')

        self.core.cvxpy_endogenous_data_to_database(operation)

    def update_database_and_problem(
            self,
            operation: str = 'update',
            force_overwrite: bool = False,
    ) -> None:
        """
        Updates the SQLite database and initializes problems. To be used in 
        case some changes in exogenous data have made, so that the SQLite 
        database and the problems can be updated without re-generating the
        Model instance.

        Args:
            operation (str, optional): The operation to perform on the 
                database. Defaults to 'update'.
            force_overwrite (bool, optional): Whether to force overwrite 
                existing data. Used for testing purpose. Defaults to False.

        Returns:
            None
        """
        self.logger.info(
            f"Updating SQLite database '{self.settings['sqlite_database_file']}' "
            "and initialize problems.")

        self.load_exogenous_data_to_sqlite_database(operation, force_overwrite)
        self.initialize_problems(force_overwrite)

    def generate_pbi_report(self) -> None:
        """
        This method generates the PowerBI report for inspecting input data
        and results of the numerical models. 

        Returns:
            None
        """
        self.logger.info(
            "Generating PowerBI report "
            f"'{self.settings['powerbi_report_file']}'.")

        self.pbi_tools.generate_powerbi_report()

    def erase_model(self) -> None:
        """
        Erases the model directory.
        This method deletes the directory containing all model files.

        Returns:
            None
        """
        self.logger.warning(f"Erasing model {self.settings['model_name']}.")

        self.files.erase_dir(self.paths['model_dir'])
