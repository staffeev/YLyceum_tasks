from helpful_files.geocoder import *
import pygame


def process_arg():
    if len(sys.argv) > 1:
        address = '+'.join(sys.argv[1:])
        org = get_organization(get_address_pos(address))
        data = [get_organization_data(i) for i in org]
        points = [f'{i[0][0]},{i[0][1]},' + 'pm2grm' if 'нет данных' in i[1]
                  else f'{i[0][0]},{i[0][1]},' + 'pm2gnm' if 'круглосуточно'
                                                             in i[1] else
                  f'{i[0][0]},{i[0][1]},' + 'pm2blm' for i in data]
        return get_image(address, points=points)
    else:
        print('Адрес не задан')
        sys.exit(0)


def main():
    img = process_arg()
    pygame.init()
    pygame.display.set_caption('Поиск аптеки 2')
    screen = pygame.display.set_mode(img.get_size())
    screen.blit(img, (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()


if __name__ == '__main__':
    main()