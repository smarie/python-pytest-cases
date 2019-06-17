def pytest_configure(config):
    # change the option
    setattr(config.option, 'with_reorder', 'skip')
