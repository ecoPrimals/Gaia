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

**The teacher did it too.** This page's own rule sheet said "port 31415 does not exist". The head (the
cloud agent that wrote these lessons) copied that line forward and called the port invented. Nobody had
looked. biomeOS was listening on 31415 on this gate the whole time; what never existed is the zk-commit
endpoint. It came out only when the listening ports were listed for another reason. *Do:* a claim about
a running system is checked against the running system, also when the claim is in your own rule sheet,
and also when you are the one teaching.

**Choosing between files without opening them.** In 59 cases the hands were asked which of several
files with the same name a page means, each case twice with the list turned around. They never opened
a file: every answer came from the paths alone. In 27 cases the answer changed when the list was
turned, in 16 there was no usable answer, and in 16 they named the same file both times. The head read
those 16 against the page: 8 stood, 8 did not. One wrong pick took a path with "neuromorphic" in it for
a paper about a neuromorphic chip, when the paper names the other repository eleven times. *Do:* when
the choice is between files, open the page and the files. An answer that changes when the list is
turned around was a guess, and an answer that stays the same can still be one.

## Measuring

**A check that passed a wrong answer.** A question asked whether a person may be pinned on the atlas.
The check looked only for "no" as the first word, and passed an answer that said no because the atlas
is a bone in the neck. *Do:* a check must test the reason, not only the verdict. When a pass surprises
you, read the answer.

**One run is not a number.** The same eighteen questions, asked three times with nothing changed, gave
8, 9 and 9. *Do:* before you say a change helped, run it more than once on each side and give every
count.

**The same bytes, or only the same text.** Files were copied into the commons from Windows checkouts
and hashed. 304 of 324 had Windows line ends that their repositories never held, and "is this the file
its repository published?" came back no for 328. Nothing was wrong with the files; the checkout had
rewritten them. *Do:* when a hash matters, take the bytes git stored (`git show HEAD:path`), not the
file the checkout wrote. And turn line-end conversion off where hashes are kept (`* -text`).

**A busy server is not a missing file.** The first check of the new site said 14 files were missing;
the next, a minute later, said 8. None were. The check had counted "the server did not answer in time"
as "the file is not there". *Do:* keep "not there" (the server said so) apart from "no answer", ask
again before you report, and when a count changes between two runs with nothing changed, distrust both.

**Carried is not federated.** Asked to pass the commons from one gate's nestgate to the other, both
ways failed: one gate could not reach its security provider, the other speaks a transport the first
does not offer. A script then fetched each file from one and put it into the other, and both stores
now hold all 370. That is a copy made by a third party, and the record says "carried". *Do:* name what
was done by what did it. If the thing you were asked to test failed and you reached the goal another
way, report the failure first and the other way second.

## What may be public

**The owner asks for what the rule forbids.** Kevin may give you a street address and ask for it on a
page. The rule he set is that home is given at town level only. *Do:* do not write it. Tell him the
rule and what the page can say instead ("House 1, Lansing area"). A rule he made is changed by him
changing the rule, not by one request in passing.
