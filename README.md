# README

This repo contains function that takes cisco config and turns its interface configurations
and makes ranged interfaces as it's much more compact.

## Installation

Run the following to install:

```python
pip install rangify
```

## Usage

```python
from rangify import ranger

## It can accept 2 types of inputs.

### Get ranged interfaces and configs from file
ranger("filename")

### Get ranged interfaces from dictionary of dictionaries 
ranger(interfaces)

```