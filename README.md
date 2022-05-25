# wordle

This is a wordle solver that recommends the best guesses.

It currently runs for the danish version (wørdle.dk), but can easily be changed to other languages by changig the word lists.

Run the file "run_wordle_solver.py" to execute program.

### About the files in the directory
The file lookup.txt needs to be generated for the program to work (too large to put in git). This is done by instatiating the class WordleLookup from the file wordle_classes.py and running the class method calculate_full_lookup(). This process took arround 30 minutes on my Mac (2016 - 3.3 GHz Dual-Core Intel Core i7)

The file 'five_letter_words.txt' is generated from the fullform list "ddo_fullforms_2020-08-26.csv" containing all danish full forms. To (re)generate this file, run the file "get_five_letter_words.py".

