
In the ``rhea`` package there are numerous functions,
~~modules~~ blocks, and objects that are used to develop a core.
The following is a list of the most commonly used.

..  make each of these available in the rhea global space ??

Core development
================

.. autoclass:: rhea.system.Global

.. autoclass:: rhea.system.Clock

.. autoclass:: rhea.system.Reset

.. autofunction:: rhea.system.Signals

.. autoclass:: rhea.system.ControlStatusBase

Memory-mapped interfaces

Streaming interfaces

.. autofunction:: rhea.cores.misc.assign

.. autofunction:: rhea.cores.misc.syncro


Test Development
================

.. autofunction:: tb_args

.. autofunction:: tb_default_args

.. autofunction:: run_testbench

