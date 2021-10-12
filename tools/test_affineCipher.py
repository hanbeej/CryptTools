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
    parser.add_argument("-k", "--key", help="암호화에 사용되는 A값.", type=int)
    parser.add_argument("-l", "--lang", help=f"available languages: {enchant.list_languages()} (default: en_US). 키가 제공되지 않은 경우에만 유용함", default='en_US')
    parser.add_argument("-z", "--affine", help="암호화에 사용되는 B값",type=int)
    parser.add_argument("-V", "--verbose", action='store_true', help="여분의 정보를 알려줌")
    parser.add_argument("-A", "--all", action='store_true', help="테스트된 각 키에 대해 해독된 텍스트 표시")
    parser.add_argument("-D", "--debug", action='store_true', help="텍스트 유효성 확인에 대한 정보 표시")
    parser.add_argument("-T", "--threshold", help="전체 텍스트에 유효한 단어 수 비율 (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="프로그램이 끝나면 삐 소리가 난다. SOX를 설치해야 할 수 있음")
    args = parser.parse_args()



def affineCipher(text, shift, affine):
    """Encrypts/Decrypts a `text` using the caesar substitution cipher with specified `shift` key"""
    if shift < 0 or shift > MODULE:
        error(f"key must be between 0 and {MODULE}")
    return ''.join(map(lambda char: shift_by_affine(char, shift, affine), text))

if __name__ == "__main__":
    set_args()

    validator = Validator(args.lang, args.threshold, args.debug, args.beep)
    text = read(args.text)

    if args.key is not None:
        if args.verbose:
            print(f"Original text most frequent character: {most_frequent_char(clean(text))}\n")
        encrypted = affineCipher(text, args.key, args.affine)
        print(encrypted)
        if args.verbose:
            print(f"\nEncrypted text most frequent character: {most_frequent_char(clean(encrypted))}")
    
