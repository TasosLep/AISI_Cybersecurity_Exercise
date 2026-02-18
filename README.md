# AISI – Cybersecurity Take-Home Exercise

<p align="left">
  <img src="https://img.shields.io/badge/Role-Cybersecurity%20Engineer-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/Environment-Docker-informational?style=flat-square" />
  <img src="https://img.shields.io/badge/Base%20Image-Kali%20Linux-critical?style=flat-square" />
  <img src="https://img.shields.io/badge/Focus-Message%20History%20Replay-success?style=flat-square" />
</p>

Implementation for the **Cybersecurity Engineer Take-Home Exercise**

**Exercise Description (PDF) :** [Cybersecurity Engineer Take-Home Exercise](https://github.com/TasosLep/AISI_Project/blob/master/Cybersecurity_Engineer_Take%E2%80%90Home_Exercise.pdf)

**My Notes (Steps, Mistakes, Fixes) :** [Process & Lessons Learned](https://github.com/TasosLep/AISI_Project/blob/master/process_and_lessons_learned.txt)

---

## Summary

This repo implements a **message-history replay solution** with:

- **Inspect task wiring** for the `message_history` variant
- **Reproducible agent-machine Docker image** (pinned base + hardened execution)
- **Deterministic, staged replay** with persisted artifacts and logs

---

# Modified Files (`eval.yaml` & `Dockerfile`)

## 1️⃣ `eval.yaml`

### Changes
- Updated the evaluation configuration to run the **`message_history`** variant and point to the Python-based message history generator (**`solution.py`**).
- Added/updated references used for reporting/traceability during evaluation runs.

![eval.yaml](https://github.com/user-attachments/assets/1be1d8f6-1ab5-4f74-95bf-ca3147d81dce)

---

## 2️⃣ `Dockerfile` (Agent Machine)

### Changes

We updated the agent-machine image to make execution more reliable:

- **Pinned Kali base image by digest** to avoid “moving tag” drift and improve reproducibility.
- Installed required tooling (`kali-linux-headless`, `nmap`, `curl`, `iproute2`, `sshpass`, etc.).
- Applied the Kali `nmap` capability workaround (`setcap ... /usr/lib/nmap/nmap`) referenced in Kali’s issue tracker.
- Added an **`nmap-native` wrapper** that unsets PyInstaller-polluted environment variables (notably `LD_LIBRARY_PATH` pointing at `/tmp/_MEI...`) before executing the real `nmap` binary.  
  This prevents runtime issues where the sandbox runner’s embedded libs break **nmap** and even **apt-get**.  
  *(Cleaning apt lists in the same layer also keeps images smaller / more reproducible.)*

![Dockerfile](https://github.com/user-attachments/assets/6247f3b0-8eef-44b8-a965-22c3280bb5c2)

---

# Added Files (`message_history_solution_task.py` & `solution.py`)

## 1️⃣ `message_history_solution_task.py`

◉ Added a dedicated **Inspect task** that:

- Loads the **Doomla** dataset and selects the `message_history` variant  
- Hydrates `metadata.message_history` into a `PythonFunctionSource`

### Registers tools correctly for replay
- `bash_session(...)` for persistent shell state between steps  
- `bash(...)` for one-shot commands when needed  
-  increases `wait_for_output` so “quiet” commands don’t look like they never ran  

> Inspect supports tool calls to named tools like `bash` in message histories,  
> so the task must explicitly include them if you use them.

---

## 2️⃣ `solution.py`

◉ Implemented the actual **message-history generator** (the replay steps).

### Key behaviors
- The commands of `solution.sh` were used as baseline.
- Creates `./artifacts/` and appends to `./artifacts/solution.log`
- Stores stage outputs in `./artifacts/*.env` so later stages can source them
- Uses `nmap-native` (or a clean environment) to avoid `_MEI/LD_LIBRARY_PATH` issues during scanning
- Splits the chain into explicit stages:  
  **recon → pivot → DB dump → crack → workstation access → priv-esc → flag**

---

# How to Run

## Run the Inspect task normally (example)

◉ Run `message_history_solution_task.py` via Inspect’s `eval(...)` entrypoint — **builds the docker images**

### Artifacts and logs
- `./artifacts/solution.log` – main run log  
- `./artifacts/stage*.env` – persisted variables per stage  
- `./artifacts/nmap_results.log`, `./artifacts/web_nmap.txt` – scan outputs  
 
![Artifacts](https://github.com/user-attachments/assets/d76736fb-4325-4a4b-a492-a9020c305e94)
