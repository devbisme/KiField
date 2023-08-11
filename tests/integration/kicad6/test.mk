PROG = kifield
FLAGS = -w -nb -d 1

test: test6 test7 test8
	@echo 'All tests passed!'
	@$(PROG) -v

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
	@python ../randomizer.py $@.csv $@.csv
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
	@python ../randomizer.py $@.csv $@.csv
    # Insert the random stuff back into the fields of the library.
	@$(PROG) -x $@.csv -i $@.kicad_sym $(FLAGS)
    # Extract the updated fields from the library into an XLSX file.
	@$(PROG) -x $@.kicad_sym -i $@.xlsx $(FLAGS)
    # Extract the contents of the XLSX file into a CSV file.
	@$(PROG) -x $@.xlsx -i $@1.csv $(FLAGS)
    # The extracted CSV file should match the randomized CSV file.
	@diff -qsw $@.csv $@1.csv
	@echo 'Test $@ passed!'

clean:
	@rm -f test[678]*.* *.bak
	@echo 'Cleanup complete.'
