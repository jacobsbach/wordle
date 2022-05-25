
from wordle_classes import WordleSolver
     
def run_wordle_solver():
    def print_options():
        print("\t- Place guess (p)")
        print("\t- Show best guesses (b)")
        print("\t- Show possible answers (a)")
        print("\t- Check a guess (c)")
        print("\t- Show best first two guesses (t)")
        print("\t- Reset guesses (r)")
        print("\t- Exit (e)")
        
    def initialize():
        print("\n\n")
        print("#################################")
        print("# Welcome to the wordle solver #")
        print("#################################")
        print("Wait while the solver starts...\n")
        ws = WordleSolver()
        print("The Wordle Solver is ready!")
        return ws
        
    def _place_guess(ws):
        print('Place your guess:')
        guess = input()
        print('And what is the response?')
        print("(e.g. 10020 for yellow,gray,gray,green,black)")
        response = input()
        response = [int(x) for x in list(response)]
        ws.register_guess(guess,response) 
        return ws
    
    def _show_best_guesses(ws):
        print("Showing best 10 guesses")
        ws.get_best_guesses(10)
        return ws
    
    def _show_possible_answers(ws):
        print("Showing 10 possible answers")
        ws.print_possible_answers(10)
        return ws
    
    def _check_guess(ws):
        print("What answer do you want to check?")
        return ws
    
    def _show_best_two_guesses(ws):
        print("The top 10 first two guesses are:")
        return ws
    
    def _reset_guesses(ws):
        print("Guesses reset")
        return
    
    def _exit(ws):
        print("Exiting the solver. See you!")
        return 'exit'
    
    call_dict = {
        'p':_place_guess,
        'b':_show_best_guesses,
        'a':_show_possible_answers,
        'c':_check_guess,
        't':_show_best_two_guesses,
        'r':_reset_guesses,
        'e':_exit,
        }
    
    def get_input():
        user_input = input()
        if user_input not in call_dict:
            print(f'"{user_input}" is not a valid input.')
            print("Please input one of the following options:")
            print_options()
            get_input()
        return user_input
            
    ## Running
    ws = initialize()
    print("Options:")
    print_options()
    user_input = get_input()
    while True:
        ws = call_dict[user_input](ws)
        if ws == 'exit':
            break
        user_input = get_input()
    
if __name__ == '__main__':
    run_wordle_solver()