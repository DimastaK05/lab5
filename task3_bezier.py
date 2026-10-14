import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Составная кубическая кривая Безье")
clock = pygame.time.Clock()

BG = (250, 250, 252)
INK = (35, 40, 48)
CURVE = (48, 105, 190)
ANCHOR = (220, 75, 65)
GUIDE = (185, 190, 200)
POINT_R = 7
HIT_R = 13
SAMPLES = 70


anchors = [(120, 430), (300, 210), (500, 440), (700, 180), (880, 390)]
drag_index = None
show_guides = True


def bezier(p0, p1, p2, p3, t):
    """Точка кубической кривой Безье по полиному Бернштейна."""
    u = 1.0 - t
    return (
        u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
        u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1],
    )


def make_segments(points):
    """Построить гладкую составную кривую через заданные опорные точки."""
    if len(points) < 2:
        return []
    result = []
    for i in range(len(points) - 1):
        p0, p3 = points[i], points[i + 1]
        before = points[i - 1] if i > 0 else points[0]
        after = points[i + 2] if i + 2 < len(points) else points[-1]


        c1 = (p0[0] + (p3[0] - before[0]) / 6,
              p0[1] + (p3[1] - before[1]) / 6)
        c2 = (p3[0] - (after[0] - p0[0]) / 6,
              p3[1] - (after[1] - p0[1]) / 6)
        result.append((p0, c1, c2, p3))
    return result


def nearest_anchor(pos):
    for i, p in enumerate(anchors):
        if (p[0] - pos[0])**2 + (p[1] - pos[1])**2 <= HIT_R**2:
            return i
    return None


def draw_text(text, pos, font, color=INK):
    screen.blit(font.render(text, True, color), pos)


def draw():
    screen.fill(BG)
    global show_guides
    font = pygame.font.SysFont("arial", 16)
    small = pygame.font.SysFont("arial", 14)
    segments = make_segments(anchors)


    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (238, 239, 243), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (238, 239, 243), (0, y), (WIDTH, y), 1)


    for p0, c1, c2, p3 in segments:
        if show_guides:
            pygame.draw.line(screen, GUIDE, p0, c1, 1)
            pygame.draw.line(screen, GUIDE, p3, c2, 1)
            pygame.draw.circle(screen, GUIDE, (round(c1[0]), round(c1[1])), 3)
            pygame.draw.circle(screen, GUIDE, (round(c2[0]), round(c2[1])), 3)

        previous = None
        for j in range(SAMPLES + 1):
            point = bezier(p0, c1, c2, p3, j / SAMPLES)
            point = (round(point[0]), round(point[1]))
            if previous is not None:
                pygame.draw.line(screen, CURVE, previous, point, 3)
            previous = point

    for i, p in enumerate(anchors):
        color = (245, 145, 55) if i == drag_index else ANCHOR
        pygame.draw.circle(screen, color, p, POINT_R)
        pygame.draw.circle(screen, (255, 255, 255), p, 3)
        draw_text(str(i + 1), (p[0] + 9, p[1] - 18), small)

    draw_text("ЛКМ: добавить точку / перетащить опорную точку", (12, 10), font)
    draw_text("ПКМ по точке: удалить    H: скрыть/показать направляющие    C: сбросить",
              (12, 32), font)
    draw_text(f"Опорных точек: {len(anchors)}", (12, 56), small, (90, 95, 105))
    pygame.display.flip()


def main():
    global drag_index, anchors, show_guides
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    idx = nearest_anchor(event.pos)
                    if idx is None:
                        anchors.append(event.pos)
                    else:
                        drag_index = idx
                elif event.button == 3:
                    idx = nearest_anchor(event.pos)
                    if idx is not None:
                        anchors.pop(idx)
                        drag_index = None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag_index = None
            elif event.type == pygame.MOUSEMOTION and drag_index is not None:
                if drag_index < len(anchors):
                    anchors[drag_index] = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    anchors = []
                    drag_index = None
                elif event.key == pygame.K_h:
                    show_guides = not show_guides
        draw()
        clock.tick(60)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
