# Mandelbrot on MVS 3.8j

## Introduction

This codebase is aimed at printing a representation of the Mandelbrot set in MVS 3.8j implemented in assembly. There
is an [output run](docs/mandelbrot-output.pdf) that shows the results.

## Running

You'll need an install of MVS, probably through the [Hercules](https://www.hercules-390.eu/) emulator. I did most of my
development through Juergen Winkelmann's [TK4-](https://wotho.pebble-beach.ch/tk4-/) system. The current version I am running
via Rob Prins' [TK5](https://www.prince-webdesign.nl/index.php/software/mvs-3-8j-turnkey-5) system.

I should also note that Jay Moseley's [website](https://www.jaymoseley.com/hercules/) has also been very helpful in navigating
the entire system and its environment.

Once you have a machine up and running. The `/run` command should be able to post a remote job over the punch reader.

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
