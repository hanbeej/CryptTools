import sys
sys.path.insert(0, "../lib")
from utils import *
from validator import *
import argparse
import enchant

def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="text to read from. If not specified the program will read from standard input")
    parser.add_argument("-k", "--key", help="key used to encrypt. If the length of the text is different from the key length, it does not work. ", type=int)
    parser.add_argument("-l", "--lang", help=f"available languages: {enchant.list_languages()} (default: en_US). Only useful if no key is provided", default='en_US')
    parser.add_argument("-V", "--verbose", action='store_true', help="show extra information")
    parser.add_argument("-A", "--all", action='store_true', help="show decrypted text for each tested key")
    parser.add_argument("-D", "--debug", action='store_true', help="show information about text validation")
    parser.add_argument("-T", "--threshold", help="valid word count percentage to mark the whole text as valid language (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="plays a beep sound when program finishes. May require SOX to be installed")
    args = parser.parse_args()


def permutation(text,order):
    cipher_text=''
    text_order=list(map(int,list(str(order))))
    for n in range(len(text)):
        cipher_text=cipher_text+text[int(text_order[n])-1]
    return cipher_text


if __name__ == "__main__":
    set_args()

    validator = Validator(args.lang, args.threshold, args.debug, args.beep)
    text = read(args.text)

    if args.key is not None:
        if args.verbose:
            print(f"Original text most frequent character: {most_frequent_char(clean(text))}\n")
        encrypted = permutation(text, args.key)
        print(encrypted)
        if args.verbose:
            print(f"\nEncrypted text most frequent character: {most_frequent_char(clean(encrypted))}")
