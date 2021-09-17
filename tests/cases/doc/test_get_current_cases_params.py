from pytest_cases import parametrize, parametrize_with_cases, fixture, get_current_params, get_current_cases


@fixture
@parametrize(FP_simple=('john',))
def fixa(FP_simple):
    return 0, FP_simple


@parametrize(CP_simple=('joe',))
def case_casea(CP_simple, fixa):
    return CP_simple


@parametrize_with_cases("CP_acase", cases=case_casea, idstyle="explicit")
def case_caseb(CP_acase):
    return CP_acase


@fixture
@parametrize_with_cases("FP_acase", cases=".", idstyle="explicit")
def fixb(FP_acase):
    return FP_acase


i = 0


@parametrize(TP_direct=(0,))
@parametrize_with_cases("TP_acase", cases=".", idstyle="explicit")
def test_foo(TP_acase, TP_direct, fixb, request):
    global i
    i += 1
    current_cases = get_current_cases(request)
    if i == 1:
        assert current_cases == {
            "TP_acase": ("casea", case_casea, {"CP_simple": "joe"}),
            "fixb": {
                "FP_acase": ("casea", case_casea, {"CP_simple": "joe"}),
            }
        }
    elif i == 2:
        assert current_cases == {
            "TP_acase": ("casea", case_casea, {"CP_simple": "joe"}),
            "fixb": {
                "FP_acase": ("caseb", case_caseb, {"CP_acase": ("casea", case_casea, {"CP_simple": "joe"})}),
            }
        }
    elif i == 3:
        assert current_cases == {
            "TP_acase": ("caseb", case_caseb, {"CP_acase": ("casea", case_casea, {"CP_simple": "joe"})}),
            "fixb": {
                "FP_acase": ("casea", case_casea, {"CP_simple": "joe"}),
            }
        }
    elif i == 4:
        assert current_cases == {
            "TP_acase": ("caseb", case_caseb, {"CP_acase": ("casea", case_casea, {"CP_simple": "joe"})}),
            "fixb": {
                "FP_acase": ("caseb", case_caseb, {"CP_acase": ("casea", case_casea, {"CP_simple": "joe"})}),
            }
        }
