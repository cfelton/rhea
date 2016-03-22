
.PHONY: test
test:
	cd test && py.test -x --durations=7
	cd examples && py.test -x --durations=3

