# Lessons from the work — a case book for the hands

Each case here happened. What went wrong is told plainly, then what to do. The short rules that follow
from them are in `data/spine/distilled.md`, which you are given at the start of every run; come here
when a rule is not enough and you want the case behind it.

The head (the agent Kevin works with) adds a case when the work teaches one. Whether the teaching
reaches you is measured, not assumed: `python tools/apprentice_bench.py`.

## Shipping

**The commit that went ahead of its test.** The title of a window was reworded. A test still expected
the old words. The commit was amended before the test result was read, so for a few minutes the branch
held a commit with a failing test. *Do:* run the tests, read the last lines of the result, then commit.
If you chain the two in one command, the commit must depend on the tests passing.

**Line ends on a new file.** A new JSON file was written with Windows line ends into a tree that keeps
Unix ones. It was caught and put right before the push, by looking. *Do:* before you commit a new file, look at what line
ends its neighbours use and match them. When you add to a file, keep the line ends it already has
(`tools/neutron_note.py` does this for the inbox).

**A patch that is counted.** Changing a file by "find this, put that" goes wrong silently when the text
is there twice or not at all. *Do:* count the matches first. One expected, one found: change it. Any
other count: stop and read the file again. `edit_file` refuses a text that matches more than once for
this reason; do not get around it with `replace_all` unless every match is meant.

**Other hands in the same tree.** `git status` often shows changed files that are not yours: another
agent's work in progress, a record a running service keeps writing. *Do:* add your own files by path.
Leave the rest exactly as it is, and say in your summary that you left it.

**When the forge is away.** The house forge lives on eastGate. When eastGate is off, a push fails and
some git commands wait a long time for an answer that will not come. *Do:* keep working and committing
here, write down what still has to go out and in which order, and push when the forge answers again.
Do not push somewhere else instead unless Kevin says so.

**A tree can be clean while its history is not.** What a file said three commits ago still travels with
the branch. *Do:* before a line of commits goes to a public place, look through every commit that goes
out, not only the newest state. If something in the history may not be public, do not push; tell Kevin.

## Finding out

**The search that looked like a stuck model.** Asked about a word that is nowhere in the repository, the
hands searched from the root and read every file under it: 161,293 files, 4.2 GB. It looked as if the
model had frozen. It had not; the graphics card was idle the whole time. *Do:* when something hangs,
measure where the time goes before you name a cause. And search where the answer can be: source is in
`runtime/`, `static/`, `tools/`, `primals/`; `data/` is large and mostly records. (grep now stops at 20
seconds and says the search did not finish.)

**Her own wrong answer, found and repeated.** Asked which file the gate serves for `/kenshi`, the hands
found an earlier answer of their own in the run record, a wrong one, and gave it back as "explicitly
stated". *Do:* an earlier answer is not evidence, yours or anyone's. The route is in
`runtime/gaia_gate.pi`; read it there. (A search from above now leaves `data/hands` out.)

**A file that says so.** `runtime/sourdough/culture.jsonl` keeps old conversations with the models. One
of them names a port for an endpoint that never existed. Found by a search, it reads like a fact. *Do:*
ask what kind of file you are reading. Code and configuration show what the system does. A record of
talk shows what someone said.

**Guessing a name instead of reading.** Asked for the function in `runtime/arena.pi` that asks every
stable who it is, the hands listed the directory and then named a function without opening the file.
*Do:* open the file. `grep` for `def ` in it gives every function with its line; read around the one
that fits.

## Measuring

**A check that passed a wrong answer.** A question asked whether a person may be pinned on the atlas.
The check looked only for "no" as the first word, and passed an answer that said no because the atlas
is a bone in the neck. *Do:* a check must test the reason, not only the verdict. When a pass surprises
you, read the answer.

**One run is not a number.** The same eighteen questions, asked three times with nothing changed, gave
8, 9 and 9. *Do:* before you say a change helped, run it more than once on each side and give every
count.

## What may be public

**The owner asks for what the rule forbids.** Kevin may give you a street address and ask for it on a
page. The rule he set is that home is given at town level only. *Do:* do not write it. Tell him the
rule and what the page can say instead ("House 1, Lansing area"). A rule he made is changed by him
changing the rule, not by one request in passing.
