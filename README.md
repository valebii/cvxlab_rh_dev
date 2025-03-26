# CVXlab

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Community](#community)
- [Citing](#citing)

## Introduction
CVXlab is a Python-embedded, open-source modeling framework able to generate and to solve convex numerical optimization problems.
The framework extends the functionalities of the cvxpy package in the following ways:
- It enables to express your problem in a natural way that follows the math, rather than in the restrictive standard form required by solvers. You can easily conceptualize numerical problem (sets, variables, symbolic equations) with an excel-based or yaml-based interface (no code experience requested). 
- It allows the generation and solution of multiple integrated optimization problems at the same time (allowing models integration or decomposition);
- It simplifies exogenous data input to the model based on excel, and it centralizes data management based on SQLite;

## Installation
To install the package, use:
```bash
pip install .
```

## Usage
Here's a brief example of how to use the package:
```python
import pyesm

# Define your problem
# ...example code...

# Solve the problem
# ...example code...
```
For more detailed usage instructions, please refer to the [Usage Guide](usage.rst).

## Examples
Here are some example scripts and notebooks demonstrating the usage of the package:
- [Example Script 1](examples/example_script1.py)
- [Example Script 2](examples/example_script2.py)
- [Example Notebook 1](examples/example_notebook1.ipynb)
- [Example Notebook 2](examples/example_notebook2.ipynb)

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Community
The CVXlab community consists of researchers, data scientists, software engineers, and students from all over the world. We welcome you to join us!

* To chat with the CVXlab community in real-time, join us on [Discord](https://discord.gg/4urRQeGBCr).
* To have longer, in-depth discussions with the CVXlab community, use [Github Discussions](https://github.com/your-repo/pyesm/discussions).
* To share feature requests and bug reports, use [Github Issues](https://github.com/your-repo/pyesm/issues).

Please be respectful in your communications with the CVXlab community, and make sure to abide by our [code of conduct](CODE_OF_CONDUCT.md).

## Citing
If you use CVXlab for academic work, we encourage you to cite our papers. If you use CVXlab in industry, we'd love to hear from you as well, on Discord or over email.




