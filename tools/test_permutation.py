
import sys
sys.path.insert(0, "../lib")
from utils import *
from validator import *
import argparse
import enchant

def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="암호화할 텍스트를 입력. 텍스트 입력값은 최대 9자리.")
    parser.add_argument("-k", "--key", help="텍스트를 암호화할 키값을 입력. ", type=int)
    parser.add_argument("-l", "--lang", help=f"사용가능한 언어: {enchant.list_languages()} (default: en_US). 현재 영어만 제공", default='en_US')
    parser.add_argument("-V", "--verbose", action='store_true', help="여분의 정보를 알려줌")
    parser.add_argument("-A", "--all", action='store_true', help="테스트된 각 키에 대해 해독된 텍스트 표시")
    parser.add_argument("-D", "--debug", action='store_true', help="텍스트 유효성 확인에 대한 정보 표시")
    parser.add_argument("-T", "--threshold", help="전체 텍스트에 유효한 단어 수 비율 (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="프로그램이 끝나면 삐 소리가 난다. SOX를 설치해야 할 수 있음")
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
