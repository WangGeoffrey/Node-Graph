import pygame
import math

pygame.init()
WIDTH = 600
WIN = pygame.display.set_mode((WIDTH+100, WIDTH))
pygame.display.set_caption('Node Graph')
font = pygame.font.SysFont('Corbel',15)

BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHTER = (200, 200, 200)
WHITE = (255, 255, 255)

SIZE = 20

class Node:
    def __init__(self, pos):
        self.pos = pos
        self.color = GREY
        self.edges = set()

    def get_pos(self):
        return self.pos

    def select(self):
        if self.color == GREY:
            self.color = LIGHTER
        else:
            self.color = GREY

    def get_edges(self):
        return self.edges

    def move(self, pos):
        self.erase()
        self.pos = pos

    def connect(self, edge):
        self.edges.add(edge)

    def update_edges(self, edges):
        self.edges = self.edges.intersection(edges)

    def draw(self):
        pygame.draw.circle(WIN, self.color, self.pos, SIZE)

    def erase(self):
        pygame.draw.circle(WIN, WHITE, self.pos, SIZE)

class Edge:
    def __init__(self, first, second):
        self.color = BLACK
        self.connecting = {first, second}
        self.position = {first.get_pos(), second.get_pos()}

    def get_connecting(self):
        return self.connecting

    def get_ends(self):
        return tuple(self.connecting)

    def get_poss(self):
        return tuple(self.position)

    def move(self):
        self.erase()
        first, second = self.get_ends()
        self.position = {first.get_pos(), second.get_pos()}
    
    def draw(self):
        first, second = self.get_poss()
        pygame.draw.line(WIN, self.color, first, second)

    def erase(self):
        first, second = self.get_poss()
        pygame.draw.line(WIN, WHITE, first, second)

class Button:
    def __init__(self, x_pos, y_pos, height, width, text):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.height = height
        self.width = width
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, height, width)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + height//2, y_pos + width//2))

    def get_rect(self):
        return self.rect

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        WIN.blit(self.text, self.text_rect)

    def selected(self):
        self.color = GREY

    def deselected(self):
        self.color = WHITE

def draw_graph(nodes, edges):
    for edge in edges:
        edge.draw()
    for node in nodes:
        node.draw()
        text = font.render(str(nodes.index(node)+1) , True , BLACK)
        text_rect = text.get_rect(center=node.get_pos())
        WIN.blit(text, text_rect)
    pygame.display.update()

def check_in_range(pos1, pos2, range):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt(abs(x1 - x2)*abs(x1 - x2) + abs(y1 - y2)*abs(y1 - y2)) < range

def main():
    WIN.fill(WHITE)

    buttons = []
    buttons.append(Button(WIDTH+1, 0, 100, WIDTH//3, 'Add'))
    buttons.append(Button(WIDTH+1, WIDTH//3, 100, WIDTH//3, 'Remove'))
    buttons.append(Button(WIDTH+1, 2*(WIDTH//3), 100, WIDTH//3, 'Connect'))
    action = 0

    nodes = []
    edges = set()
    move_node = False
    toggle_second = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if WIDTH < pos[0]:
                    for button in buttons:
                        if button.get_rect().collidepoint(event.pos):
                            action = buttons.index(button)+1
                elif move_node:
                    move_node = False

            if pygame.mouse.get_pressed()[0]:
                if not WIDTH < pos[0]:
                    if action == 1:
                        if 50 < pos[0] < WIDTH-50 and 50 < pos[1] < WIDTH-50:
                            nodes.append(Node(pos))
                            action = 0
                    elif action == 2:
                        for node in nodes:
                            if check_in_range(node.get_pos(), pos, SIZE):
                                node.erase()
                                nodes.remove(node)
                                for edge in node.get_edges():
                                    edge.erase()
                                edges = edges.difference(node.get_edges())
                                action = 0
                                break
                        if action != 2:
                            for node in nodes:
                                node.update_edges(edges)
                    elif action == 3:
                        for node in nodes:
                            if check_in_range(node.get_pos(), pos, SIZE):
                                if toggle_second:
                                    if node != node_to_connect:
                                        edge = Edge(node, node_to_connect)
                                        valid = True
                                        for existing_edge in node.get_edges():
                                            if existing_edge.get_connecting() == edge.get_connecting():
                                                valid = False
                                                break
                                        if valid:
                                            node_to_connect.select()
                                            node.connect(edge)
                                            node_to_connect.connect(edge)
                                            edges.add(edge)
                                            action = 0
                                            toggle_second = False
                                            break
                                else:
                                    node_to_connect = node
                                    node_to_connect.select()
                                    toggle_second = True
                                    break
                    elif move_node:
                        for edge in edges:
                            edge.move()
                        node_to_move.move(pos)
                    else:
                        for node in nodes:
                            if check_in_range(node.get_pos(), pos, SIZE):
                                move_node = True
                                node_to_move = node
                                break

        draw_graph(nodes, edges)

        for button in buttons:
            if button.get_rect().collidepoint(pos) or action == buttons.index(button)+1:
                button.selected()
                button.draw()
            else:
                button.deselected()
                button.draw()

        pygame.display.update()

main()
