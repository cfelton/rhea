

Memory mapped interfaces
========================

Base classes
------------
The following are the building blocks for defining a system with
memory-mapped attributes.

.. autoclass:: rhea.system.MemorySpace

.. autoclass:: rhea.system.MemoryMapped
    :members:

.. autoclass:: rhea.system.MemoryMap

.. autoclass:: rhea.system.RegisterFile


Memory mapped buses
-------------------
The following are the memory-mapped bus interfaces available
in rhea.

.. toctree::
   :maxdepth: 1

   barebone
   wishbone
   avalon
   axi4
