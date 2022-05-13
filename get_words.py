import pickle
import pandas as pd

def get_all_words(verbose = False):
    data = pd.read_csv("ods_fullforms_2020-08-26.csv",sep='\t',header = None)
    words = list(data[0])

    # Remove accents and aa
    map_letters = {
        'aa':'å',
        'ã':'a',
        'ê':'e',
        'é':'e'}
    for old, new in map_letters.items():
        words = [w.replace(old,new) for w in words]
    
    # 5 letters
    words = [w.lower() for w in words if len(w) == 5]

    # Remove words with strange symbols
    only_allowed = "abcdefghijklmnopqrstuvxyzæøå"
    word_allowed = lambda word: all([letter in only_allowed for letter in word])
    words = [w for w in words if word_allowed(w)]

    # Drop duplicates
    words = set(words)

    if verbose:
        print("Letters in words:")
        letters = set("".join(words))
        print(", ".join(sorted(letters)))
        print(f"Number of words: {len(words):,}")
    
    return words

def main():
    five_letter_words = get_all_words()
    with open('five_letter_words.pkl', 'wb') as f:
        pickle.dump(five_letter_words, f)

if __name__ == '__main__':
    main()
