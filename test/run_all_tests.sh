#!/usr/bin/env bash

# run all the tests
/usr/bin/time python ./test_cores/test_converters/test_adc128s022.py > output/run_all_tests.log
/usr/bin/time python ./test_cores/test_eth/test_gemac_lite.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_fifo/test_afifo.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_fifo/test_ffifo.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_fifo/test_fifo_ramp.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_fifo/test_sfifo.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_sdram/test_sdram.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_serio.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_spi.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_ticks.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_video/test_create_image.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_video/test_hdmi.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_video/test_lt24lcd_driver.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_video/test_lt24lcdsys.py >> output/run_all_tests.log
/usr/bin/time python ./test_cores/test_video/test_vgasys.py >> output/run_all_tests.log
/usr/bin/time python ./test_cosim/test_fpgalink/test_fpgalink.py >> output/run_all_tests.log
/usr/bin/time python ./test_models/test_fx2_model.py >> output/run_all_tests.log
/usr/bin/time python ./test_system/test_regfile.py >> output/run_all_tests.log

