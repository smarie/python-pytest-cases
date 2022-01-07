#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-pyfields>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-pyfields/blob/master/LICENSE>
from pytest_cases import parametrize, parametrize_with_cases


class Person:
    def __init__(self, name):
        self.name = name


def get_tasks():
    return [Person("joe"), Person("ana")]


class CasesFoo:
    @parametrize(task=get_tasks(), ids=lambda task: task.name)
    def case_task(self, task):
        return task


@parametrize_with_cases("task", cases=CasesFoo)
def test_foo(task):
    print(task)
