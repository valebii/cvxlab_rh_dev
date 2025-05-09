from typing import Tuple
import pytest


def run_test_cases(
        func: callable,
        test_cases: Tuple,
        **func_args,
) -> None:
    """
    Utility function to run a series of test cases for a given function.

    Each test case should be a tuple of the form:
        (input, expected_output, expected_exception)
    or
        (input, expected_output, expected_exception, func_kwargs)
    where:
        - input: The input to pass to the function under test.
        - expected_output: The expected result (if no exception is expected).
        - expected_exception: The exception type expected (or None).
        - func_kwargs: (optional) dict of keyword arguments for the function.

    Additional keyword arguments (**func_args) are passed to every function call,
    and are overridden by per-case func_kwargs if provided.

    Args:
        func (callable): The function to test.
        test_cases (tuple): List of test case tuples.
        **func_args: Additional keyword arguments for the function.

    Raises:
        AssertionError: If the function output does not match expected_output.
        Exception: If the function does not raise the expected_exception.
    """
    for case in test_cases:

        if len(case) == 3:
            text, expected, error = case
            func_kwargs = func_args
        else:
            text, expected, error, func_kwargs = case
            func_kwargs = {**func_args, **func_kwargs}

        if error:
            with pytest.raises(error):
                func(text, **func_kwargs)
        else:
            assert func(text, **func_kwargs) == expected
