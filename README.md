# Mandelbrot on MVS 3.8j

## Introduction

## Running

## Quick File List

### Core Code

* **PRTMAND** Top level. Calculates the Mandelbrot set and prints and image of it.
* **MANDEL** Macro to determine if a point is in the Mandelbrot set.
* **DMAND** Data storage for the MANDEL macro.
* **MANONE** Calculates a single iteration of the Mandelbrot set.
* **DMO** Data storage for the MANONE macro.
* **CLMAG** Macro to calculate the square of the magnitude of a complex number.
* **CRDTRAN** Macro to do 1D coordinate tranformation.
* **CRDINIT** Initializes 1D coordinate transform.
* **PUTC** Inserts a character into a memory location.

### Standard Operation

* **run** Submits the assemble and run job over network punch reader.
* **MANJOB** The job to assemble and run the program.

### Debug Operation

* **ran** Submits the debug job over network punch reader.
* **MANASM** First part of job JCL, calls the assembler. Immediately after this is the inlined assembly program.
* **MANASE** Last part of job JCL. Calls the assembled code with the SYSUDUMP dataset defined to output a dump on abend.
