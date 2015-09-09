PYTHON=python


all: xilinx altera

xilinx: xula pone #atlys ufo400 

xula: #xilinx/xula.bit
	time $(PYTHON) ex_xula.py

#ufo400: #xilinx/ufo400.bit
#	$(PYTHON) ex_ufo400.py

pone: #xilinx/pone.bit
	time $(PYTHON) ex_pone.py

#atlys: #xilinx/atlys.bit
#	$(PYTHON) ex_atlys.py

#zybo: #xilinx/zybo.bit
#	$(PYTHON) ex_zybo.py


#parallela: #xilinx/parallela.bit
#	$(PYTHON) ex_parallela.py

altera: de0nano #de0

de0nano: #altera/
	time $(PYTHON) ex_de0nano.py

#de2cII: #altera/
#	$(PYTHON) ex_de2cII.py

#de0: #altera/
#	$(PYTHON) ex_de0.py

clean:
	rm -Rf altera/*
	rm -Rf xilinx/*

