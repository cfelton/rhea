
TIME=$(shell which time)
LOG=output/run_all_tests.log

ifndef PYTHON
	PYTHON=python
endif

run:
	$(TIME) py.test

find: 
	grep "def .*test_" -R * --include=*.py | cat -n

# There is an issue where the pytest runner takes 10x to execute
# the tests listed below.  Each test file calls the individual tests.
# This is undersired because it is a maintanence pain, need to resolve
# the pytest issue.
test:
	rm -Rf output/
	mkdir output/
	$(TIME) $(PYTHON) ./test_cores/test_converters/test_adc128s022.py > $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_eth/test_gemac_lite.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_fifo/test_afifo.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_fifo/test_ffifo.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_fifo/test_fifo_ramp.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_fifo/test_sfifo.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_sdram/test_sdram.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_serio.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_spi/test_spi.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_spi/test_spi_cso_config.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_ticks.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_video/test_create_image.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_video/test_hdmi.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_video/test_lt24lcd_driver.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_video/test_lt24lcdsys.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cores/test_video/test_vgasys.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_cosim/test_fpgalink/test_fpgalink.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_models/test_fx2_model.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_system/test_regfile.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_system/test_regfile_api.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_system/test_memmap.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_system/test_to_generic.py >> $(LOG)
	$(TIME) $(PYTHON) ./test_system/test_streamers.py >> $(LOG)


clean:
	rm -Rf output/
	rm -f *.vcd*
	rm -f *.v
	rm -f *.vhd
	rm -f *.txt
	rm -f *.log
	rm -Rf vcd/
	rm -f *.o
	rm -f *.pyc


