# QubitHub Qiskit Fall Fest 2026 - ten quantum computing challenges

Ten guided, progressively harder coding challenges for a one-day quantum computing hackathon, written for **Qiskit 2.x**.
Each challenge is a Jupyter notebook with a story, the key idea, your **TODO** functions, public checks that tell you right away
what works, and hints that go from subtle to explicit. Everything runs on an ordinary laptop (CPU only): **no accounts, no API keys,
no paid services and no quantum hardware.**

| # | Challenge | Tier | Estimated time* | What you practise | Colab |
|---|---|---|---|---|---|
| 1 | Superposition Under the Microscope | 1 - Foundations | 15-25 min | amplitudes vs probabilities, exact vs sampled results | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_01_superposition/challenge_01_superposition.ipynb) |
| 2 | The Entanglement Detective | 1 - Foundations | 20-30 min | Bell states, correlations in several bases, telling entangled from product states | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_02_entanglement/challenge_02_entanglement.ipynb) |
| 3 | Gate Surgeon | 1 - Foundations | 20-30 min | reading and repairing circuits, bit order, equivalent circuits | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_03_gate_surgeon/challenge_03_gate_surgeon.ipynb) |
| 4 | Teleport the Qubit | 2 - Algorithms and applications | 40-60 min | teleportation with mid-circuit measurement and classical control | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_04_teleportation/challenge_04_teleportation.ipynb) |
| 5 | Find the Hidden State | 2 - Algorithms and applications | 40-60 min | Grover search: oracle, diffuser, number of iterations | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_05_grover/challenge_05_grover.ipynb) |
| 6 | Fight the Noise | 2 - Algorithms and applications | 40-60 min | noise models, total variation distance, does mitigation really help? (needs `qiskit-aer`) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_06_noise/challenge_06_noise.ipynb) |
| 7 | The Quantum Network Cut | 2 - Algorithms and applications | 45-60 min | Max-Cut as a Hamiltonian, QAOA, correctness vs solution quality | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_07_qaoa_maxcut/challenge_07_qaoa_maxcut.ipynb) |
| 8 | Teach a Quantum Circuit | 3 - Advanced | 60-90 min | variational classifier, training, train/test leakage, honest baselines | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_08_quantum_ml/challenge_08_quantum_ml.ipynb) |
| 9 | Protect the Logical Qubit | 3 - Advanced | 50-80 min | three-qubit bit-flip code, syndromes, feed-forward, what it cannot protect | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_09_error_correction/challenge_09_error_correction.ipynb) |
| 10 | The Hardware Architect | 3 - Advanced | 45-75 min | transpilation for a given coupling map: depth and two-qubit gate count | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_10_transpilation/challenge_10_transpilation.ipynb) |

\* The times are **estimates**, not measurements. Start with challenge 1; the tiers get harder, but every challenge is self-contained.

**New here?** Click a **Colab** badge to open that notebook in Google Colab - nothing to install, see [Colab](#colab) - or follow [Quick start - local Jupyter](#quick-start---local-jupyter) to work on your own computer.

## What you need

* Python 3.11 or newer (3.11, 3.12, 3.13 and 3.14 were tested; Python 3.10 is not supported - the pinned `qiskit-aer` does not install there), about 1 GB of free disk space, and either a local Jupyter setup or a (free) Google account for Colab.
* The exact library versions the project was **tested with** are pinned in [`requirements.txt`](requirements.txt)
  (Qiskit 2.6.0, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.2, pytest 9.1.1; Qiskit Aer 0.18.0 for challenge 6 only).
  `pyproject.toml` lists the *compatible ranges*. Other combinations should work but are **untested**.
* **Windows on ARM** laptops (Snapdragon) cannot use the pinned versions: Qiskit 2.6.0 has no ready-made build for them and `pip` would try to compile it. Use Colab (below) instead,
  or install an x64 build of Python (not tested).
* Only **challenge 6** needs `qiskit-aer` (a noise-capable simulator). It is deliberately not required for the other nine. The setup cell
  of the challenge 6 notebook installs it if it is missing (this needs an internet connection); you can also install it beforehand
  with `pip install qiskit-aer==0.18.0`.

## Quick start - local Jupyter

```bash
python -m venv .venv
# Windows (PowerShell):   .venv\Scripts\Activate.ps1
# Windows (cmd):          .venv\Scripts\activate.bat
# macOS / Linux:          source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
pip install jupyterlab        # or open the notebooks in VS Code; JupyterLab itself is not pinned by this project
jupyter lab
```

Then open `challenges/challenge_01_superposition/challenge_01_superposition.ipynb` and run the cells from top to bottom.
Start Jupyter from inside this folder (or open the notebook from here): the first cell finds the project by looking for `pyproject.toml`
in the notebook's working folder and its parents.

## Colab

The quickest route needs nothing on your computer: **click the "Open in Colab" badge of your challenge** in the table at the top of this page.

1. Colab opens the notebook straight from GitHub. When you run it, Colab warns that the notebook was not authored by Google - that is the standard message for every notebook that comes from GitHub; choose *Run anyway*
   (everything the notebook runs is in this repository).
2. Run the first cell (*Setup*). Colab opened only the notebook, so the cell **fetches the project from GitHub** into the Colab machine (a few seconds), installs it together with the compatible Qiskit version
   (about a minute the first time) and prints the library versions it found. Colab's own versions differ from the tested ones: if a check behaves oddly, the cell says which versions differ.
3. Work through the notebook as described under *Open a challenge*. Colab does **not** save changes to the GitHub original, and every notebook runs on its own, initially empty machine: use
   *File > Save a copy in Drive* (or *File > Download .ipynb*) before you leave - a recycled runtime forgets everything. For the next challenge you open, the setup cell fetches the project again.
4. To hand in, run the last cell: it writes `submission_cNN.py` into `/content`. Open the *Files* pane (folder icon), right-click the file and choose *Download*.

**If the badge does not work for you** - for example because the organisers gave you a zip file - upload the project yourself. Colab runs every notebook in its own, initially empty machine, so do this *in the notebook you work in*, and again for
each challenge notebook you open. The project team went through this route once on a real Colab runtime (2026-10-30, Python 3.13): challenge 1 in the Colab interface from the upload to the hand-in cell,
and all ten notebooks executed on that Colab machine.

1. Unzip the file on your computer: you need the notebook of your challenge, `challenges/challenge_NN_<name>/challenge_NN_<name>.ipynb`. In Colab choose *File > Upload notebook* and pick that notebook.
2. Add a code cell above its first cell (hover over the top edge of the first cell and click *+ Code*) and run it:

   ```python
   from google.colab import files
   files.upload()                                   # choose the zip file you received
   !unzip -q participant_package.zip
   %cd participant_package
   ```

   (If you received a repository address, use `!git clone <that address>` and `%cd` into the folder it creates.)
3. Run the setup cell (the first cell of the notebook). It finds the project when it is the working folder, one of its parents, or a folder right below it, installs the helper package
   (`pip install -e .`) and the compatible Qiskit version from `pyproject.toml`; this takes a minute. If it says that it cannot find the project, run `%cd /content/participant_package` in a cell above it first.
   If Colab shows a banner asking you to restart the session after the installation, restart it and run the setup cell again.
4. Colab files disappear when the runtime is recycled: download your notebook (*File > Download .ipynb*) before you leave. The last cell writes `submission_cNN.py` into the folder you entered with `%cd`.

Colab changes its runtime images from time to time, so tell the organisers if a step behaves differently for you.

## Open a challenge

Every folder `challenges/challenge_NN_<name>/` contains

| File | What it is |
|---|---|
| `challenge_NN_<name>.ipynb` | the guided notebook - **open this one** |
| `starter.py` | the same TODO stubs as a plain Python file (for editors and the command line) |
| `README.md` | the problem statement, function contracts and acceptance criteria in one page |

How a notebook works: read the story, run the cells in order, complete the cells marked **TODO**, then run the **public checks** cell. It lists every check
as `[PASS]`, `[FAIL]` (with a message) or `[TODO]` (the function still raises `NotImplementedError`). Open the hints one at a time - subtle first, explicit last.
Cells that need a finished function print "not ready yet" instead of failing while a TODO is open, so you can run the whole notebook at any time.

Working outside Jupyter:

```bash
pytest tests/public/test_c01_public.py --impl challenges/challenge_01_superposition/starter.py     # your edited starter file
pytest tests/public/test_c01_public.py --impl path/to/your_notebook.ipynb                            # your notebook
```

To hand in your work, save the notebook or run the last cell: it writes `submission_cNN.py` into the folder the notebook runs in (normally the folder of the notebook; in Colab `/content`
or the folder you entered with `%cd`, listed in the *Files* pane, where you can download it).

## How your work is checked

* The **public checks** you can run yourself are a *smoke test*: they confirm that the basics work. Passing them is necessary, not sufficient.
* The organisers run **additional hidden tests** with many more inputs, edge cases (invalid input must raise `ValueError`), different sizes and different random seeds.
  Hard-coding an answer does not help: tests change the input and check the *mathematics* of the result (state vector, unitary, probabilities), never the exact
  gates you used - any correct construction is accepted.
* Exact quantities are compared with an absolute tolerance of 1e-9. Quantities obtained from finite shots use fixed seeds and a documented statistical tolerance.
* Challenges with an optimisation component (7, 8 and 10) grade **correctness** and **solution quality** separately: a stochastic optimiser is never required to be perfect.
* Typical scoring: 60% correctness, 20% edge cases, 10% your reflection answers, 10% code clarity (50 / 15 / 15 quality / 10 / 10 for challenges 7, 8 and 10).
  *Bonus* tasks give up to 10 extra points and are never needed for full marks.

## Rules of fair play

* Hints and documentation are welcome; ask the organisers when you are stuck. Do not copy another team's solution.
* Do not edit the files in `src/` and `tests/` - the checks must stay the same for everybody.
* Never share your notebook outputs with credentials or personal data in them; this project needs none.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `ModuleNotFoundError: qiskit_fest` | start Jupyter from this folder, or run `pip install -e . --no-deps` in it |
| circuit drawings fall back to text | `pip install pylatexenc` (it is in `requirements.txt`) |
| challenge 6: `ModuleNotFoundError: qiskit_aer` | `pip install qiskit-aer==0.18.0` (internet needed) |
| `pip install -r requirements.txt` says it "could not find a version" of `qiskit` or `qiskit-aer`, or starts compiling Qiskit | check `python --version` (3.11 or newer is required) and, on Windows, whether the laptop is ARM-based (see *What you need*); Colab avoids both problems |
| challenge 6 on Linux: `ImportError: ... cannot allocate memory in static TLS block` when `qiskit_aer` is imported | start Python / Jupyter with the environment variable `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` (e.g. `export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` in the terminal before `jupyter lab`); it must be set before the program starts. We met this in a plain Linux container; whether your machine is affected is unknown |
| the setup cell warns that versions differ | everything should still work; `pip install -r requirements.txt` in a fresh virtual environment reproduces the tested versions |
| `[TODO]` in the checks | that function still raises `NotImplementedError` - finish the TODO cell and run it again |
| the notebook cannot find the project | open the notebook from this folder (see *Colab* for Colab) |

## Reporting a problem

Tell the organisers at the event or - if you received this package through a repository - open an issue there. A report helps most when it contains

* the challenge number and the cell or check that fails (the name the public checks print);
* the **complete** error message, copied as text rather than as a screenshot;
* the output of `python -c "import qiskit_fest; print(qiskit_fest.environment_report())"` and the name of your system (Windows, macOS, Linux, Colab);
* what you have already tried.

Please do not paste credentials or personal data into a report; this project needs none.

## What was verified, and what was not

The challenge bank was developed and checked on **Windows 11 with CPython 3.11.9 in a virtual environment** with exactly the versions in `requirements.txt`. The project's own test suite
(the public and hidden tests run against the reference solutions) also passed in **Linux containers** with Python 3.11, 3.12, 3.13 and 3.14 using the pinned versions, and with Python 3.12 and 3.13 using the newest versions the declared ranges allow (Qiskit 2.6.1, NumPy 2.5.4, SciPy 1.18.1). On Windows a fresh virtual environment built from `requirements.txt` ran the notebooks of
challenges 1 and 6 from their own setup cell, and a Colab-style emulation (Ubuntu 24.04, Python 3.12, the newest allowed library versions, project unzipped next to the notebook) ran all ten notebooks
without errors. On **Google Colab** (2026-10-30: Python 3.13.18, Qiskit 2.6.1, NumPy 2.1.3, SciPy 1.16.3, Matplotlib 3.10.0, pytest 8.4.2) challenge 1 was worked through by hand in the Colab interface and all ten
notebooks were executed on a Colab machine; that run found a problem with the first run of challenge 6 on a machine without Aer (all its checks were skipped), which is fixed. The test suite also passes in a Linux
container with exactly those Colab library versions. macOS and Qiskit versions other than 2.6.0 / 2.6.1 are **untested**; for macOS we only checked with `pip` that ready-made builds of every pinned
library exist (Apple silicon and Intel, Python 3.11 to 3.14). Windows on ARM is not supported by the pinned versions (see *What you need*).
Check what *your* installation does with `python -c "import qiskit_fest; print(qiskit_fest.environment_report())"`.
