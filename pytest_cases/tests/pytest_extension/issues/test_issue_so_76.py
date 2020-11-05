# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
import pytest_cases

doubles = [0.0, -1.0, 1.0]
char_strings = ['"s"', '"_"']
c_identifiers = ['_', '_c']


class DummyClass(object):
    def __init__(self, *args, **kwargs):
        """
        Initialize this function.

        Args:
            self: (todo): write your description
        """
        self.args = args


@pytest_cases.fixture_plus()
@pytest.mark.parametrize('double', doubles)
@pytest.mark.parametrize('char_string', char_strings)
def value_table_description(double, char_string):
    """
    Return a formatted description.

    Args:
        double: (todo): write your description
        char_string: (str): write your description
    """
    return '{} {}'.format(double, char_string), DummyClass(double, char_string)


@pytest_cases.fixture_plus()
@pytest.mark.parametrize('value_table_name', c_identifiers)
@pytest.mark.parametrize('value_descriptions_count', [1, 2])
@pytest_cases.parametrize_plus('value_description_0', [pytest_cases.fixture_ref('value_table_description')])
@pytest_cases.parametrize_plus('value_description_1', [pytest_cases.fixture_ref('value_table_description')])
def value_table(value_table_name, value_descriptions_count, value_description_0, value_description_1):
    """
    Builds a table table.

    Args:
        value_table_name: (str): write your description
        value_descriptions_count: (str): write your description
        value_description_0: (str): write your description
        value_description_1: (str): write your description
    """
    value_description_0_string, value_description_0_value = value_description_0
    value_description_1_string, value_description_1_value = value_description_1
    value_descriptions_string = [value_description_0_string, value_description_1_string][:value_descriptions_count]
    value_descriptions_value = [value_description_0_value, value_description_1_value][:value_descriptions_count]
    return ('VAL_TABLE_ {} {} ;'.format(value_table_name, ' '.join(value_descriptions_string)),
            DummyClass(value_table_name, value_descriptions_value))


@pytest_cases.fixture_plus()
@pytest.mark.parametrize('value_tables_count', [1, 2])
@pytest_cases.parametrize_plus('value_table_0', [pytest_cases.fixture_ref('value_table')])
@pytest_cases.parametrize_plus('value_table_1', [pytest_cases.fixture_ref('value_table')])
def value_tables(value_tables_count, value_table_0, value_table_1):
    """
    Return the number of tables.

    Args:
        value_tables_count: (str): write your description
        value_table_0: (todo): write your description
        value_table_1: (todo): write your description
    """
    value_table_0_string, value_table_0_value = value_table_0
    value_table_1_string, value_table_1_value = value_table_1
    value_tables_string = '\n'.join([value_table_0_string, value_table_1_string][:value_tables_count])
    value_tables_value = [value_table_0_value, value_table_1_value][:value_tables_count]
    return value_tables_string, DummyClass(value_tables_value)


@pytest_cases.parametrize_plus('vts', [pytest_cases.fixture_ref('value_tables')])
def test_value_tables_node(vts):
    """
    Test if a node exists.

    Args:
        vts: (todo): write your description
    """
    # value_table_string, value_table_value = vts
    # p = DummyClass(value_table_string)
    # assert isinstance(p.ast.value_tables, list)
    # assert p.ast.value_tables[0] == value_table_value
    pass


def test_synthesis(module_results_dct):
    """
    Test if the results of the results.

    Args:
        module_results_dct: (todo): write your description
    """
    assert len(module_results_dct) == len([1, 2]) * len(c_identifiers) * len([1, 2]) * len(char_strings) * len(doubles)
