from helpful_files.geocoder import *
import pygame
from random import choice


CITIES = ['Москва', 'Санкт-Петербург', 'Нью-Йорк', 'Чикаго', 'Канберра',
          'Новороссийск', 'Пекин', 'Сидней', 'Генуя', 'Рига']


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Угадай-ка город')
    screen = pygame.display.set_mode((600, 450))
    pygame.display.flip()
    running = True
    cur_city = choice(CITIES)
    pos = get_random_coords(cur_city)
    picture = get_image(cur_city, ll=pos)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                cur_city = choice(list(set(CITIES) - {cur_city}))
                pos = get_random_coords(cur_city)
                picture = get_image(cur_city, ll=pos)
        screen.blit(picture, (0, 0))
        pygame.display.flip()
    pygame.quit()