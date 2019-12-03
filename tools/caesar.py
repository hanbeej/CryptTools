#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../lib")
from utils import *
from validator import *
import argparse
import enchant

def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="읽을 문자 지정되지 않은 경우 프로그램이 표준 입력에서 읽힌다.")
    parser.add_argument("-k", "--key", help="암호화에 사용되는 키. 키가 제공되지 않으면 프로그램에서 지정된 언어를 사용하여 암호를 해독하려고 시도함", type=int)
    parser.add_argument("-l", "--lang", help=f"available languages: {enchant.list_languages()} (default: en_US). 키가 제공되지 않은 경우에만 유용함", default='en_US')
    parser.add_argument("-V", "--verbose", action='store_true', help="여분의 정보를 알려줌")
    parser.add_argument("-A", "--all", action='store_true', help="테스트된 각 키에 대해 해독된 텍스트 표시")
    parser.add_argument("-D", "--debug", action='store_true', help="텍스트 유효성 확인에 대한 정보 표시")
    parser.add_argument("-T", "--threshold", help="전체 텍스트에 유효한 단어 수 비율 (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="프로그램이 끝나면 삐 소리가 난다. SOX를 설치해야 할 수 있음")
    args = parser.parse_args()

def caesar(text, shift):
    """Encrypts/Decrypts a `text` using the caesar substitution cipher with specified `shift` key"""
    if shift < 0 or shift > MODULE:
        error(f"key must be between 0 and {MODULE}")
    return ''.join(map(lambda char: shift_by(char, shift), text))

def crack(text, terminal=True):
    """Cracks the text that must be encrypted with the caesar cipher"""
    shifts = reversed_shifts(clean(text), args.verbose)
    for i, shift in enumerate(shifts):
        decrypt = caesar(text, shift)
        if args.verbose:
            sys.stdout.write("\r")
            sys.stdout.write(f"Testing '{FREQUENCY_ALPHABET[i]}' (ROT-{shift})       ")
            sys.stdout.flush()
        if args.all:
            print(f'Testing decrypted text:\n"{decrypt}"')
        if args.verbose and args.debug:
            print()
        if validator.is_valid(decrypt):
            encryptionKey = (MODULE - shift)%MODULE
            if terminal:
                if args.verbose:
                    validator.success()
                    if args.debug:
                        print()
                    print(f'Decrypted with ROT-{shift}. Original encryption key: {encryptionKey}')
                print(decrypt)
            return (encryptionKey, decrypt)
        if args.debug:
            print()
    if args.verbose and not args.debug:
            print()
    if terminal:
        validator.fail()
    return FAILED

if __name__ == "__main__":
    set_args()

    validator = Validator(args.lang, args.threshold, args.debug, args.beep)
    text = read(args.text)

    if args.key is not None:
        if args.verbose:
            print(f"Original text most frequent character: {most_frequent_char(clean(text))}\n")
        encrypted = caesar(text, args.key)
        print(encrypted)
        if args.verbose:
            print(f"\nEncrypted text most frequent character: {most_frequent_char(clean(encrypted))}")
    else:
        crack(text)
