import numpy as np

class WordleEncoder():
    def __init__(self, path = 'five_letter_words.txt'):
        self.words = self._get_all_words(path)
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
            yellow = np.isin(guesses, answers)
            responses += 1*yellow
            return responses
        else: # If t
            
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
        
    def calculate_full_lookup(self, save_txt = True, first_n = None, verbose = False):
        
        x = self.X.copy() # words, maybe a subset for testing
        if first_n:
            x = x[:first_n]
            
        nb_guesses = x.shape[0]
        R = np.zeros((nb_guesses,nb_guesses)).astype('int16')
        for row, guess in enumerate(x):
            r = self.get_responses(guess,x)
            n = self._responses2num(r)
            R[row,:] = n
            if row % 100 == 0:
                print(f"Guess number {row:<4} of {nb_guesses}")
            
        if save_txt:
            np.savetxt(self.lookup_filename, R, fmt = '%d')
        else:
            return R
        
    def load_full_lookup(self):
        return np.loadtxt(self.lookup_filename, dtype = 'uint16')
            
        
    
        
    