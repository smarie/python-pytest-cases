# META
# {'passed': 1, 'skipped': 0, 'failed': 0}
# END META

def test_config(request):
    assert request.session.config.getoption('with_reorder') == 'skip'
