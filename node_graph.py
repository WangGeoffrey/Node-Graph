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
LIGHTGREY = (192, 192, 192)
WHITE = (255, 255, 255)

SIZE = 20 #Node radius

class Node:
    def __init__(self, pos):
        self.pos = pos
        self.color = GREY
        self.edges = set()

    def get_pos(self):
        return self.pos

    def select(self):
        if self.color == GREY:
            self.color = LIGHTGREY
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
    def __init__(self, node1, node2):
        self.color = BLACK
        self.connecting = {node1, node2}
        self.start_pos = node1.get_pos()
        self.end_pos = node2.get_pos()

    def get_connecting(self):
        return self.connecting

    def move(self):
        self.erase()
        node1, node2 = self.connecting
        self.start_pos = node1.get_pos()
        self.end_pos = node2.get_pos()
    
    def draw(self):
        pygame.draw.line(WIN, self.color, self.start_pos, self.end_pos)

    def erase(self):
        pygame.draw.line(WIN, WHITE, self.start_pos, self.end_pos)

class Button:
    def __init__(self, x_pos, y_pos, width, height, text):
        self.color = WHITE
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.text = font.render(text, True, BLACK)
        self.text_rect = self.text.get_rect(center=(x_pos + width//2, y_pos + height//2))

    def get_rect(self):
        return self.rect

    def click(self):
        if self.is_selected():
            self.deselect()
        else:
            self.select()

    def select(self):
        self.color = GREY

    def deselect(self):
        self.color = WHITE

    def is_selected(self):
        return self.color == GREY

    def hovered(self):
        if not self.is_selected():
            self.color = LIGHTGREY

    def clear(self):
        if not self.is_selected():
            self.color = WHITE

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        WIN.blit(self.text, self.text_rect)

class Button2(Button):
    def __init__(self, x_pos, y_pos, width, height, text, alt_text):
        super(Button2, self).__init__(x_pos, y_pos, width, height, text)
        self.alt_text = font.render(alt_text, True, BLACK)

    def click(self):
        temp = self.text
        self.text = self.alt_text
        self.alt_text = temp

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
        if in_range(pos, node.get_pos(), SIZE*3):
            if not node in exclude:
                return False
    return True

def closest_valid_pos(nodes, pos, node_to_move): #helper function of get_positions()
    x, y = pos
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
        a, b = x, y
        if SIZE*2 > x:
            a = SIZE*2
        elif x > WIDTH-SIZE*2:
            a = WIDTH-SIZE*2
        if SIZE*2 > y:
            b = SIZE*2
        elif y > WIDTH-SIZE*2:
            b = WIDTH-SIZE*2
        pos = (a, b)
        if valid_pos(nodes, pos, {node_to_move}):
            return pos
    elif in_display and len(intersecting) == 1:
        node = intersecting.pop()
        if pos == node.get_pos():
            return None
        x1, y1 = node.get_pos()
        scale = 3*SIZE/math.sqrt((x - x1)**2 + (y - y1)**2)
        pos = (x1+(x-x1)*scale, y1+(y-y1)*scale)
        if valid_pos(nodes, pos, {node, node_to_move}):
            return pos
    valid, invalid = get_positions(nodes, pos, node_to_move, set(), set())
    closest = (WIDTH, None)
    for p in valid:
        dist = math.sqrt((p[0] - x)**2 + (p[1] - y)**2)
        if closest[0] > dist:
            closest = (dist, p)
    return closest[1]

def get_positions(nodes, pos, node_to_move, valid, invalid): #recursive function
    x, y = pos
    intersecting = set()
    direction = None
    if not (SIZE*2 < x < WIDTH-SIZE*2 and SIZE*2 < y < WIDTH-SIZE*2):
        a = b = 0
        if SIZE*2 >= x: #Left
            a = -1
        elif x >= WIDTH-SIZE*2: #Right
            a = 1
        if SIZE*2 >= y: #Up
            b = -1
        elif y >= WIDTH-SIZE*2: #Down
            b = 1
        direction = (a, b) #(horizontal, vertical)
    for node in nodes:
        if in_range(pos, node.get_pos(), SIZE*3+0.1): #+0.1 for positions calculated from nodes
            if node != node_to_move:
                intersecting.add(node)
    if not bool(direction):
        while bool(intersecting):
            node1 = intersecting.pop()
            for node2 in intersecting:
                pos1, pos2 = get_intersections(node1, node2)
                valid, invalid = add_pos(nodes, pos1, node_to_move, {node_to_move, node1, node2}, valid, invalid)
                valid, invalid = add_pos(nodes, pos2, node_to_move, {node_to_move, node1, node2}, valid, invalid)
        return valid, invalid
    else:
        positions = set()
        while bool(intersecting):
            node1 = intersecting.pop()
            x1, y1 = node1.get_pos()
            base1 = base2 = 0
            if direction[1] != 0:
                y = WIDTH/2 + direction[1]*(WIDTH/2 - SIZE*2)
                base1 = math.sqrt((SIZE*3)**2 - (y1 - y)**2)
            if direction[0] != 0:
                x = WIDTH/2 + direction[0]*(WIDTH/2 - SIZE*2)
                base2 = math.sqrt((SIZE*3)**2 - (x1 - x)**2)
            if direction[0] != 0 and direction[1] != 0: #Corner
                positions.add((x, y1-direction[1]*base2))
                positions.add((x1-direction[0]*base1, y))
            elif direction[0] != 0: #Horizontal
                positions.add((x, y1-base2))
                positions.add((x, y1+base2))
            elif direction[1] != 0: #Vertical
                positions.add((x1-base1, y))
                positions.add((x1+base1, y))
            while bool(positions):
                temp = positions.pop()
                valid, invalid = add_pos(nodes, temp, node_to_move, {node1, node_to_move}, valid, invalid)
            for node2 in intersecting:
                pos1, pos2 = get_intersections(node1, node2)
                valid, invalid = add_pos(nodes, pos1, node_to_move, {node_to_move, node1, node2}, valid, invalid)
                valid, invalid = add_pos(nodes, pos2, node_to_move, {node_to_move, node1, node2}, valid, invalid)
        return valid, invalid

def add_pos(nodes, pos, node_to_move, exclude, valid, invalid):
    if pos in valid or pos in invalid:
        pass
    else:
        if valid_pos(nodes, pos, exclude):
            valid.add(pos)
        else:
            invalid.add(pos)
            valid, invalid = get_positions(nodes, pos, node_to_move, valid, invalid)
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
    buttons = [
        Button(WIDTH+1, 0, SIDE_BAR, WIDTH//4, 'Add'),
        Button(WIDTH+1, WIDTH//4, SIDE_BAR, WIDTH//4, 'Remove'),
        Button(WIDTH+1, WIDTH//2, SIDE_BAR, WIDTH//4, 'Connect'),
        Button2(WIDTH+1, 3*WIDTH//4, SIDE_BAR, WIDTH//4, 'View', 'Return')
    ]
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
                        button.deselect()
                        if button.get_rect().collidepoint(event.pos):
                            button.click()
                    if toggle_connect:
                        toggle_connect = False
                        node_to_connect.select()
                elif move_node:
                    move_node = False
            if pygame.mouse.get_pressed()[0]:
                if x <= WIDTH:
                    if buttons[0].is_selected(): #Add node
                        if SIZE*2 < x < WIDTH-SIZE*2 and SIZE*2 < y < WIDTH-SIZE*2:
                            valid = True
                            for node in nodes:
                                if in_range(pos, node.get_pos(), SIZE*3):
                                    valid = False
                                    break
                            if valid:
                                nodes.append(Node(pos))
                                buttons[0].deselect()
                    elif buttons[1].is_selected(): #Remove node
                        for node in nodes:
                            if in_range(pos, node.get_pos(), SIZE):
                                node.erase()
                                for edge in node.get_edges():
                                    edge.erase()
                                nodes.remove(node)
                                edges = edges.difference(node.get_edges())
                                for node in nodes:
                                    node.update_edges(edges)
                                buttons[1].deselect()
                                break
                    elif buttons[2].is_selected(): #Connect nodes
                        for node in nodes:
                            if in_range(pos, node.get_pos(), SIZE):
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
                                            toggle_connect = False
                                            buttons[2].deselect()
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
                        pos = closest_valid_pos(nodes, pos, node_to_move)
                        if not bool(pos):
                            pos = prev_pos
                        node_to_move.move(pos)
                        prev_pos = pos
                        for edge in node_to_move.get_edges():
                            edge.move()
                    else:
                        for node in nodes:
                            if in_range(pos, node.get_pos(), SIZE):
                                move_node = True
                                node_to_move = node
                                break
        draw_graph(nodes, edges)
        for button in buttons:
            button.clear()
            if button.get_rect().collidepoint(pos):
                button.hovered()
            button.draw()
        pygame.draw.line(WIN, BLACK, (WIDTH, 0), (WIDTH, WIDTH))
        for i in range(5):
            pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//4), (WIDTH+SIDE_BAR, i*WIDTH//4))
    pygame.quit()

main()
