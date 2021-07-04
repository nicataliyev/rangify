README
======

This repo contains function that takes cisco config and turns its interface configurations
and makes ranged interfaces as it's much more compact. It compares every interface config block to others and extracts similar ones only. It also shortens the cisco interface names. ex: it prints `GigabitEthernet1/0/1` as `Gi1/0/1`

Installation
------------

Run the following to install:

```python
pip install rangify
```

Usage
-----

```python
from rangify import ranger

ranger("cisco_config.txt") # or ranger(interfaces_dict)

```
## **It can accept 2 types of inputs.**  
<br>

## Text config from file  
<br>

Let's say `test_config.txt` contains following text(abbreviated, for full text please check the `test_config.txt` file)

```
!
interface GigabitEthernet1/0/1
 ...any text config block..
!
interface GigabitEthernet1/0/2
 ...any text config block..
!
interface GigabitEthernet1/0/3
 ...any text config block..
!
```
Then following function will print to screen more compact ranged version of configuration:


```python
ranger("filename.txt")
```
Output:  

```
interface range Gi1/0/1-3
 ...any text config block...
```

## Interfaces as dictionary of dictionaries  
<br>

This takes dictionary of dictionaries as an input. Key for dictionary is interface name and the value is the configuration dictionary.  And returns same dictionary structure but this time the keys are in collapsed/ranged form. Example below.

```python
# input dictionary
sample_ints = {
        "GigabitEthernet1/0/1": {},
        "GigabitEthernet1/0/2": {},
        "GigabitEthernet1/0/4": {"mode": "access"},
        "GigabitEthernet3/4/2": {"mode": "access"},
        "GigabitEthernet3/4/3": {"mode": "access"},
        "GigabitEthernet3/5/3": {"mode": "trunk"},
        "GigabitEthernet3/6/3": {"mode": "trunk"},
}
# range them all
print(ranger(interfaces))
```

Output:
```python
    {'range Gi1/0/1-2': {}, 
    'range Gi1/0/4, Gi3/4/2-3': {'mode': 'access'}, 
    'range Gi3/5/3, Gi3/6/3': {'mode': 'trunk'}}
```