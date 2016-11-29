#PROG = python -m ..\kifield
PROG  = kifield
FLAGS = -w -nb -d 1

test: test1 test2 test3 test4
	@echo 'All tests passed!'
	@$(PROG) -v

test1:
	@rm -f $@*.* 
	@cp cat.sch $@.sch
	@$(PROG) -x $@.sch -i $@.csv $(FLAGS)
	@python randomizer.py $@.csv $@.csv
	@$(PROG) -x $@.csv -i $@.sch $(FLAGS)
	@$(PROG) -x $@.sch -i $@.xlsx $(FLAGS)
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test2:
	@rm -f $@*.* 
	@cp hier_test.sch $@1.sch
	@$(PROG) -x $@1.sch -i $@.csv -r $(FLAGS)
	@$(PROG) -x $@.csv -i $@1.sch -r $(FLAGS)
	@$(PROG) -x $@1.sch -i $@.xlsx -r $(FLAGS)
	@$(PROG) -x $@.xlsx -i $@1.csv -r $(FLAGS)
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test3:
	@rm -f $@*.*
	@cp xess.lib $@.lib
	@$(PROG) -x $@.lib -i $@.csv $(FLAGS)
	@python randomizer.py $@.csv $@.csv
	@$(PROG) -x $@.csv -i $@.lib $(FLAGS)
	@$(PROG) -x $@.lib -i $@.xlsx $(FLAGS)
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test4:
	@rm -f $@*.*
	@$(PROG) -x xess.lib -i xess.csv $(FLAGS)
	@python insert_dcm.py xess.csv $@.csv
	@cp xess.lib $@.lib
	@$(PROG) -x $@.csv -i $@.lib 
	@$(PROG) -x $@.lib -i $@.dcm $(FLAGS)
	@$(PROG) -x xess.lib $@.dcm -i $@1.csv $(FLAGS)
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

clean:
	@rm -f test1*.* test2*.* test3*.* test4*.*
	@echo 'Cleanup complete.'
