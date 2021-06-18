# Figuring out abend

## Initial

Abend 0C1
For lots of things
Put in WTO statements
Appears to be in call to OPEN
Tried many DCB changes to no avail

## Dump

Can add SYSUDUMP to job step to generate a dump
Following [Analysis Procedure](https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.2.0/com.ibm.zos.v2r2.ieav100/iea3v1_Analysis_Procedure.htm)

1. Collect and analyze logrec records

The problem is in my code.

2. Collect and analyze messages about the problem.

Ditto.

3. Analyze the dump as in following steps.

4. Obtain abend code, reason code, job name, step name, and program status word (PSW)

Abend 0C1
System
Job   PRTMAND
Step  GO
PSW   078D0000 00000026

First 32
            1   1   2   2   2   3
0   4   8   2   6   0   4   8   2
00000111100011010000000000000000

Second 32
3   3   4   4   4   5   5   6   6
2   6   0   4   8   2   6   0   4
00000000000000000000000000100110

Bit 12 (from left?) = 1
EC Mode

Program-Event-Recording Mask (R) (bit 1) = 0
Translation Mode (T) (Bit 5): 1 (address translation enabled)
I/O Mask (IO) (Bit 6): 1 (I/O enabled)
External Mask (E) (Bit 7): 1 (external interrupts enabled)
Protection Key (Bit 8-11): 1000 (protection key for storage)
Extended-Control Mode (Bit 12): 1 (check)
Machine-Check Mask (M) (Bit 13): 1 (machine check interrupts enabled)
Wait State (W) (Bit 14): 0 (in running state)
Problem State (P) (Bit 15): 1 (in problem state)
Condition Code (CC) (Bit 18,19): 00 (condition code)
Program Mask (Bit 20-23): 0000 (no interruptions from overflow)
Instruction Address (Bit 40-63): 000000000000000000100110 (26 hex) location of left-most byte of next instruction
0,2-4,16-17,24-39 should be 0: check

5. Analyze the RTM2WA (Recovery Termination Manager 2 Work Area)

    * In the TCB summary, find the TCB (Task Control Block) for the task.
      Completion code in CMP field. Obtain TCB address from RTM2WA

      CMP 900C1000
      TCB Address 99DA58

    * In the RTM2WA summary, obtain the registers and address of program
      Registers elided.
      Program address: 0

    * If the RTM2WA summary does not give program name and address, probably an SVC instruction
      abnormally ended.
      No name or address: SVC?

    * If RTM2WA gives address of RTM2WA ....
      Not the case here

6. Analyze the dump for the program name, if the name field is zero, do the following

    * Find the control blocks for the task being dumped
