Let's flesh out a plan:

# End goal

CircuitPython stack runnable on the BPI-Bit-S2 with to do the `/Users/alex/Development/Isana/LightTower-challenge`
As a PoC to show the working of the software stack (to be build), we want to have the LightTower-challenge implemented and running. 


## Specifics

Experiments with be human conducted. You write the software. This is a Poc, we want to demonstrate doability, not deliver production code. But the code on the library level should be upgradable to production level quality with moderate effort. Keep detailed records of open todo's. The code descibes the current working/state of the algorithms, optionally including todos for _future_ outstanding work or improvment thoughs. History of  past chagnes is stored in Git. You can commit to working branches coarsely, whenever a larger chunk of work has been achieved or is starting to go revision phases. Document learnings and reasoning for past changes in separate `ai-notes` folder (structure your own notes, create subrirectories where benefitting structure to incorporate aspect covered by multiple files).

### Set-up

Set up `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX` as a circuitpython project (use `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040` as a template)


* we are working inside Cursor IDE version 3.18.25 with CircuitPythonSync extension version 2.2.2 (https://github.com/padgettholdings/circuitpythonsync) on MacOS x 26.6 with custom scripts for some aspects (please research past notes and your memory)
* use stock CircuitPython 10.3.0 for BPI-Bit-S2  https://circuitpython.org/board/bpi_bit_s2/
* If you need a local python, use `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`

### Important aspects
* we want to focus on asynchronous programming

### First Major milestone:

#### An asynchronous LED matrix library:

We'll use `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040` (unfinished) as a template

Copy the custom display library from `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040` and install dependencies  to the appropriate subfolders of `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX`. We work on the copy. 

- we need to adpat it to 5x5 LEDs, limit brightness to 20% of max possible (hardcoded constant in library)
- adjust library such that certain files can be replaced by different ones to witch back to 8x8 matrix (possebly also needing to adjust the coordinate Look-Up Table [LUT] - see `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/lib/display` for further reading). For physical orientation of 5x5 Matrix in BPI-Bit-S2 see `/Users/alex/Desktop/sort/2026-01 Exp02 BPI-Bit-S2 CircuitPython Exploration` and `/Users/alex/Development/VsCode/CircuitPython/2026-02_Exp09_BPI-Bit-S2-LED-Matrix`
- try to figure out what pictograms the Microbit offers (I think we might have analyzed that in some past conversations)
- we need a proper font that displays well on a 5x5 LED. I find the compromized that the microbit MakeCode makes quite good.


#### An asynchronous Button library 
* we have done some brainstorming in with the following rough sketch of a tutorial: `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/Notes/Button_chat.md` (we could try to implement that)
* or we can follow `/Users/alex/Development/VsCode/CircuitPython/CodingTutor/mini-project-scatches/button-library.md` 

Please analyse, make a detailed plan and distill a recommendation


## Working preferences

* keep internal working notes
   - consult `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` for guidelines and best practises 
   - work with the human user on a conceptually higher-level using generalizations, abstractions, simplifications (consult `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` for for guidelines and best practises)
* maintain a detailed plan for cold-AI (see `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/cold-ai-paradigm.md`) tailored for AI consumption
   - discuss the plan with me on a conceptually higher-level using generalizations, abstractions, simplifications so I don't have to go through the low level detailed steps (consult `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` for for guidelines and best practises)
   - use adaptive planning disciple (and looped plan refinement protocol) - for details see `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` 
 * don't change my working setup without explicit permission, you are allowed to install/use up to 5 extra scripts that you design and maintain if you have informed me about it, are sure those scripts are not harmful for my dev machine, easily revertable / removable. Track all changes you made for installing the scirpts and how to remove them in detailed notes (in `ai-notes` folder). Be cautious and responsible with my working environment. Maintain a precise spec for the scripts so you know at any time what they are supposed to do. Follow pragmatically the "Do one thing and do it well" philosophy with your shell scipt. If in doubt, ask - shell scripts are a very powerfull tool. 

* do not execute distructive operations allowed without explicity approval from the human user (silence not enough) - consult `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` (something should be in there, if not flag)  

### Next steps:

Analyze the situation and collect all relevant knowledge (digests + references, working draft of most relevant core pieces to entire copy of display library to evolve). In the process structure and maintain and optimize  `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes` as information store that covers everything from task to working notes of most recent code and collected learnings on the way. Content in `ai-notes` should be optimized for cold-AI retrievability and discoverability and reasonably self-contained (including full path/file references to other adjacent or related materials or code bases for further reading). 

* analyze the requirements, lets try to align on open questions and unclear aspects with the goal that you can then independently work on a first PoC of the first interim milestone independenty (over night)
* lets aim for a subsequent phase of testing the setup so we can believe you can operate and iterate independently if possible (this might not work if the BPI-Bit-S2 get's stuck and requires physical restart or reset - that is ok)


At all stages, check and track progress, be adaptive and try to autonomously address hurdles without installing stacks of extra stoftware. Plan for rare, but strategically valuable stages for focused human testing. 

