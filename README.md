# Life Sim 

Simulating an abstraction of life.


# Goal

"I can run one simulation from the command line, and it creates one CSV file."

This repository will use **two connected modes**:

### 1. Training World 

Used for:

- random policy  
- scripted baseline  
- Population Q-learning  
- memory experiments  

Properties:

- one agent  
- one grid  
- food respawn  
- no reproduction  
- mostly stationary dynamics  

Why?
This is where the learning policy becomes understandable.


### 2. Population World 

Used for:

- reproduction  
- mutation  
- trait selection  
- ecology-like runs  

Properties:

- multiple agents  
- shared resources  
- births and deaths  
- population-level change  
- no expectation that tabular RL remains perfectly stable  

This is where adaptation and population behavior emerge.

> This separation is not optional. It makes the project much easier to reason about.


