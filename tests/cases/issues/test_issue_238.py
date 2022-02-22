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
