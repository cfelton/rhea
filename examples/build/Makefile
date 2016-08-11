PYTHON=python


all: xilinx altera lattice

#########################################################
# Xilinx boards
#########################################################
xilinx: xula pone #atlys ufo400 

xula: #xilinx/xula.bit
	time $(PYTHON) ex_xula.py

#ufo400: #xilinx/ufo400.bit
#	$(PYTHON) ex_ufo400.py

pone: #xilinx/pone.bit
	time $(PYTHON) ex_pone.py

anvyl: #xilinx/anvyl.bit
	time $(PYTHON) ex_anvyl.py

mojo: #xilinx/anvyl.bit
	time $(PYTHON) ex_mojo.py

# atlys: #xilinx/atlys.bit
# 	$(PYTHON) ex_atlys.py

zybo: #xilinx/zybo.bit
	$(PYTHON) ex_zybo.py


# parallela: #xilinx/parallela.bit
# 	$(PYTHON) ex_parallela.py


#########################################################
# Altera boards
#########################################################
altera: de0nano #de0

de0nano: #altera/
	time $(PYTHON) ex_de0nano.py

de0cv: #altera/
	$(PYTHON) ex_de0cv.py

#de0nano_soc: #altera/
#	$(PTYHON) ex_de0nano_soc.py

#de1_soc: #altera/
#	$(PYTHON) ex_de1_soc.py

#de2cII: #altera/
#	$(PYTHON) ex_de2cII.py

#de0: #altera/
#	$(PYTHON) ex_de0.py


#########################################################
# Lattice boards
#########################################################
lattice: icestick

icestick:
	time $(PYTHON) ex_icestick.py 


#########################################################
clean:
	rm -Rf altera
	rm -Rf xilinx
	rm -Rf yosys
	rm -Rf iceriver
	rm -f *.log



