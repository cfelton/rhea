
Hopefully a second (or third) set of eyes can point out the stupid 
mistake I am making.  In the process of migrating `rhea` to use the
lastest myhdl 1.0dev, specifically the `@myhdl.block` and methods I 
ran into a conversion issue.  The ~~module~~ block that failed to 
convert, I thought, was a simple dual-port RAM description.

Numerous odd things:

   1. The block converts with 0.9 py2.7 and py3.4 (there is another
      error with 3.5, will leave that for later).

   2. I am unable to reproduce the converison error in a sandbox 
      version (see below).

   3. The block passes a suite of test with python 3.5 fails 
      conversion with python 3.4 and python 3.5 (didn't test the
      migration in process version with python 2.7)

The [block I am trying to convert can be found in this link]().

Here is a modified version of the block, removing some of the 
functions I use in `rhea`.

<!-- fifo_mem -->
```python
```

The converted code is missing the declaration for the array in the 
Verilog and VHDL versions.

```python
memarray = [Signal(datatype) for _ in range(memsize)]
```

The `memarray` is not defined in the converted code but it is used.

At first I thought I stumbled upon a bug, I looked at the `test_ram.py`
code in myhd/test/conversion/general.  None of the existing models 
matched my block exactly, so I added a block hopeing it would reproduce
the error I was seeing in the myhdl test suite.

<!-- mode_mem -->
```python
```

This version passes just fine.  I am hoping someone will see the 
silly mistake I am making or some suggestions what to try next.
