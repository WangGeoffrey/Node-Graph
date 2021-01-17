import pygame
import math

pygame.init()
WIDTH = 600
SIDE_BAR = 100
WIN = pygame.display.set_mode((WIDTH+SIDE_BAR, WIDTH))
pygame.display.set_caption('Node Graph')
font = pygame.font.SysFont('Corbel', 15)

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
    def __init__(self, x_pos, y_pos, width, height, text):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))

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
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < range

def valid_pos(nodes, pos, exclude):
    in_nodes = set()
    for node in nodes:
        if check_in_range(node.get_pos(), pos, SIZE*3):
            in_nodes.add(node)
    if len(in_nodes.difference(exclude)) == 0:
        return True
    return False

def get_intersections(pos1, pos2):
    x0, y0 = pos1
    x1, y1 = pos2
    r = SIZE*3

    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
    a=(r**2-r**2+d**2)/(2*d)
    h=math.sqrt(r**2-a**2)
    x2=x0+a*(x1-x0)/d   
    y2=y0+a*(y1-y0)/d   
    x3=x2+h*(y1-y0)/d     
    y3=y2-h*(x1-x0)/d 

    x4=x2-h*(y1-y0)/d
    y4=y2+h*(x1-x0)/d
    
    return ((x3, y3), (x4, y4))

def main():
    WIN.fill(WHITE)

    buttons = []
    buttons.append(Button(WIDTH+1, 0, SIDE_BAR, WIDTH//3, 'Add'))
    buttons.append(Button(WIDTH+1, WIDTH//3, SIDE_BAR, WIDTH//3, 'Remove'))
    buttons.append(Button(WIDTH+1, 2*(WIDTH//3), SIDE_BAR, WIDTH//3, 'Connect'))
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
                            temp = buttons.index(button)+1
                            if temp == action:
                                action = 0
                            else:
                                action = temp
                elif move_node:
                    move_node = False

            if pygame.mouse.get_pressed()[0]:
                if not WIDTH < pos[0]:
                    if action == 1: #Add node
                        if SIZE*2 < pos[0] < WIDTH-SIZE*2 and SIZE*2 < pos[1] < WIDTH-SIZE*2:
                            outside = False
                            for node in nodes:
                                if check_in_range(node.get_pos(), pos, SIZE*3):
                                    outside = True
                                    break
                            if not outside:
                                nodes.append(Node(pos))
                                action = 0
                    elif action == 2: #Remove node
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
                    elif action == 3: #Connect nodes
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
                                        node_to_connect.select()
                                        toggle_second = False
                                else:
                                    node_to_connect = node
                                    node_to_connect.select()
                                    toggle_second = True
                                    break
                    elif move_node:
                        new_pos = pos
                        if not (SIZE*2 < pos[0] < WIDTH-SIZE*2 and SIZE*2 < pos[1] < WIDTH-SIZE*2):
                            new_x, new_y = pos
                            if SIZE*2 > pos[0]:
                                new_x = SIZE*2
                            elif pos[0] > WIDTH-SIZE*2:
                                new_x = WIDTH-SIZE*2
                            if SIZE*2 > pos[1]:
                                new_y = SIZE*2
                            elif pos[1] > WIDTH-SIZE*2:
                                new_y = WIDTH-SIZE*2
                            new_pos = (new_x, new_y)
                        if new_pos == pos:
                            intersecting = []
                            for node in nodes:
                                if check_in_range(node.get_pos(), pos, SIZE*3):
                                    if node != node_to_move:
                                        intersecting.append(node)
                            if len(intersecting) != 0:
                                if len(intersecting) == 1:
                                    if intersecting[0].get_pos() == pos:
                                        new_pos = prev_pos
                                    else:
                                        xx1, yy1 = intersecting[0].get_pos()
                                        xx2, yy2 = pos
                                        length = math.sqrt((xx1 - xx2)**2 + (yy1 - yy2)**2)
                                        length = SIZE/length
                                        xx3 = (xx2 - xx1) * length
                                        yy3 = (yy2 - yy1) * length
                                        new_pos = (xx1+xx3*3, yy1+yy3*3)
                                        exclude = {node_to_move, intersecting[0]}
                                        if not valid_pos(nodes, new_pos, exclude):
                                            find_new = []
                                            for node in nodes:
                                                if check_in_range(node.get_pos(), new_pos, SIZE*3):
                                                    if node != intersecting[0]:
                                                        find_new.append(node)
                                            poss = set()
                                            for other in find_new:
                                                temp1, temp2 = get_intersections(intersecting[0].get_pos(), other.get_pos())
                                                exclude = {intersecting[0], other, node_to_move}
                                                if valid_pos(nodes, temp1, exclude):
                                                    poss.add(temp1)
                                                if valid_pos(nodes, temp2, exclude):
                                                    poss.add(temp2)
                                            closest = SIZE*3
                                            closest_pos = (-1, -1)
                                            for tuple in poss:
                                                temp0 = math.sqrt((tuple[0] - pos[0])**2 + (tuple[1] - pos[1])**2)
                                                if closest > temp0:
                                                    closest = temp0
                                                    closest_pos = tuple
                                            new_pos = closest_pos
                                else:
                                    positions = set()
                                    for outer_index in range(len(intersecting)):
                                        for inner_index in range(outer_index + 1, len(intersecting)):
                                            intersect1, intersect2 = get_intersections(intersecting[outer_index].get_pos(), intersecting[inner_index].get_pos())
                                            exclude = {intersecting[outer_index], intersecting[inner_index], node_to_move}
                                            if valid_pos(nodes, intersect1, exclude):
                                                positions.add(intersect1)
                                            if valid_pos(nodes, intersect2, exclude):
                                                positions.add(intersect2)
                                    closest = SIZE*6
                                    closest_pos = (-1, -1)
                                    for p in positions:
                                        temp0 = math.sqrt((p[0] - pos[0])**2 + (p[1] - pos[1])**2)
                                        if closest > temp0:
                                            closest = temp0
                                            closest_pos = p
                                    if closest_pos == (-1, -1):
                                        new_pos = prev_pos
                                    else:
                                        new_pos = closest_pos
                        prev_pos = new_pos
                        node_to_move.move(new_pos)
                        for edge in node_to_move.get_edges():
                            edge.move()
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
            else:
                button.deselected()
            button.draw()
        pygame.draw.line(WIN, BLACK, (WIDTH, 0), (WIDTH, WIDTH))
        for i in range(4):
            pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//3), (WIDTH+SIDE_BAR, i*WIDTH//3))
    pygame.quit()

main()
