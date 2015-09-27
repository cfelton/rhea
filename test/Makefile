
TIME=time
LOG=output/run_all_tests.log

run:
	py.test

find: 
	grep "def .*test_" -R * --include=*.py | cat -n

test:
	rm -Rf output/
	mkdir output/
	$(TIME) python ./test_cores/test_converters/test_adc128s022.py > $(LOG)
	$(TIME) python ./test_cores/test_eth/test_gemac_lite.py >> $(LOG)
	$(TIME) python ./test_cores/test_fifo/test_afifo.py >> $(LOG)
	$(TIME) python ./test_cores/test_fifo/test_ffifo.py >> $(LOG)
	$(TIME) python ./test_cores/test_fifo/test_fifo_ramp.py >> $(LOG)
	$(TIME) python ./test_cores/test_fifo/test_sfifo.py >> $(LOG)
	$(TIME) python ./test_cores/test_sdram/test_sdram.py >> $(LOG)
	$(TIME) python ./test_cores/test_serio.py >> $(LOG)
	$(TIME) python ./test_cores/test_spi.py >> $(LOG)
	$(TIME) python ./test_cores/test_ticks.py >> $(LOG)
	$(TIME) python ./test_cores/test_video/test_create_image.py >> $(LOG)
	$(TIME) python ./test_cores/test_video/test_hdmi.py >> $(LOG)
	$(TIME) python ./test_cores/test_video/test_lt24lcd_driver.py >> $(LOG)
	$(TIME) python ./test_cores/test_video/test_lt24lcdsys.py >> $(LOG)
	$(TIME) python ./test_cores/test_video/test_vgasys.py >> $(LOG)
	$(TIME) python ./test_cosim/test_fpgalink/test_fpgalink.py >> $(LOG)
	$(TIME) python ./test_models/test_fx2_model.py >> $(LOG)
	$(TIME) python ./test_system/test_regfile.py >> $(LOG)


clean:
	rm -Rf output/
	rm -f *.vcd*
	rm -f *.v
	rm -f *.vhd
	rm -f *.txt
	rm -f *.log
	rm -Rf vcd/

