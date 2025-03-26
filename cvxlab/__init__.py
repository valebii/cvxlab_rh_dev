"""
cvxlab - A Python-embedded, open-source modeling framework able to generate and 
to solve convex numerical optimization problems.
===============================================================================

The package is a Python-embedded, open-source modeling framework able to generate
and to solve convex numerical optimization problems. The package is designed to
provide a high-level interface to the user, allowing to specify the optimization
problem in a natural way, without the need to deal with the low-level details of
the solvers. The package is based on the CVXPY modeling language, and it is
compatible with the CVXPY solvers.

"""

# Import necessary modules and submodules
from cvxlab.backend.model import Model
from cvxlab.support.model_directory import (
    create_model_dir,
    transfer_setup_info_xlsx,
    handle_model_instance
)
from .version import __version__

# Metadata
__authors__ = "'Matteo V. Rocco'"
__collaborators__ = "'Lorenzo Rinaldi', 'Debora Ghezzi', 'Valeria Baiocco', 'Emanuela Colombo'"
__license__ = "Apache License 2.0"

# Initialization code (if any)
