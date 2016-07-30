
##########################
``rhea`` common components
##########################

The ``rhea`` top-level namespace includes a small collection of
functions and objects that are commonly used in `building subblocks`_
(cores).  This is a thin-layer in the software stack used to build
complex digital systems.

.. _building subblocks: http://

The following is the list of the functions and objects in the rhea
top-level namespace.  See the information below for more details.

   #. rhea.Clock(init_val, frequency)
   #. rhea.Reset(init_val, active, async)
   #. rhea.Global()
   #. rhea.Constants(**named_constants)
   #. rhea.Signals(sigtype, num_sigs)
   #. rhea.syncro
   #. rhea.assign


.. autoclass:: rhea.Clock

.. autoclass:: rhea.Reset

.. autoclass:: rhea.Global

.. autoclass:: rhea.Constants

.. autofunction:: rhea.Signals

.. autofunction:: rhea.assign

.. autofunction:: rhea.syncro


Examples
========

