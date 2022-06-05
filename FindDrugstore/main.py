from helpful_files.geocoder import *
import pygame


def process_arg():
    if len(sys.argv) > 1:
        address = '+'.join(sys.argv[1:])
        address_pos = get_address_pos(address)
        org = get_organization(get_address_pos(address))
        data = get_organization_data(org)
        text = [f'Адрес: {data[0]}', f'Название организации: {data[1]}',
                f'Часы работы: {data[2]}',
                f'Расстояние до организации: '
                f'{lonlat_distance(address_pos, data[-1])} км']
        return get_image(address, points=[data[-1]]), text
    else:
        print('Адрес не задан')
        sys.exit(0)


def main():
    img, data_to_display = process_arg()
    pygame.init()
    pygame.display.set_caption('Поиск аптеки 2')
    img = pygame.transform.scale(img, (img.get_width() * 2,
                                       img.get_height() * 2))
    screen = pygame.display.set_mode(img.get_size())
    screen.blit(img, (0, 0))
    font = pygame.font.Font(None, 20)
    y = 0
    for i in range(len(data_to_display)):
        caption = font.render(data_to_display[i],
                              True, pygame.Color('black'))
        screen.blit(caption, (0, y))
        y += caption.get_height() + 5
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()


if __name__ == '__main__':
    main()