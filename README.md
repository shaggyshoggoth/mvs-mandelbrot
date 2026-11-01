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

### Support Code

### Standard Operation

* **run** Submits the assemble and run job over network punch reader.
* **MANJOB** The job to assemble and run the program.

### Punch Operation

* **punch** Submits the punch job over network punch reader. Generates punch card output for the source and assembled programs.
* **MANPCH** First part of punch job. Copies the inlined source job deck (MANJOB plus the program) to the card punch.
* **MANPCA** Last part of punch job. Assembles the program, punches the object deck.
* **tools/cards.py** Renders a punched EBCDIC deck as card images.
* **docs/cards/** Output of the above steps.

*NOTE* The card punch can be a bit persnickety. Run `devinit 00D pch/mandel.pch` to switch to EBCDIC, then `/$S PUN1` to start the punch device.

JES2 punches a blank card after each deck. Afterwards, `devinit 00D pch/pch00d.txt ascii` restores the punch (this empties that file).

### Debug Operation

* **run-dump** Submits the debug job over network punch reader.
* **MANASM** First part of job JCL, calls the assembler. Immediately after this is the inlined assembly program.
* **MANASE** Last part of job JCL. Calls the assembled code with the SYSUDUMP dataset defined to output a dump on abend.
* **MANAST** Unused alternative to MANJOB for the ASSIST assembler.
