# Supermarket Assistant

A python program to assist you in managing your supermarket in the game *Supermarket Simulator* from *Nokta Games*.
It works by reading your save file and telling you what to do next (bills to pay, store shelf to fill, what to order and the amount, ...).

## How to use

### 1. Modify the game

You need to modify the game to be able to have some informations from it (the list of all products, their name, the product licenses, ...).
Since I don't (yet) know how to package a mod for this game, You need to be able to modify it yourself.
Here is my process:
- If the game is running, stop it (don't forget to save your progress).
- Donwload  [**dnSpy**](https://github.com/dnSpy/dnSpy/releases) and run it.
- Open the file `(game install folder)/Supermarket Simulator_Data/Managed/Assembly-CSharp.dll`.
- Modify the source of the game as shown in [this file](mods/extract-data.diff).
- In **dnSpy**, save the modifications (**File** -> **Save the module**).
- Start the game and continue your saved progress. It will create a file in the save folder of the game, that the program will read, along with your save file.

### 2. Download and run the program

Download the `SupermarketAssistant.exe` file [from here](https://github.com/marcbal/SupermarketAssistant/releases) and run the executable.
It will open a terminal window and load all the necessary data from the game.
The content of the window will automatically refresh when the game is saved.

## Run from the source

1. Install a recent version of python (for me it works using Python 3.9).
2. Install the requirements with `pip install -r requirements.txt`
3. Run the program with `python src`

## Extra

This repo also provides some extra modifications you can do to the game to make it a little better: you can see them in the [mods](mods) folder.