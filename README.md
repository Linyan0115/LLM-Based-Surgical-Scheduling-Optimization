# LLM-Based-Surgical-Scheduling-Optimization

## Overview

This project builds a real-time surgical scheduling system that integrates:

- LLM-based constraint extraction (GLM-4 via Zhipu API)

- Chain-of-Expert multi-agent processing

- MILP optimization using CPLEX

The system automates surgical case analysis, surgery sequencing, and equipment allocation.
Tested on 1000+ surgeries across 20 operating rooms, it achieved:

- 18% improvement in scheduling efficiency

- 22% higher resource utilization

- 20% faster real-time decision speed

## System Pipeline

## Key Components

### LLM + COE Framework

- Converts policies, surgeon notes, and hospital rules into structured constraints

- Modules: constraint engineer, data validator, policy interpreter

- Ensures model-ready inputs for optimization

### MILP Optimization (CPLEX)

- Handles OR assignment, sequencing, surgeon availability, machine allocation

- Dynamic model selection based on case types

- Tuned for real-time scheduling
