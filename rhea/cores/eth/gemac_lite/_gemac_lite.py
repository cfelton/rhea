
from myhdl import *



def m_simple_gemac(

    # ~~[ports]~~
    clock,    # 125 MHz
    reset,    # system reset

    gmii,     # GMII interface
    flow,     # flow control

    rxst,     # rx stream
    txst,     # tx stream 

    settings, # settings

    #~~[parameters]~~
    config=None
):
    """
    """

    SGE_IFG = 12   # 12 should be the absolute minimum


    grst1 = m_reset_sync(rxst.clk, reset, reset_rxclk)
    grst2 = m_reset_sync(txst.clk, reset, reset_txclk)

    # @todo: break out the gmii into gmii_tx and gmii_rx 
    gtx = m_simple_gemac_tx(clock, reset, 
                            gmii_tx, 
                            txst)

    grx = m_simple_gemax_rx(clock, reset,
                            gmii_rx,
                            rxst)

    gfl = m_flow_control()


    return grst1, grst2, gtx, grx, gfl