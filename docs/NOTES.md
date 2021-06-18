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

