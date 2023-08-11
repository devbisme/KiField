PROG = kifield

test: test_v5 test_v6 test_v7
	@echo 'All tests passed!'
	@$(PROG) -v

test_v5:
	make -C kicad5 -f test.mk

test_v6:
	make -C kicad6 -f test.mk

test_v7:
	make -C kicad7 -f test.mk

clean:
	@rm -f test[0-9]*.* *.bak
	make -C kicad5 -f test.mk clean
	make -C kicad6 -f test.mk clean
	make -C kicad7 -f test.mk clean
	@echo 'Cleanup complete.'
