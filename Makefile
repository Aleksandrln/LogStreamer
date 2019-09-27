TEST = py.test $(arg)

test: cd test && $(TEST)
