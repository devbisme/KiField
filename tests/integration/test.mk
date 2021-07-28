PROG = kifield
#PROG = python -m ..\..\kifield
FLAGS = -w -nb -d 1

test: test1 test2 test3 test4 test5 test6 test7 test8 test9 test10 test11
	@echo 'All tests passed!'
	@$(PROG) -v

test1:
	@rm -f $@*.*
    # Copy the CAT schematic file.
	@cp CAT.sch $@.sch
    # Get the fields from the schematic into the CSV file.
	@$(PROG) -x $@.sch -i $@.csv $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
	@python randomizer.py $@.csv $@.csv
    # Insert the random stuff back into the fields of the schematic.
	@$(PROG) -x $@.csv -i $@.sch $(FLAGS)
    # Extract the updated fields from the schematic into an XLSX file.
	@$(PROG) -x $@.sch -i $@.xlsx $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the randomized CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test2:
	@rm -f $@*.*
    # Copy the hierarchical schematic file.
	@cp hier_test.sch $@1.sch
    # Extract the fields from the schematic into a CSV file.
	@$(PROG) -x $@1.sch -i $@.csv -r $(FLAGS)
    # Restore the fields from the CSV file back into the schematic.
	@$(PROG) -x $@.csv -i $@1.sch -r $(FLAGS)
    # Extract the schematic fields into an XLSX file.
	@$(PROG) -x $@1.sch -i $@.xlsx -r $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv -r $(FLAGS)
    # The extracted CSV file should match the original CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test3:
	@rm -f $@*.*
    # Copy the XESS library file.
	@cp xess.lib $@.lib
    # Extract the fields from the library into a CSV file.
	@$(PROG) -x $@.lib -i $@.csv $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
	@python randomizer.py $@.csv $@.csv
    # Insert the random stuff back into the fields of the library.
	@$(PROG) -x $@.csv -i $@.lib $(FLAGS)
    # Extract the updated fields from the library into an XLSX file.
	@$(PROG) -x $@.lib -i $@.xlsx $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the randomized CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test4:
	@rm -f $@*.*
    # Extract the fields from the library into a CSV file.
	@$(PROG) -x xess.lib -i xess.csv $(FLAGS)
    # Insert some DCM-type fields into the CSV file.
	@python insert_dcm.py xess.csv $@.csv
    # Make a copy of the library file.
	@cp xess.lib $@.lib
    # Insert the DCM fields into the library.
	@$(PROG) -x $@.csv -i $@.lib
    # Extract the fields from the library into a DCM file.
	@$(PROG) -x $@.lib -i $@.dcm $(FLAGS)
    # Extract the fields from the library and the DCM file into a CSV file.
	@$(PROG) -x xess.lib $@.dcm -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the original CSV file with added DCM fields.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test5:
	@rm -f $@*.*
    # Copy the hierarchical schematic file.
	@cp hier_test2.sch $@1.sch
    # Extract the fields from the schematic into a CSV file.
	@$(PROG) -x $@1.sch -i $@.csv -r $(FLAGS)
    # Restore the fields from the CSV file back into the schematic.
	@$(PROG) -x $@.csv -i $@1.sch -r $(FLAGS)
    # Extract the schematic fields into an XLSX file.
	@$(PROG) -x $@1.sch -i $@.xlsx -r $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv -r $(FLAGS)
    # The extracted CSV file should match the original CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test6:
	@rm -f $@*.*
    # Extract the fields from the schematic into a CSV file.
	@$(PROG) -x hierarchical_schematic.kicad_sch -i $@.csv -r $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
    # @python randomizer.py $@.csv $@.csv
    # Restore the fields from the CSV file back into the schematic.
	@$(PROG) -x $@.csv -i hierarchical_schematic.kicad_sch -r -w -d 1
    # Extract the schematic fields into an XLSX file.
	@$(PROG) -x hierarchical_schematic.kicad_sch -i $@.xlsx -r $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv -r $(FLAGS)
    # Restore the hierarchical schematic files.
	@cp -f hierarchical_schematic.kicad_sch.1.bak hierarchical_schematic.kicad_sch
	@cp -f leaf1.kicad_sch.1.bak leaf1.kicad_sch
	@cp -f leaf2.kicad_sch.1.bak leaf2.kicad_sch
    # The extracted CSV file should match the original CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test7:
	@rm -f $@*.*
    # Extract the fields from the schematic into a CSV file.
	@$(PROG) -x random_circuit.kicad_sch -i $@.csv -r $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
	@python randomizer.py $@.csv $@.csv
    # Restore the fields from the CSV file back into the schematic.
	@$(PROG) -x $@.csv -i random_circuit.kicad_sch -r -w -d 1
    # Extract the schematic fields into an XLSX file.
	@$(PROG) -x random_circuit.kicad_sch -i $@.xlsx -r $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv -r $(FLAGS)
    # Restore the schematic files.
	@cp -f random_circuit.kicad_sch.1.bak random_circuit.kicad_sch
    # The extracted CSV file should match the original CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test8:
	@rm -f $@*.*
    # Copy the library file.
	@cp Amplifier_Video.kicad_sym $@.kicad_sym
    # Extract the fields from the library into a CSV file.
	@$(PROG) -x $@.kicad_sym -i $@.csv $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
	@python randomizer.py $@.csv $@.csv
    # Insert the random stuff back into the fields of the library.
	@$(PROG) -x $@.csv -i $@.kicad_sym $(FLAGS)
    # Extract the updated fields from the library into an XLSX file.
	@$(PROG) -x $@.kicad_sym -i $@.xlsx $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the randomized CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test9:
	@rm -f $@*.*
    # Copy the CAT schematic file.
	@cp CAT.sch $@.sch
    # Get the grouped fields from the schematic into the CSV file.
	@$(PROG) -g -x $@.sch -i $@.csv $(FLAGS)
    # Make a copy of the grouped fields.
	@cp $@.csv $@1.csv
    # Extract the grouped fields and add them to the copy.
	@$(PROG) -g -x $@.sch -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the initial CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test10:
	@rm -f $@*.*
    # Copy the CAT schematic file.
	@cp CAT.sch $@.sch
    # Get the grouped fields from the schematic into the CSV file, no ranges
	@$(PROG) -g -nr -x $@.sch -i $@.csv $(FLAGS)
    # Make a copy of the grouped fields.
	@cp $@.csv $@1.csv
    # Extract the grouped fields and add them to the copy.
	@$(PROG) -g -nr -x $@.sch -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the initial CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

test11:
	@rm -f $@*.*
    # Copy the CAT schematic file.
	@cp CAT.sch $@.sch
    # Get the grouped (no ranges) fields from the schematic into the CSV file.
	@$(PROG) -g -nr -x $@.sch -i $@.csv $(FLAGS)
    # Add some random columns of random stuff to the CSV file.
	@python randomizer.py $@.csv $@.csv
    # Insert the random stuff back into the fields of the schematic.
	@$(PROG) -x $@.csv -i $@.sch $(FLAGS)
    # Extract the updated grouped (no ranges) fields from the schematic into an XLSX file.
	@$(PROG) -g -nr -x $@.sch -i $@.xlsx $(FLAGS)
    # Extract the grouped (no ranges) contents of the XLSX file into a CSV file.
	@$(PROG) -g -nr -x $@.xlsx -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the randomized CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'


clean:
	@rm -f test[1-11]*.* *.bak
	@echo 'Cleanup complete.'
