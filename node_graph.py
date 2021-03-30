from __future__ import annotations
import pygame
import math

pygame.init()
WIDTH = 600
SIDE_BAR = 100
WIN = pygame.display.set_mode((WIDTH+SIDE_BAR, WIDTH))
pygame.display.set_caption('Node Graph')
font = pygame.font.SysFont('Corbel', 15)

BLACK = (0, 0, 0)
DARKERGREY = (96, 96, 96)
GREY = (128, 128, 128)
LIGHTGREY = (192, 192, 192)
WHITE = (255, 255, 255)

SIZE = 20 #Node radius

SHOW_WEIGHTS = True
CUSTOM_WEIGHTS = False

class Node:

    def __init__(self, pos: tuple):
        self.colorN = GREY
        self.posN = pos
        self._edgesN = set()
        self._connectedN = set()

    @property
    def colorN(self) -> tuple:
        return self._colorN

    @colorN.setter
    def colorN(self, color: tuple) -> None:
        self._colorN = color

    @property
    def posN(self) -> tuple:
        return self._posN

    @posN.setter
    def posN(self, pos: tuple) -> None:
        self._posN = pos

    @property
    def edgesN(self) -> set:
        return self._edgesN.copy()
    
    def add_edge(self, edge: Edge) -> None:
        self._edgesN.add(edge)

    def update_edges(self, edges: set()) -> None:
        self._edgesN = self._edgesN.intersection(edges)

    @property
    def connectedN(self) -> set:
        return self._connectedN.copy()

    def connect_node(self, node: Node) -> None:
        self._connectedN.add(node)

    def disconnect_node(self, node: Node) -> None:
        if node in self._connectedN:
            self._connectedN.remove(node)

    def hover(self):
        if self.colorN != DARKERGREY:
            self.colorN = LIGHTGREY

    def unhover(self):
        if self.colorN != DARKERGREY:
            self.colorN = GREY

    def select(self):
        self.colorN = DARKERGREY

    def deselect(self):
        self.colorN = GREY

    def moveN(self, pos):
        self.eraseN()
        self.posN = pos

    def drawN(self):
        pygame.draw.circle(WIN, self.colorN, self.posN, SIZE)

    def eraseN(self):
        pygame.draw.circle(WIN, WHITE, self.posN, SIZE)

class Edge:

    def __init__(self, node1: Node, node2: Node):
        self.colorE = BLACK
        self.connectingE = {node1, node2}
        self.edge = (node1.posN, node2.posN)
        self.weightE = '1'
        self.update_textE()

    @property
    def colorE(self) -> tuple:
        return self._colorE

    @colorE.setter
    def colorE(self, color) -> None:
        self._colorE = color

    @property
    def connectingE(self) -> set:
        return self._connectingE.copy()

    @connectingE.setter
    def connectingE(self, nodes: set(Node, Node)) -> None:
        self._connectingE = nodes

    @property
    def edge(self) -> tuple(tuple, tuple):
        return self._edge

    @edge.setter
    def edge(self, edge: tuple(tuple, tuple)) -> None:
        self._edge = edge

    @property
    def weightE(self) -> str:
        return self._weightE

    @weightE.setter
    def weightE(self, input) -> None:
        self._weightE = input

    def input_weightE(self) -> None:
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.weightE = self.weightE[:-1]
                        if not bool(self.weightE):
                            self.weightE = '0'
                    else:
                        if event.unicode.isnumeric():
                            if int(self.weightE):
                                self.weightE += event.unicode
                            else:
                                self.weightE = event.unicode
            self.moveE()
            self.drawE()
            for node in self.connectingE:
                node.drawN()
            pygame.display.update()
        return True

    def distance(self) -> int:
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        return int(math.sqrt((x1-x2)**2+(y1-y2)**2))

    def get_weightE(self) -> int:
        if CUSTOM_WEIGHTS:
            return int(self.weightE)
        else:
            return self.distance()

    @property
    def textE(self) -> Surface:
        return self._textE

    @textE.setter
    def textE(self, text: Surface) -> None:
        self._textE = text
    
    @property
    def text_rectE(self) -> Rect:
        return self._text_rectE

    @text_rectE.setter
    def text_rectE(self, text_rect: Rect) -> None:
        self._text_rectE = text_rect

    def update_textE(self):
        if CUSTOM_WEIGHTS:
            self.textE = font.render(self.weightE, True, BLACK)
        else:
            self.textE = font.render(str(self.distance()), True, BLACK)
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        self.text_rectE = self.textE.get_rect(center=(min(x1, x2)+abs(x1-x2)/2, min(y1, y2)+abs(y1-y2)/2))

    def moveE(self):
        self.eraseE()
        self.edge = tuple(node.posN for node in self.connectingE)
        self.update_textE()

    def drawE(self) -> None:
        pygame.draw.line(WIN, self.colorE, self.edge[0], self.edge[1])
        if SHOW_WEIGHTS:
            WIN.blit(self.textE, self.text_rectE)

    def eraseE(self):
        pygame.draw.line(WIN, WHITE, self.edge[0], self.edge[1])
        pygame.draw.rect(WIN, WHITE, self.text_rectE)

class Graph:
    def __init__(self):
        self._matrix = [] #Incidence matrix
        self._nodesG = []
        self._edgesG = []

    @property
    def matrix(self) -> list:
        return self._matrix.copy()

    @property
    def nodesG(self) -> list:
        return self._nodesG.copy()

    @property
    def edgesG(self) -> list:
        return self._edgesG.copy()

    def toggle_show(self):
        global SHOW_WEIGHTS
        SHOW_WEIGHTS = not SHOW_WEIGHTS
        for edge in self.edgesG:
            edge.eraseE()

    def toggle_weight(self):
        global CUSTOM_WEIGHTS
        CUSTOM_WEIGHTS = not CUSTOM_WEIGHTS
        for edge in self.edgesG:
            edge.moveE()

    def add_node(self, node: Node):
        self._nodesG.append(node)
        row = list(0 for element in self.edgesG)
        self._matrix.append(row)

    def remove_node(self, node: Node):
        offset = 0
        row = self._matrix.pop(self._nodesG.index(node))
        for col in range(len(row)):
            if row[col] == 1:
                self.remove_edge(self._edgesG[col-offset])
                offset += 1
        self._nodesG.remove(node)

    def add_edge(self, edge: Edge):
        self._edgesG.append(edge)
        for index in range(len(self.nodesG)):
            self._matrix[index].append(int(self._nodesG[index] in edge.connectingE))

    def remove_edge(self, edge: Edge):
        col_index = self._edgesG.index(edge)
        for row in self._matrix:
            row.pop(col_index)
        self._edgesG.remove(edge)

    def get_edge(self, node_pair: set(Node, Node)):
        for edge in self.edgesG:
            if edge.connectingE == node_pair:
                return edge
        return None

    def is_connected_graph(self) -> bool:
        connecting = connected_graph(self.nodesG[0], {self.nodesG[0]})
        return connecting == set(self.nodesG)

    def MST(self): #Minimum Spanning Tree
        self.deselect_edges()
        if not (bool(self.nodesG) and self.is_connected_graph()):
            return False
        mst = set()
        trees = []
        nodes = set(self.nodesG)
        edges = self.edgesG
        edges.sort(key=lambda x: x.get_weightE())
        while len(mst) < len(self.nodesG)-1:
            min = edges.pop(0)
            linked = min.connectingE
            index = -1
            if linked.issubset(nodes):
                mst.add(min)
                nodes = nodes.difference(linked)
                trees.append(linked)
            else:
                for tree in trees:
                    if linked.issubset(tree):
                        break
                    elif bool(linked.intersection(tree)):
                        if index+1:
                            trees[trees.index(tree)] = tree.union(trees.pop(index))
                            break
                        mst.add(min)
                        index = trees.index(tree)
                        trees[index] = tree.union(linked)
                else:
                    nodes = nodes.difference(linked)
        for edge in mst:
            edge.colorE = BLACK

    def min_cover(self):
        exposed = self.max_matching()
        for node in exposed:
            for edge in node.edgesN:
                edge.colorE = BLACK
                break

    def max_matching(self):
        self.deselect_edges()
        matching = set()
        exposed = set(self.nodesG)
        path = None
        while len(exposed) > 1:
            for node in exposed:
                path = self.augmenting_path(node, matching, exposed, set(), set(), {node: True})
                if bool(path):
                    break
            else:
                break
            alternating_path = path.difference(matching)
            matching = matching.difference(path).union(alternating_path)
            exposed = set(self.nodesG)
            for edge in matching:
                exposed = exposed.difference(edge.connectingE)
        for edge in matching:
            edge.colorE = BLACK
        return exposed

    def augmenting_path(self, current, matching, exposed, considered, path, label):
        for node in current.connectedN:
            edge = self.get_edge({current, node})
            if edge not in considered and node not in label:
                if node in exposed:
                    if label[current]:
                        path.add(edge)
                        return path
                    else:
                        return None
                elif label[current] or edge in matching:
                    label[node] = not label[current]
                    result = self.augmenting_path(node, matching, exposed, considered.union({edge}), path.union({edge}), label)
                    if bool(result):
                        return result
        return None

    def hamiltonian_cycle(self):
        self.deselect_edges()
        if not bool(self.nodesG):
            return False
        start = self.nodesG[0]
        cycle = self.h_cycle(start, start, set(self.nodesG), {start}, set())
        if bool(cycle):
            for edge in cycle:
                edge.colorE = BLACK

    def h_cycle(self, start, current, nodes, visited, cycle):
        if len(cycle) == len(nodes)-1 and start in current.connectedN and len(cycle) > 1:
            return cycle.union({self.get_edge({current, start})})
        else:
            for node in current.connectedN:
                if not node in visited:
                    temp = self.h_cycle(start, node, nodes, visited.union({node}), cycle.union({self.get_edge({current, node})}))
                    if bool(temp):
                        return temp
        return None

    def deselect_edges(self):
        for edge in self.edgesG:
            edge.colorE = LIGHTGREY

    def reset_edges(self):
        for edge in self.edgesG:
            edge.colorE = BLACK

    def drawG(self):
        for edge in self.edgesG:
            edge.drawE()
        for node in self.nodesG:
            node.drawN()
            text = font.render(str(self.nodesG.index(node)+1) , True , BLACK)
            text_rect = text.get_rect(center=node.posN)
            WIN.blit(text, text_rect)
        pygame.display.update()

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
    def __init__(self, x_pos, y_pos, width, height, text, function):
        super(Button2, self).__init__(x_pos, y_pos, width, height, text)
        self.execute = function

    def click(self):
        self.color = GREY
        self.draw()
        self.color = WHITE
        return self.execute()

class Button3(Button):
    def __init__(self, x_pos, y_pos, width, height, text, alt_text):
        super(Button3, self).__init__(x_pos, y_pos, width, height, text)
        self.alt_text = font.render(alt_text, True, BLACK)
        self.alt_text_rect = self.alt_text.get_rect(center=(x_pos + width//2, y_pos + height//2))
        self.toggle = False

    def click(self):
        self.toggle = not self.toggle

    def is_selected(self):
        return self.toggle

    def hovered(self):
        self.color = LIGHTGREY

    def clear(self):
        self.color = WHITE

    def draw(self):
        pygame.draw.rect(WIN, self.color, self.rect)
        if not self.toggle:
            WIN.blit(self.text, self.text_rect)
        else:
            WIN.blit(self.alt_text, self.alt_text_rect)

class Button4(Button3):
    def __init__(self, x_pos, y_pos, width, height, text, alt_text, function):
        super(Button4, self).__init__(x_pos, y_pos, width, height, text, alt_text)
        self.execute = function

    def click(self):
        self.toggle = not self.toggle
        self.color = GREY
        self.draw()
        self.color = WHITE
        return self.execute()

def connected_graph(current, connecting):
    for node in current.connectedN:
        if not node in connecting:
            connecting.add(node)
            connecting = connected_graph(node, connecting)
    return connecting

def has_cycle(matrix, nodes, edges, current_nodes, current_edges):
    if len(nodes) < 3:
        return False
    for node in current_nodes:
        incident = 0
        for edge in current_edges:
            incident += matrix[nodes.index(node)][edges.index(edge)]
        if incident < 2:
            break
    else:
        return True
    for node in current_nodes:
        if self.has_cycle(current_nodes.difference({node}), set(edge for edge in current_edges if node not in edge.connectingE)):
            return True
    return False

def in_range(pos1, pos2, range):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < range

def valid_pos(nodes, pos, exclude):
    if not (SIZE*2 <= pos[0] <= WIDTH-SIZE*2 and SIZE*2 <= pos[1] <= WIDTH-SIZE*2):
        return False
    for node in nodes:
        if in_range(pos, node.posN, SIZE*3):
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
        if in_range(pos, node.posN, SIZE*3):
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
        if pos == node.posN:
            return None
        x1, y1 = node.posN
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
        if in_range(pos, node.posN, SIZE*3+0.1): #+0.1 for positions calculated from nodes
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
            x1, y1 = node1.posN
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
    x0, y0 = node1.posN
    x1, y1 = node2.posN
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
        Button(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'Add'),
        Button(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Remove'),
        Button(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'Connect'),
        Button4(WIDTH+1, 3*WIDTH//6, SIDE_BAR, WIDTH//6, 'Custom weights', 'Default weights', lambda: graph.toggle_weight()),
        Button4(WIDTH+1, 4*WIDTH//6, SIDE_BAR, WIDTH//6, 'Hide', 'Show', lambda: graph.toggle_show()),
        Button3(WIDTH+1, 5*WIDTH//6, SIDE_BAR, WIDTH//6, 'View', 'Return')
    ]
    buttons2 = [
        Button2(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'Hamilton Cycle', lambda: graph.hamiltonian_cycle()),
        Button2(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Max Matching', lambda: graph.max_matching()),
        Button2(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'MST', lambda: graph.MST()),
        buttons[3],
        buttons[4],
        buttons[5]
    ]
    graph = Graph()
    prev_pos = (-1, -1)
    current_node = None
    current_edge = None
    move_node = False
    toggle_connect = False
    prev_button = buttons[0]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            x, y = pos = pygame.mouse.get_pos()
            if buttons[5].is_selected():
                if event.type == pygame.MOUSEBUTTONUP:
                    for button in buttons2:
                        if button.get_rect().collidepoint(event.pos):
                            button.click()
                            if buttons2.index(button) == len(buttons2)-1:
                                graph.reset_edges()
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    if WIDTH < x:
                        for button in buttons:
                            if button.get_rect().collidepoint(event.pos):
                                button.click()
                                if button != prev_button:
                                    prev_button.deselect()
                                prev_button = button
                                break
                        if toggle_connect:
                            toggle_connect = False
                            node_to_connect.select()
                    elif move_node:
                        move_node = False
                if not move_node:
                    if bool(current_node):
                        if not in_range(pos, current_node.posN, SIZE):
                            current_node.unhover()
                            current_node = None
                    elif bool(current_edge):
                        if not current_edge.text_rectE.collidepoint(pos):
                            current_edge.colorE = BLACK
                            current_edge = None
                    if not (bool(current_node) or bool(current_edge)):
                        for node in graph.nodesG:
                            if in_range(pos, node.posN, SIZE):
                                node.hover()
                                current_node = node
                                break
                        else:
                            for edge in graph.edgesG:
                                if edge.text_rectE.collidepoint(pos):
                                    edge.colorE = LIGHTGREY
                                    current_edge = edge
                                    break
                if pygame.mouse.get_pressed()[0]:
                    if x <= WIDTH:
                        if move_node:
                            pos = closest_valid_pos(graph.nodesG, pos, node_to_move)
                            if not bool(pos):
                                pos = prev_pos
                            node_to_move.moveN(pos)
                            prev_pos = pos
                            for edge in node_to_move.edgesN:
                                edge.moveE()
                        elif buttons[0].is_selected(): #Add node
                            if bool(current_node):
                                move_node = True
                                node_to_move = current_node
                                continue
                            if SIZE*2 < x < WIDTH-SIZE*2 and SIZE*2 < y < WIDTH-SIZE*2:
                                valid = True
                                for node in graph.nodesG:
                                    if in_range(pos, node.posN, SIZE*3):
                                        break
                                else:
                                    graph.add_node(Node(pos))
                        elif buttons[1].is_selected(): #Remove
                            if bool(current_node):
                                current_node.eraseN()
                                for edge in current_node.edgesN:
                                    edge.eraseE()
                                graph.remove_node(current_node)
                                for node in graph.nodesG:
                                    node.update_edges(set(graph.edgesG))
                                    node.disconnect_node(current_node)
                                current_node = None
                            elif bool(current_edge):
                                graph.remove_edge(current_edge)
                                for node in current_edge.connectingE:
                                    node.update_edges(set(graph.edgesG))
                                    node.disconnect_node(current_edge.connectingE.difference({node}).pop())
                                current_edge.eraseE()
                                current_edge = None
                        elif buttons[2].is_selected(): #Connect nodes
                            if bool(current_node):
                                if in_range(pos, current_node.posN, SIZE):
                                    if toggle_connect:
                                        if node != node_to_connect:
                                            if not node in node_to_connect.connectedN:
                                                edge = Edge(node, node_to_connect)
                                                node_to_connect.select()
                                                node.connect_node(node_to_connect)
                                                node.add_edge(edge)
                                                node_to_connect.connect_node(node)
                                                node_to_connect.add_edge(edge)
                                                graph.add_edge(edge)
                                                node_to_connect.deselect()
                                                toggle_connect = False
                                        else:
                                            node_to_connect.deselect()
                                            toggle_connect = False
                                    else:
                                        node_to_connect = node
                                        node_to_connect.select()
                                        toggle_connect = True
                                        break
                        elif bool(current_node):
                            move_node = True
                            node_to_move = current_node
                        elif buttons[3].is_selected():
                            if bool(current_edge):
                                running = current_edge.input_weightE()
        if buttons[5].is_selected():
            graph.drawG()
            for button in buttons2:
                button.clear()
                if button.get_rect().collidepoint(pos):
                    button.hovered()
                button.draw()
            pygame.draw.line(WIN, BLACK, (WIDTH, 3*WIDTH//6), (WIDTH, WIDTH))
            for i in range(6):
                pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//6), (WIDTH+SIDE_BAR, i*WIDTH//6))
        else:
            graph.drawG()
            for button in buttons:
                button.clear()
                if button.get_rect().collidepoint(pos):
                    button.hovered()
                button.draw()
            pygame.draw.line(WIN, BLACK, (WIDTH, 0), (WIDTH, WIDTH))
            for i in range(6):
                pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//6), (WIDTH+SIDE_BAR, i*WIDTH//6))
    pygame.quit()

main()
