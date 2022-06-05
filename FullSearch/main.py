from helpful_files.geocoder import *
import pygame


def process_arg():
    if len(sys.argv) > 1:
        return get_image('+'.join(sys.argv[1:]))
    else:
        print('Адрес не задан')
        sys.exit(0)


def main():
    img = process_arg()
    pygame.init()
    pygame.display.set_caption('Картинка')
    screen = pygame.display.set_mode((600, 450))
    screen.blit(img, (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()


if __name__ == '__main__':
    main()