#from typing_extensions import Self
import numpy as np
import pandas as pd
import os.path

class WordleEncoder():
    def __init__(self, path = 'five_letter_words.txt'):
        if os.path.isfile(path):
            self.words = self._get_all_words(path)
        else:
            print(f"{path} has not been generated yet.")
            print(f"Run get_five_letter_words.py to extract five-letter words from fullform words.")
        self._assert_words(nb_letters = 5)
        self._let2num, self._num2let = self._get_letter_maps()
        # Get numeric representation of words
        self.X = self._words2mat(self.words)
    
    def _get_all_words(self, path):
        with open(path) as f:
            all_words = f.read().splitlines()
        return all_words
    
    def _assert_words(self, nb_letters = 5):
        # Assert length = 5
        assert all([len(w) == nb_letters for w in self.words]), f"All words must have length {nb_letters}"

        # Assert case
        assert all([w.lower() == w for w in self.words]), "All words must be lower case"

        # Assert used letters
        only_allowed = "abcdefghijklmnopqrstuvxyzæøå"
        used = set("".join(self.words))
        assert all([u in only_allowed for u in used]), "Only allowed letters are {only_allowed}"
    
    def _get_letter_maps(self):
        letters = sorted(list(set("".join(self.words))))
        let2num = {l:n for n,l in enumerate(letters)}
        num2let = {n:l for l,n in let2num.items()}
        return let2num, num2let
    
    def _word2vec(self, word):
            return np.array([self._let2num[l] for l in word]).astype('int16')
    
    def _vec2word(self, vec):
        return "".join([self._num2let[n] for n in vec])
    
    def _words2mat(self, words):
        return np.array([self._word2vec(w) for w in words]).astype('int16')
    
    def _mat2words(self,mat):
        return [self._vec2word(vec) for vec in mat]
    
    def _responses2num(self,responses):
        # Convert response to number by using base 3 (gray, yellow, green)
        # Numbers count 3^4, 3^3, 3^2, 3^1, 3^0, from left to right
        return np.sum([responses[:,idx]*(3**(5-idx-1)) for idx in range(5)], axis = 0)

    def _nums2responses(self,nums):
        # Convert number to response array by using base 3 (gray, yellow, green)
        return np.array([[int(char) for char in np.base_repr(num,3).zfill(5)] for num in nums])
    
class WordleLookup(WordleEncoder):
    def __init__(self):
        super().__init__()
        self.lookup_filename = 'lookup.txt'
        self.best_two_guesses_filename = 'best_first_two_guesses.csv'
        
    def _flatten(self,t):
        return [item for sublist in t for item in sublist]

    def _find_rows_with_duplicates(self,a):
        a_sorted = np.sort(a, axis=-1)
        return list(~(a_sorted[...,1:] != a_sorted[...,:-1]).all(-1))
    
    def get_responses(self,guess: np.ndarray, answers:np.ndarray) -> np.ndarray:
        """Get responses from a single guess on multiple answers.

        Args:
            guess (np.ndarray): The guess as numbers
            answers (np.ndarray): Array of answers to return responses for.
            Expected to have one guess for each row.

        Returns:
            np.ndarray: The responses as same size as answers.
                0: black (no match), 1: yellow (correct letter, wrong position)
                2: green (correct letter and position)
        """
        
        # Do not change the answers globally
        answers = answers.copy()
        
        # Expand guesses to same size as answers, to prepare for removal of letters
        guesses = np.tile(guess,(answers.shape[0],1))
            
        # First put greens
        green = (guesses == answers)

        # Remove greens from guess and answers by putting dummy
        guesses[green] = -1 # Dummy
        answers[green] = -2 # Not same as guesses dummy

        # Add green to response
        responses = 2*green
        
        # Add yellows depending on duplicated letters in guess
        guess_has_no_duplicates = len(guess) == len(set(guess))
        if guess_has_no_duplicates:
            # This is simple. Add the yellows by checking if guess letter is in answer
            yellow = (guesses[:,:,None] == answers[:,None,:]).any(-1)
            responses += 1*yellow
            return responses
        else:
            # Make yellows iteratively until no more matches are found
            # Find rows (words) that have still duplicated letters after green letters are removed
            all_rows = np.array(range(answers.shape[0]))
            check_rows = self._find_rows_with_duplicates(guesses)
            while check_rows:
                intersects = [np.intersect1d(g, a,return_indices=True) for g,a in zip(guesses[check_rows],answers[check_rows])]
                idx_guess = [list(intersect[1]) for intersect in intersects]
                
                # Note, the output from intersect1d gives each row in the subset all_rows[check_rows]
                # Make sure "rows" below refer to the global row number
                rows = self._flatten([[r]*len(g) for r,g in zip(all_rows[check_rows],idx_guess)])
                if rows: # If no rows found, continue and exit in next loop 
                    idx_answer = [list(intersect[2]) for intersect in intersects]
                    idx_guess = self._flatten(idx_guess)
                    idx_answer = self._flatten(idx_answer)
                    responses[rows,idx_guess] = 1 # Assign yellow
                    guesses[rows,idx_guess] = -10 # Remove from guess after yellow
                    answers[rows,idx_answer] = -11 # Remove from answer after yellow
                    
                # Check the rows that has been assigned a yellow again for matches
                check_rows = list(set(rows))
                
            return responses
        
    def calculate_full_lookup(self, save_txt = True, verbose = False):
        X = self.X.copy()
            
        nb_guesses = X.shape[0]
        R = np.zeros((nb_guesses,nb_guesses)).astype('uint8')
        for row, guess in enumerate(X):
            r = self.get_responses(guess,X)
            n = self._responses2num(r)
            R[row,:] = n
            if row % 10 == 0:
                print(f"Guess number {row:<4} of {nb_guesses}")
            
        if save_txt:
            np.savetxt(self.lookup_filename, R, fmt = '%d')
        else:
            return R
        
    def load_full_lookup(self):
        if os.path.isfile(self.lookup_filename):
            return np.loadtxt(self.lookup_filename, dtype = 'uint8')
        else:
            print(f"The file self.lookup_filename has not been generated yet.")
            print(f"Run the function 'calculate_full_lookup'")
    
    def calculate_best_two_guesses(self, nb_best = 100):
        print("Calculates the best two guesses to start with")
        # Get the 20 best guess1
        df_best = self.get_best_guesses(top_n = 20)
        guess1_idx_vec = list(df_best['guess_idx'])
        
        # Search for the best second guess in combination with these
        nb_guesses = self.R.shape[0]
        nb_possible_answers = self.R.shape[1]
        informations = np.zeros((nb_guesses,nb_guesses))
        # Each guess pair leads to multiple response pairs.
        for _counter, guess1_idx in enumerate(guess1_idx_vec):
            _responses1, _ = np.unique(self.R[guess1_idx,:], return_counts = True)
            for guess2_idx in range(nb_guesses):
                
                _information = 0
                for _response1 in _responses1:
                    response1_args = np.argwhere(self.R[guess1_idx,:] == _response1).ravel()
                    _, _counts2 = np.unique(self.R[guess2_idx,response1_args], return_counts = True)
                    # Probability of getting pattern1 and pattern2
                    _p = _counts2 / nb_possible_answers # Arrays for all response2
                    _information +=  -np.sum(_p*np.log2(_p))
                if guess2_idx % 100 == 0:
                    print(_counter,guess2_idx,_information)
                informations[guess1_idx, guess2_idx] = _information

        best_args = np.argsort(-informations.flatten())
        guess1_idx = best_args // informations.shape[0]
        guess2_idx = best_args % informations.shape[0]
        data = [(self.words[idx1],self.words[idx2],informations[idx1,idx2],(1/2)**informations[idx1,idx2]*RinformationsR.shape[0]) for idx1,idx2 in zip(guess1_idx[:nb_best],guess2_idx[:nb_best])]
        df_best_two = pd.DataFrame(data = data, columns = ['guess_1','guess_2','information','expected_nb_words'])
        df_best_two.to_csv(self.best_two_guesses_filename)
        return
    
    def load_best_two_guesses(self):
        if os.path.isfile(self.best_two_guesses_filename):
            return pd.read_csv(self.best_two_guesses_filename)
        else:
            print(f"The file {self.lookup_filename} has not been generated yet.")
            print(f"Run the function 'calculate_full_lookup'")
        
class WordleSolver(WordleLookup):
    def __init__(self):
        super().__init__()
        self.R = self.load_full_lookup()
        self.R_original = self.R.copy() # Prepare for reset
        self.guess_number = 0
        self.words_reduced = self.words.copy()
        self.guesses = []
        self.responses = []
        
    def reset(self):
        self.R = self.R_original
        self.guess_number = 0
        self.words_reduced = self.words.copy()
        self.guesses = []
        self.responses = []
         
    def get_best_guesses(self, top_n = 10, only_possible = False):
        # Get information
        nb_guesses = self.R.shape[0]
        nb_possible_answers = self.R.shape[1]
        informations = np.zeros(nb_guesses)
        for guess_idx in range(nb_guesses):
            _, _counts = np.unique(self.R[guess_idx,:], return_counts = True)
            _p = _counts / nb_possible_answers
            _information = -np.sum(_p*np.log2(_p))
            informations[guess_idx] = _information
            
        best_args = np.argsort(-informations)
        best_guesses = np.array(self.words)[best_args]
        is_possible_answer = [w in self.words_reduced for w in best_guesses]
        best_informations = informations[best_args]
        expected_reduction = (1/2)**best_informations
        expected_nb_words = nb_possible_answers*expected_reduction

        df_best = pd.DataFrame()
        df_best['guess'] = best_guesses
        df_best['guess_idx'] = best_args
        df_best['is_possible_answer'] = is_possible_answer
        df_best['information'] = best_informations
        #df_best['expected_reduction'] = expected_reduction
        df_best['expected_nb_words'] = np.round(expected_nb_words,2)
        
        if only_possible:
            df_best = df_best.query('is_possible_answer')
        return df_best.head(top_n)
    
    def register_guess(self, guess_word, response):
        self.guesses.append(guess_word)
        self.responses.append("".join([str(r) for r in response]))
        guess_word = guess_word.lower()
        if len(guess_word) != 5:
            print("Expecting words with five letters")
            return
        if len(response) != 5:
            print("Expecting responses with five letters")
            return
        if set(response) - set([0,1,2]):
            print("Response needs to be numbers 0 (black, letter not in word), 1 (yellow, letter in word but wrong position) or 2 (green, correct letter and position)")
            return
        if guess_word not in self.words:
            print(f"{guess_word} is not in word list")
            return
    
        response = self._responses2num(np.array([response]))[0]
        word_idx = self.words.index(guess_word)
        
        # Reduce columns (possible answers) of R_reduced
        new_args = np.argwhere(self.R[word_idx,:] == response).ravel()
        self.words_reduced = list(np.array(self.words_reduced)[new_args])
        self.R = self.R[:,new_args]
        self.guess_number += 1
        
    def print_possible_answers(self, top_n = 10):
        nb_possible_answers = len(self.words_reduced)
        print(f"Listing top {top_n} possible answers:")
        print("\n".join(self.words_reduced[:top_n]))
        print(f"({nb_possible_answers} total possible answers)")
        return
   