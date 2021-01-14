import pygame
import math

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH+100, WIDTH))
pygame.display.set_caption('Node Graph')

BLACK = (0, 0, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)

class Node:
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = GREY
        self.connected = set()

    def move(self, pos):
        self.erase()
        self.x_pos, self.y_pos = pos

    def connect(self, node):
        self.connected.add(node)

    def draw(self):
        pygame.draw.circle(WIN, self.color, (self.x_pos, self.y_pos), 25)

    def erase(self):
        pygame.draw.circle(WIN, WHITE, (self.x_pos, self.y_pos), 25)

class Edge:
    def __init__(self, first, second):
        self.start = (first.x_pos, first.y_pos)
        self.end = (second.x_pos, second.y_pos)
        self.color = BLACK
        self.connecting = (first, second)

    def move(self, node):
        self.erase()
        if node == self.connecting[0]:
            self.start = (node.x_pos, node.y_pos)
        elif node == self.connecting[1]:
            self.end = (node.x_pos, node.y_pos)
    
    def draw(self):
        pygame.draw.line(WIN, self.color, self.start, self.end)

    def erase(self):
        pygame.draw.line(WIN, WHITE, self.start, self.end)

def draw_graph(nodes, edges):
    for edge in edges:
        edge.draw()
    count = 1
    pygame.init()
    font = pygame.font.SysFont('Corbel',15)
    for node in nodes:
        node.draw()
        text = font.render(str(count) , True , BLACK)
        text_rect = text.get_rect(center=(node.x_pos, node.y_pos))
        WIN.blit(text, text_rect)
        count += 1
    pygame.display.update()

def main():
    WIN.fill(WHITE)
    pygame.init()
    font = pygame.font.SysFont('Corbel',15)
    text1 = font.render('Add' , True , BLACK)
    text1_rect = text1.get_rect(center=(WIDTH+50, WIDTH//6))
    text2 = font.render('Remove' , True , BLACK)
    text2_rect = text2.get_rect(center=(WIDTH+50, WIDTH//2))
    text3 = font.render('Connect' , True , BLACK)
    text3_rect = text3.get_rect(center=(WIDTH+50, (WIDTH//6)*5))

    nodes = []
    edges = set()
    toggle_second = False
    toggle1 = False
    toggle2 = False
    toggle3 = False
    
    add_node = False
    remove_node = False
    connect_node = False
    move_node = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                if WIDTH < pos[0]:
                    if 0 < pos[1] <= WIDTH//3 and not (remove_node or connect_node) and toggle1:
                        toggle1 = False
                        add_node = True
                    elif WIDTH//3 < pos[1] <= 2*(WIDTH//3) and not (add_node or connect_node) and toggle2:
                        toggle2 = False
                        remove_node = True
                    elif 2*(WIDTH//3) < pos[1] <= WIDTH and not (add_node or remove_node) and toggle3:
                        toggle3 = False
                        connect_node = True
                elif move_node:
                    move_node = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if WIDTH < pos[0]:
                        if 0 < pos[1] <= WIDTH//3 and not (remove_node or connect_node):
                            toggle1 = True
                        elif WIDTH//3 < pos[1] <= 2*(WIDTH//3) and not (add_node or connect_node):
                            toggle2 = True
                        elif 2*(WIDTH//3) < pos[1] <= WIDTH and not (add_node or remove_node):
                            toggle3 = True

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if not WIDTH < pos[0]:
                    if add_node:
                        if 50 < pos[0] < WIDTH-50 and 50 < pos[1] < WIDTH-50:
                            nodes.append(Node(pos[0], pos[1]))
                            add_node = False
                    elif remove_node:
                        for node in nodes:
                            if math.sqrt(abs(node.x_pos - pos[0])*abs(node.x_pos - pos[0]) + abs(node.y_pos - pos[1])*abs(node.y_pos - pos[1])) < 25:
                                node.erase()
                                nodes.remove(node)
                                remove_node = False
                                break
                    elif connect_node:
                        for node in nodes:
                            if math.sqrt(abs(node.x_pos - pos[0])*abs(node.x_pos - pos[0]) + abs(node.y_pos - pos[1])*abs(node.y_pos - pos[1])) < 25:
                                if toggle_second:
                                    edge = Edge(node, node_to_connect)
                                    node_to_connect.color = GREY
                                    node.connect(edge)
                                    node_to_connect.connect(edge)
                                    edges.add(edge)
                                    connect_node = False
                                    toggle_second = False
                                    break
                                else:
                                    node_to_connect = node
                                    node_to_connect.color = (200, 200, 200)
                                    toggle_second = True
                                    break
                    elif move_node:
                        for edge in edges:
                            if edge.connecting[0] == node_to_move or edge.connecting[1] == node_to_move:
                                edge.move(node_to_move)
                                break
                        node_to_move.move(pos)
                    else:
                        for node in nodes:
                            if math.sqrt(abs(node.x_pos - pos[0])*abs(node.x_pos - pos[0]) + abs(node.y_pos - pos[1])*abs(node.y_pos - pos[1])) < 25:
                                move_node = True
                                node_to_move = node
                                break

        draw_graph(nodes, edges)

        mouse = pygame.mouse.get_pos()

        if WIDTH < mouse[0] and 0 < mouse[1] <= WIDTH//3 or add_node:
            pygame.draw.rect(WIN, GREY, (WIDTH+1, 0, 100, WIDTH//3))
        else:
            pygame.draw.rect(WIN, WHITE, (WIDTH+1, 0, 100, WIDTH//3))
        WIN.blit(text1, text1_rect)

        if WIDTH < mouse[0] and WIDTH//3 < mouse[1] <= 2*(WIDTH//3) or remove_node:
            pygame.draw.rect(WIN, GREY, (WIDTH+1, WIDTH//3, 100, WIDTH//3))
        else:
            pygame.draw.rect(WIN, WHITE, (WIDTH+1, WIDTH//3, 100, WIDTH//3))
        WIN.blit(text2, text2_rect)

        if WIDTH < mouse[0] and 2*(WIDTH//3) < mouse[1] <= WIDTH or connect_node:
            pygame.draw.rect(WIN, GREY, (WIDTH+1, 2*(WIDTH//3), 100, WIDTH//3))
        else:
            pygame.draw.rect(WIN, WHITE, (WIDTH+1, 2*(WIDTH//3), 100, WIDTH//3))
        WIN.blit(text3, text3_rect)

        pygame.display.update()
main()