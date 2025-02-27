import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('keyboard ctrl')
screen.fill((0, 0, 0))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("exit")
            sys.exit()

    keys = pygame.key.get_pressed()

    # 方法1：直接使用pygame的字母键常量
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if keys[getattr(pygame, f'K_{letter.lower()}')]:
            print(f"按下了: {letter}")

    # 方法2：使用ASCII码范围检测
    for i in range(97, 123):  # ASCII码 a-z: 97-122
        if keys[i]:
            print(f"按下了: {chr(i).upper()}")

    # 方法3：使用pygame内置的key_code检测（推荐）
    pressed_keys = []
    for key_code in range(len(keys)):
        if keys[key_code]:
            key_name = pygame.key.name(key_code)
            if len(key_name) == 1 and key_name.isalpha():
                pressed_keys.append(key_name.upper())
    if pressed_keys:
        print(f"当前按下的字母: {', '.join(pressed_keys)}")

    # 打印按键状态数组（0表示未按下，1表示按下）
    for i, is_pressed in enumerate(keys):
        if is_pressed:  # 只打印被按下的键
            key_name = pygame.key.name(i)  # 获取按键名称
            print(f"Key {i} ({key_name}): {is_pressed}")
    
    for i in range(26):
        if keys[pygame.K_a + i]:  # 检测从 A 到 Z 的按键
            print(chr(pygame.K_a + i))

    # 检测上下左右键
    if keys[pygame.K_UP]:
        print("Up arrow")
    if keys[pygame.K_DOWN]:
        print("Down arrow")
    if keys[pygame.K_LEFT]:
        print("Left arrow")
    if keys[pygame.K_RIGHT]:
        print("Right arrow")

    # 按下 'Esc' 退出程序
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()