# MC3 Modder:

**MC3 Modder** is an all-in-one desktop utility
engineered in Python and Tkinter designed to
completely streamline and automate the extraction,
decompilation, and repackaging of game assets for
Midnight Club 3 Dub Edition. By providing a
responsive, asynchronous GUI layout over low-level
Python scripts, it eliminates tedious command-line
workflows and enables effortless game modding.

# Key Features & Modules:
## N°1 Integrated File Storage Explorer:
Multi-column, color-coded item browsing hierarchy
mapping folder trees dynamically. Double-click
directory navigation paired with quick parent-level
traversal. Runs out-of-the-box targeting local project 
source locations directly.

## N°2 Dave File Manager:
**Extract:** Unpacks massive core game asset
archives *(e.g., Assets.dat)* into customized asset
folders.

**Repack:** Encodes updated structural asset
directories securely back into game-ready binary
layouts with highly specific compilation
configurations.

## N°3 Hash Manager:
Extracts and builds specialized data stream tables
such as *Stream.dat*.

Synchronized directly with PS2 stream manifests
***(MC3_PS2_Streams.lst)*** to verify pointer allocations
accurately.

Automated pipeline processing using multithreaded
threshold assignments.

## N°4 STRTBL String Matrix Converter:
**Decompile:** Converts binary game text containers
***(.strtbl)*** into clean, structured, human-readable .json
data files.

**Compile:** Re-encodes modified text string
adjustments back into binary pointer structures
compatible with the game's original engine.

## N°5 Audio Converter (RSTM) Control Deck:

Converts custom music tracks and audio blocks
directly into native **Rockstar RSTM .rsm** archive
formats.

**Wide Format Ingestion:** Handles raw audio files
(.mp3, .wav, .flac, .ogg) alongside specialized console
rips ***(.genh, .fsb, .ss2, .ads, .rws, .snd).***

**Execution Options:** Supports custom injection
properties like audio looping **(--loop-full),** forced
output overrides **(--overwrite),** and testing
simulation runs **(--dry-run).**

# Stability & Safety Systems:

**Asynchronous Threading Model:** Subprocesses run
inside dedicated background execution contexts,
keeping the GUI fast and perfectly responsive
throughout heavy asset loads.

**Smart Routing Verification:** Prevents unintended
data loss by prompting choices to safely skip
processing, authorize overwrites, or abort
operations when duplicate outputs are detected.  

**Live Pipeline Execution Logs:** Offers an integrated
console monitoring interface displaying low-level
terminal telemetry logs in real time.

**Small Advices**: Make backups, that always the best way
to recover your old files if an issue appears
trust me. I also recommend you to put all the files in
the ***"Workspace"*** folder to make life easier for you.


# Prerequisites & Dependencies:

**The last version of Python**: You don't lose anything
to install the last version of python, and even if you
might be using a goofy old computer, you can still
find newer versions compatible with Windows 7.

**Tkinter module**: Literally, the second core of this
app, it is with it that you are able to get the graphic
interface.

**System Modding Scripts**: I have included them in
the ***tools*** folder. **Don't touch them.**.

**Additional Things**: *psxavenc, vgmstream, ffmpge
and ffprobe* **must** be installed to be able to convert
to the .rsm format.

# Credits:

You'll find them included in the tool.

***Copyright • The MC3 modding community • No
rights reserved :)***