# Mandelbrot in S370 Assembly

## Background

## Environment

* Jurgen Winkelmann TK4- System
    * http://wotho.ethz.ch/tk4-/
    * MVS 3.8j
    * Hercules 4.0 emulator
    * Minor changes? (3270 operator and user consoles only)

## Learning journey

* Setup
* Playing around
    * TSO Commands (docs/where do they come from)
    * RPF
    * Creating files
    * JCL
    * Submitting jobs
    * Admin duty (clearing logs)
* Failing to recover from crashes
* Tapes/disks/etc.
* System generation

## Deciding what to do

* What do I want to create?
* Random wikipedia mandlebrot on mainframe
* Decisions
    * Implement this from scratch
    * Assembly because I don't want to deal
      with Fortran/COBOL

## Development Journey

* Pieces (implementing bits of code at a time)
* Using RPF
* Delay
* Restart
* Submitting code via TCP card reader
* Documentation overload
* Basic implementation
* Assembled product
* Debug nightmare

## Debug

* Abend code is useless
* Poked at simpler
* Found out how to get more debug info
* Interpretation?
* Ok, found an example [here](http://www.edwardbosworth.com/My3121Textbook_HTM/MyText3121_Ch02_V02.htm)
    * Inserted DCB for printer verbatim, chaning DDNAME
    * SOC1
    * Changed PRINT => PRINTER
    * SOC1
    * Added SAVEAREA DD and lines between SAVE (14,12) and OPEN:
        ```
         BALR  12,0                   ESTABLISH                       
         USING *,12                   ADDRESSABILITY                  
         LA    2,SAVEAREA             ADDRESS OF MY SAVE AREA         
         ST    2,8(,13)              FORWARD CHAIN MINE               
         ST    13,SAVEAREA+4          BACKWARD CHAIN CALLER'S         
         LR    13,2                  SET 13 FROM MY SUB CALLS        
        ```
    * SO13: Progress!!
    * Changed LRECL in DCB to 121
    * Ok! Now we're getting past OPEN!
    * Determine what exactly this does and why.
* Now failing on STC in PUTC
* Moved top of code around (got rid of USING PRTMAND,15 - changing to just USING for register 12)
* After poking around for a while with compilation errors around STC, inlined the macro. Seems
  the macro syntax I'm using is incorrect. It's just a three-instruction thing so I'll ignore it.
* Now, getting S0CC which is an exponent overflow exception. Cool, at least something mathy is
  hapenning.
* `S` and `ST` were confused in `MANDEL`. The intended operation was to store. See `GA22-7000`
* Changed `PL4` to `F` for alignment issues - see `GC33-4010`
* Changed `CRDINIT` logic to compute `y0 -m*x0`
* Changed `MANDEL` to reset `z` to `0` after each point.
* Changed `MANONE` because it was negating the imaginary part.
* Changed `PRTMAND` because the termination condition never occurred.
* Changed plot bounds to -2.1..0.6 x -1.125..1.125 on a 120x61 grid to fill the page better.
