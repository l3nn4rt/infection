# infection

A library for experimenting with SIR model.

## Modes

- standard package importing
- stand-alone CLI program

## Installation

1. clone repository

    ```sh
    git clone https://github.com/l3nn4rt/infection
    ```

2. install dependencies

    ```sh
    python -m pip install -r infection/requirements.txt
    ```

## Usage

All modules have an help command:

```sh
python -m infection.generation --help
python -m infection.simulation --help
python -m infection.visualization --help
```

## Example

1. create a graph

    ```sh
    python -m infection.generation --save TORUS_U_ERDOS_RENYI -c 5 -r 6 -p .1
    GRAPH_UID # save this
    ```

2. simulate infection evolution over graph

    ```sh
    python -m infection.simulation --save -g $GRAPH_UID -p .3 -s 1
    EVOLUTION_UID # save this
    ```

3. show animation and timeline

    ```sh
    python -m infection.visualization -e $EVOLUTION_UID -a -t
    ```
