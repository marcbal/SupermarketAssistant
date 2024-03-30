# Supermarket Assistant

A python script to assist you in managing your supermarket in the game *Supermarket Simulator* from *Nokta Games*.
The script works by reading your save file and telling you what to do next (pay your bill, displays to fill in the store, what to order and the amount, ...).

## Setup

### 1. Install python

A recent version is recommended (for me it works using Python 3.9).
Install the `ansi` module using the command `pip install ansi`

### 2. Modify the game

You need to modify the game to be able to have some informations from it (the list of all products, their name, the product licenses, ...).
Since I don't (yet) know how to package a mod for this game, You need to be able to modify it yourself.
Here is my process:
- If the game is running, stop it (don't forget to save your progress).
- Use **dnSpy** and open the file `(game install folder)/Supermarket Simulator_Data/Managed/Assembly-CSharp.dll`.
- Follow the modifications shown in the file at `mods/extract-data.txt` from this project folder.
- In **dnSpy**, save the modifications (**File** -> **Save the module**).
- Start the game and continue your saved progress. It will create a file in the save folder of the game, that the script will read, along with your save file.

### 3. Run the script

From your terminal or command prompt, use the following command:
```bash
python main.py
```

You need to run the script again every time you save your progress (or after each day).


## Extra

This repo also provides some extra modifications you can do to the game to make it a little better: you can see them in the `mods` folder.