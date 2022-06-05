from helpful_files.geocoder import *
import pymorphy2


def process_arg():
    if len(sys.argv) > 1:
        return get_kind(get_address_pos('+'.join(sys.argv[1:])),
                        kind='district')
    else:
        print('Адрес не задан')
        sys.exit(0)


if __name__ == '__main__':
    address = ' '.join(sys.argv[1:])
    district = process_arg().split()
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(district[0])[0]
    word2 = morph.parse(district[1])[0]
    print(f'Адрес "{address}" находится в '
          f'{word.inflect({"loct", "masc"}).word.capitalize()} '
          f'{word2.inflect({"loct"}).word}')