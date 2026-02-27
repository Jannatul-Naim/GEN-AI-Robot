# 🤖 Robot Brain Module

## Overview
The **Robot Brain** module implements the cognitive layer of a robotic arm system. It integrates:

- **Vision perception**  
- **Large Language Model (LLM) reasoning**  
- **Short-term memory**  
- **Symbolic planning**

The brain converts **natural language commands** into **safe, executable robotic actions**.

---

## Architecture

User Command
↓
┌──────────┐
│ Brain │
├──────────┤
│ Memory │ ← safety & state
│ LLM │ ← intent + reasoning
│ Planner │ ← symbolic actions
└──────────┘
↓
Execution Plan
↓
Robot Controller

yaml
Copy code

---

## Directory Structure

vision/
│
├── main.py # CLI loop and system entry point
├── brain.py # Cognitive decision-making core
├── llm.py # LLM prompt + decision extraction
├── memory.py # Robot short-term memory & safety state
├── plan.py # Symbolic task planner
├── server.py # Vision + robot communication layer
├── config.py # System configuration
├── init.py
└── README.md

yaml
Copy code

---

## Core Components

### `config.py`
Defines system parameters such as:

- Vision server URL  
- Robot controller endpoint  
- LLM inference parameters  
- Confidence thresholds for object selection  

---

### `brain.py`
The central controller that:

- Checks safety state  
- Queries the LLM for intent and steps  
- Validates decisions against memory and vision  
- Produces structured execution plans  

Supported intents: `task`, `chat`, `stop`

---

### `llm.py`
Handles language grounding:

- Builds prompts enforcing safety and constraints  
- Extracts structured decisions from LLM responses  
- Prevents hallucination and enforces maximum two-step actions  

---

### `memory.py`
Tracks robot internal state:

- Held object  
- Safety mode (`normal` or `stop`)  

Prevents illegal actions such as picking while already holding.

---

### `plan.py`
Implements symbolic planning primitives:

- Object selection (`nearest`, `farthest`)  
- Pick, place, and give actions  
- Relative positioning rules  

---

### `server.py`
Communication bridge:

- Fetches object detections from the vision system  
- Sends validated plans to the robot controller  
- Handles network failures gracefully  

---

### `main.py`
Interactive command loop:

- Accepts natural language commands  
- Fetches vision data  
- Executes cognitive reasoning  
- Sends plans to the robot  

---

## Example Interaction

USER> pick the nearest bottle and place it on the right

BRAIN OUTPUT:
{
"intent": "task",
"plan": [
{"action": "pick", "object": "bottle"},
{"action": "place", "x": 10, "z": 25}
],
"reply": "Done"
}

yaml
Copy code

---

## Requirements

```bash
pip install requests