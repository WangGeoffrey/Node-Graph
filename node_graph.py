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

def in_range(pos1, pos2, range):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < range

def valid_pos(nodes, pos, exclude):
    if not (SIZE*2 <= pos[0] <= WIDTH-SIZE*2 and SIZE*2 <= pos[1] <= WIDTH-SIZE*2):
        return False
    for node in nodes:
        if in_range(node.get_pos(), pos, SIZE*3):
            if not node in exclude:
                return False
    return True

def closest_valid_pos(nodes, pos, node_to_move):
    x, y = pos
    new_pos = pos
    valid = set()
    invalid = set()
    intersecting = set()
    in_display = SIZE*2 <= x <= WIDTH-SIZE*2 and SIZE*2 <= y <= WIDTH-SIZE*2
    for node in nodes:
        if in_range(pos, node.get_pos(), SIZE*3):
            if node != node_to_move:
                intersecting.add(node)
    if in_display and not bool(intersecting):
        return pos
    elif not in_display and not bool(intersecting):
        if SIZE*2 > x:
            x = SIZE*2
        elif x > WIDTH-SIZE*2:
            x = WIDTH-SIZE*2
        if SIZE*2 > y:
            y = SIZE*2
        elif y > WIDTH-SIZE*2:
            y = WIDTH-SIZE*2
        new_pos = (x, y)
        if valid_pos(nodes, new_pos, {node_to_move}):
            return new_pos
    elif in_display and len(intersecting) == 1:
        node = intersecting.pop()
        if pos == node.get_pos():
            return None
        x1, y1 = node.get_pos()
        scale = 3*SIZE/math.sqrt((x - x1)**2 + (y - y1)**2)
        new_pos = (x1+(x-x1)*scale, y1+(y-y1)*scale)
        if valid_pos(nodes, new_pos, {node, node_to_move}):
            return new_pos
    valid, invalid = get_positions(nodes, new_pos, node_to_move, set(), set())
    closest = WIDTH
    closest_pos = None
    for p in valid:
        temp = math.sqrt((p[0] - x)**2 + (p[1] - y)**2)
        if closest > temp:
            closest = temp
            closest_pos = p
    return closest_pos

def get_positions(nodes, pos, node_to_move, valid, invalid):
    intersecting = set()
    direction = None # (horizontal, vertical)
    if not (SIZE*2 < pos[0] < WIDTH-SIZE*2 and SIZE*2 < pos[1] < WIDTH-SIZE*2):
        a = b = 0
        if SIZE*2 >= pos[0]:
            a = -1
        elif pos[0] >= WIDTH-SIZE*2:
            a = 1
        if SIZE*2 >= pos[1]:
            b = -1
        elif pos[1] >= WIDTH-SIZE*2:
            b = 1
        direction = (a, b)
    for node in nodes:
        if in_range(pos, node.get_pos(), SIZE*3):
            if node != node_to_move:
                intersecting.add(node)
    if not bool(direction):
        while bool(intersecting):
            temp = intersecting.pop()
            for node in intersecting:
                pos1, pos2 = get_intersections(temp, node)
                if pos1 in valid or pos1 in invalid:
                    pass
                elif valid_pos(nodes, pos1, {node_to_move, temp, node}):
                    valid.add(pos1)
                else:
                    invalid.add(pos1)
                    valid, invalid = get_positions(nodes, pos1, node_to_move, valid, invalid)
                if pos2 in valid or pos2 in invalid:
                    pass
                elif valid_pos(nodes, pos2, {node_to_move, temp, node}):
                    valid.add(pos2)
                else:
                    invalid.add(pos2)
                    valid, invalid = get_positions(nodes, pos2, node_to_move, valid, invalid)
        return valid, invalid
    else:
        positions = set()
        while bool(intersecting):
            temp = intersecting.pop()
            x1, y1 = temp.get_pos()
            x, y = pos
            base1 = base2 = 0
            if direction[1] != 0:
                y = WIDTH/2 + direction[1]*(WIDTH/2 - SIZE*2)
                base1 = math.sqrt((SIZE*3)**2 - (y1 - y)**2)
            if direction[0] != 0:
                x = WIDTH/2 + direction[0]*(WIDTH/2 - SIZE*2)
                base2 = math.sqrt((SIZE*3)**2 - (x1 - x)**2)
            if direction[0] != 0 and direction[1] != 0: # Corner
                positions.add((x, y1-direction[1]*base2))
                positions.add((x1-direction[0]*base1, y))
            elif direction[0] != 0: # Horizontal
                positions.add((x, y1-base2))
                positions.add((x, y1+base2))
            elif direction[1] != 0: # Vertical
                positions.add((x1-base1, y))
                positions.add((x1-base1, y))
            while bool(positions):
                temp0 = positions.pop()
                if temp0 in valid or temp0 in invalid:
                    pass
                elif valid_pos(nodes, temp0, {temp, node_to_move}):
                    valid.add(temp0)
                else:
                    invalid.add(temp0)
                    valid, invalid = get_positions(nodes, temp0, node_to_move, valid, invalid)
            for node in intersecting:
                pos1, pos2 = get_intersections(temp, node)
                if pos1 in valid or pos1 in invalid:
                    pass
                elif valid_pos(nodes, pos1, {node_to_move, temp, node}):
                    valid.add(pos1)
                else:
                    invalid.add(pos1)
                    valid, invalid = get_positions(nodes, pos1, node_to_move, valid, invalid)
                if pos2 in valid or pos2 in invalid:
                    pass
                elif valid_pos(nodes, pos2, {node_to_move, temp, node}):
                    valid.add(pos2)
                else:
                    invalid.add(pos2)
                    valid, invalid = get_positions(nodes, pos2, node_to_move, valid, invalid)
        return valid, invalid

def get_intersections(node1, node2):
    x0, y0 = node1.get_pos()
    x1, y1 = node2.get_pos()
    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
    a=d/2
    h=math.sqrt((SIZE*3)**2-a**2)
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
    prev_pos = (-1, -1)
    move_node = False
    toggle_connect = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            x, y = pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                if WIDTH < x:
                    for button in buttons:
                        if button.get_rect().collidepoint(event.pos):
                            temp = buttons.index(button)+1
                            if temp == action:
                                action = 0
                            else:
                                action = temp
                                if toggle_connect:
                                    toggle_connect = False
                                    node_to_connect.select()
                elif move_node:
                    move_node = False
            if pygame.mouse.get_pressed()[0]:
                if not WIDTH < x:
                    if action == 1: #Add node
                        if SIZE*2 < x < WIDTH-SIZE*2 and SIZE*2 < y < WIDTH-SIZE*2:
                            outside = False
                            for node in nodes:
                                if in_range(node.get_pos(), pos, SIZE*3):
                                    outside = True
                                    break
                            if not outside:
                                nodes.append(Node(pos))
                                action = 0
                    elif action == 2: #Remove node
                        for node in nodes:
                            if in_range(node.get_pos(), pos, SIZE):
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
                            if in_range(node.get_pos(), pos, SIZE):
                                if toggle_connect:
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
                                            toggle_connect = False
                                            break
                                    else:
                                        node_to_connect.select()
                                        toggle_connect = False
                                else:
                                    node_to_connect = node
                                    node_to_connect.select()
                                    toggle_connect = True
                                    break
                    elif move_node:
                        new_pos = closest_valid_pos(nodes, pos, node_to_move)
                        if not bool(new_pos):
                            new_pos = prev_pos
                        node_to_move.move(new_pos)
                        prev_pos = new_pos
                        for edge in node_to_move.get_edges():
                            edge.move()
                    else:
                        for node in nodes:
                            if in_range(node.get_pos(), pos, SIZE):
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
