#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../lib")
from validator import *
from utils import FAILED, MODULE, ENGLISH_IC, MIN_ENGLISH_IC, MAX_SCORE, error, flatten, flatmap, read, clean, memoize, shift_by
import utils
import caesar
import math
import enchant
import argparse

KEY_LENGTH_THRESHOLD = 100
TEST_2_MAX_TEXT_LENGTH = 32

def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="텍스트를 읽어들임. 만일 프로그램을 특정하지 않았다면 기본적 입력값을 읽어들임")
    parser.add_argument("-k", "--key", help="암호화,복호화에 필요한 키값. 만일 키값이 제공되지 않았으면 크렉을 시도 텍스트를 복호화")
    parser.add_argument("--decrypt", action='store_true', help="키값을 이용해 텍스트를 복호화. 만일 키가 없을경우 다른 argument와 중복")
    parser.add_argument("--exhaustive", action='store_true', help=f"모든 가능한 키값을 테스트. 이 프로그램이 제공되지 않는 경우, 길이보다 작은 키만 테스트할 수 있음 {KEY_LENGTH_THRESHOLD} 크렉킹 동안")
    parser.add_argument("-V", "--verbose", action='store_true', help="여분의 정보를 알려줌")
    parser.add_argument("-A", "--all", action='store_true', help="테스트된 각 키에 대해 해독된 텍스트 표시")
    parser.add_argument("-D", "--debug", action='store_true', help="텍스트 유효성 확인에 대한 정보 표시")
    parser.add_argument("-T", "--threshold", help="전체 텍스트에 유효한 단어 수 비율 (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="프로그램이 끝나면 삐 소리가 난다. SOX를 설치해야 할 수 있음")
    args = parser.parse_args()

def vigenere(text, key):
    shifts = [ord(k) - ord('a') for k in key.lower()]
    if args.verbose:
        print(f'Key "{key}" shifts: {shifts}')
    i = 0
    key_length = len(key)
    def do_shift(char):
        nonlocal i
        if char.isalpha():
            shift = shifts[i] if not args.decrypt else MODULE - shifts[i]
            i = (i + 1) % key_length
            return shift_by(char, shift)
        return char
    return ''.join(map(do_shift, text))

def useful_divisors(terms):
    threshold = None if args.exhaustive else KEY_LENGTH_THRESHOLD
    return flatmap(lambda n: list(utils.divisors(n, threshold))[1:], terms)

def caesar_crack(text):
    if args.verbose:
        print("Testing key length 1 (Caesar crack)")
    caesar.args = args
    caesar.validator = validator
    (decryptedKey, decryptedText) = caesar.crack(text, terminal=False)
    if decryptedKey is not None:
        key = chr(decryptedKey + ord('A'))
        return (key, decryptedText)
    elif args.verbose:
        print("Caesar failed")
    return FAILED

def friedman(text, frequencies=None):
    kp = ENGLISH_IC
    kr = MIN_ENGLISH_IC
    ko = utils.coincidence_index(text, frequencies)
    return (ko, math.ceil((kp - kr)/(ko - kr)))

def kasiki(text):
    if args.verbose:
        print("Finding sequence duplicates and spacings...")
    utils.args = args
    min_length = 2 if (args.exhaustive or len(clean_text) < TEST_2_MAX_TEXT_LENGTH) else 3
    seqSpacings = utils.find_sequence_duplicates(clean_text, min_length)
    if args.verbose:
        if args.all:
            print(seqSpacings)
        print("Extracting spacing divisors...")
    divisors = useful_divisors(flatten(list(seqSpacings.values())))
    divisorsCount = utils.repetitions(divisors)
    if args.exhaustive:
        return [x[0] for x in divisorsCount]
    return [x[0] for x in divisorsCount if x[0] <= KEY_LENGTH_THRESHOLD]

def subgroup(n, key_length):
    i = n - 1
    letters = []
    while i < len(clean_text):
        letters.append(clean_text[i])
        i += key_length
    return ''.join(letters)

def test(key_length):
    if args.verbose:
        print(f"Testing key length {key_length}")
    groups = []
    for n in range(1, key_length + 1):
        groups.append(subgroup(n, key_length))
    a = ord('A')
    key = ""
    for n, group in enumerate(groups):
        coef = utils.coincidence_index(group)
        if args.all:
            print(f"Subgroup {n + 1} (IC: {coef})\n{group}")
        best_subkey = ('A', 0)
        for i in range(MODULE):
            shift = (MODULE - i)%MODULE
            decrypt = caesar.caesar(group, shift)
            frequencies = utils.most_frequent_chars(decrypt)
            score = utils.match_score(''.join(map(lambda x: x[0], frequencies)))
            subkey = chr(a + i)
            if args.all:
                print(f"Testing subkey '{subkey}' with match score {round(100 * (score/MAX_SCORE))}%")
            if best_subkey[1] < score:
                best_subkey = (subkey, score)
        if args.all:
            print(f"Best subkey is '{best_subkey[0]}' with match score {round(100 * (best_subkey[1]/MAX_SCORE))}%")
        key += best_subkey[0]
    decrypt = vigenere(text, key)
    return (key, decrypt) if validator.is_valid(decrypt) else FAILED

def result(decrypted, terminal):
    if terminal:
        if args.verbose:
            validator.success()
            print(f"Key: {decrypted[0].upper()}")
        print(decrypted[1])
    return decrypted

def crack(text, terminal=True):
    args.decrypt = True
    frequencies = utils.most_frequent_chars(clean_text)
    if args.all:
        print(f"Frequencies: {frequencies}")
    (coef, key_avg) = friedman(clean_text, frequencies)
    if args.verbose:
        print(f"Text IC (Index of Coincidence): {coef}")
    PERMITTED_ERROR = 0.3 * (ENGLISH_IC - MIN_ENGLISH_IC)
    if coef >= ENGLISH_IC - PERMITTED_ERROR:
        if args.verbose:
            print(f"IC suggests that the text is encrypted with monoalphabetic cipher")
        tryCaesar = caesar_crack(text)
        if tryCaesar != FAILED:
            return result(tryCaesar, terminal)
    if key_avg > 0 and key_avg <= KEY_LENGTH_THRESHOLD:
        if args.verbose:
            print(f"Friedman test suggests a key length of {key_avg}")
        decrypted = test(key_avg)
        if decrypted != FAILED:
            return result(decrypted, terminal)
    if args.verbose:
        print("Kasiki examination")
    key_lengths = kasiki(text)
    if key_avg in key_lengths:
        key_lengths.remove(key_avg)
    if args.all:
        print("Kasiki possible key lengths (sorted by probability):")
        print(key_lengths)
    for key_length in key_lengths:
        decrypted = test(key_length)
        if decrypted != FAILED:
            return result(decrypted, terminal)
    if terminal:
        validator.fail()
        if not args.exhaustive:
            print("If you want to try more keys execute this program again with the option --exhaustive. \
However, it is worth noting that the longer the key is the more errors can have the cracked key. \
In addition, this program may have difficulties to crack keys on smaller texts in comparison with the key length.")
    return FAILED

if __name__ == "__main__":
    set_args()

    if args.key is not None and not args.key.isalpha():
        error("key must be alphabetic and non-empty")

    validator = Validator("en_US", args.threshold, args.debug, args.beep)
    text = read(args.text)
    clean_text = clean(text)
    size = len(text)

    if args.key is not None:
        print(vigenere(text, args.key))
    else:
        crack(text)
