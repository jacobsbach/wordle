
from wordle_classes import WordleSolver
     
def run_wordle_solver():
    def _show_status(ws):
        nb_possible_anwers = len(ws.words_reduced)
        guess_number = ws.guess_number
        print(f"Waiting for guess {guess_number+1}")
        print(f"There are {nb_possible_anwers} possible answers")
        if guess_number > 0:
            print("Placed guesses:")
            for idx, (guess,response) in enumerate(zip(ws.guesses,ws.responses)):
                print(f"{idx+1:>2}:\t{guess}\t({response})")
                
        return ws
        
    def _initialize():
        print("\n\n")
        print("#################################")
        print("# Welcome to the wordle solver #")
        print("#################################")
        print("Wait approximately 30 seconds while the solver starts...\n")
        ws = WordleSolver()
        print("The Wordle Solver is ready!")
        return ws
    
    def _get_guess_input(ws):
        guess = input()
        if len(guess) != 5:
            print("The guess has to be five characters")
            return _get_guess_input(ws)
        if guess not in ws.words:
            print(ws.words)
            print(f"{guess} is not in the word list of the solver")
            return _get_guess_input(ws)
        return guess
    
    def _get_and_parse_response():
        response = input()
        if (not response.isnumeric()) or (len(response) != 5):
            print("Response has to 5 numbers")
            print("(e.g. 10020 for yellow, gray, gray, green, gray)")
            _get_and_parse_response()
        response = [int(x) for x in list(response)]
        return response
            
    def _place_guess(ws):
        print('Place your guess:')
        guess = _get_guess_input(ws)
        print('And what is the response?')
        print("(e.g. 10020 for yellow, gray, gray, green, gray)")
        response = _get_and_parse_response()
        ws.register_guess(guess,response) 
        print("Guess and response is registered.\n")
        return ws
    
    def _show_best_guesses(ws):
        print("##### Showing best 10 guesses #####")
        df_best = ws.get_best_guesses(10)
        print(df_best)
        print("\n")
        return ws
    
    def _show_possible_answers(ws):
        print("##### Showing 10 possible answers #####")
        ws.print_possible_answers(10)
        print("\n")
        return ws
    
    def _reset_guesses(ws):
        ws.reset()
        print("Guesses reset")
        return ws
    
    def _exit(_):
        print("Exiting the solver. See you!")
        return 'exit'
    
    def _show_options():
        print("\t- (1) Place guess")
        print("\t- (2) Show status")
        print("\t- (3) Show best guesses")
        print("\t- (4) Show possible answers")
        print("\t- (5) Reset guesses")
        print("\t- (6) Exit")
    
    call_dict = {
        '1':_place_guess,
        '2':_show_status,
        '3':_show_best_guesses,
        '4':_show_possible_answers,
        '5':_reset_guesses,
        '6':_exit,
        }
    
    def get_input():
        user_input = input()
        if user_input not in call_dict:
            print(f'"{user_input}" is not a valid input.')
            print("Please input one of the following options:")
            _show_options()
            get_input()
        return user_input
            
    ## Running
    ws = _initialize()
    _show_status(ws)
    print("Options:")
    _show_options()
    user_input = get_input()
    while True:
        ws = call_dict[user_input](ws)
        if ws == 'exit':
            break
        _show_status(ws)
        
        print("\nOptions:")
        _show_options()
        user_input = get_input()
    
if __name__ == '__main__':
    run_wordle_solver()