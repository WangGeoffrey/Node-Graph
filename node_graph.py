from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple
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

    def __init__(self, pos: Tuple):
        self.colorN = GREY
        self.posN = pos
        self.edgesN = set()
        self.connectedN = set()

    @property
    def colorN(self) -> Tuple:
        return self._colorN

    @colorN.setter
    def colorN(self, color: Tuple) -> None:
        self._colorN = color

    @property
    def posN(self) -> Tuple:
        return self._posN

    @posN.setter
    def posN(self, pos: Tuple) -> None:
        self._posN = pos

    @property
    def edgesN(self) -> Set[Edge]:
        return self._edgesN.copy()

    @edgesN.setter
    def edgesN(self, edges: Set[Edge]) -> None:
        self._edgesN = edges

    @property
    def connectedN(self) -> Set[Node]:
        return self._connectedN.copy()

    @connectedN.setter
    def connectedN(self, nodes: Set[Node]) -> None:
        self._connectedN = nodes

    def attach_edge(self, edge: Edge):
        self._edgesN.add(edge)
        self._connectedN.add(edge.connectingE.difference({self}).pop())

    def detach_edge(self, edge: Edge):
        self._edgesN.remove(edge)
        self._connectedN.remove(edge.connectingE.difference({self}).pop())

    def update_edge(self, edges: Set[Edge]):
        edge = set(self.edgesN).intersection(edges)
        if bool(edge):
            self.detach_edge(edge)

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

    def deleteN(self):
        self.eraseN()
        for edge in self._edgesN:
            edge.deleteE()

class DNode(Node):

    def attach_edge(self, edge: Edge):
        self._edgesN.add(edge)
        if edge.connectingE[0] == self:
            self._connectedN.add(edge.connectingE[1])

    def detach_edge(self, edge: Edge):
        self._edgesN.remove(edge)
        if edge.connectingE[0] == self:
            self._connectedN.remove(edge.connectingE[1])

class Edge(ABC):

    @property
    def colorE(self) -> Tuple:
        return self._colorE

    @colorE.setter
    def colorE(self, color) -> None:
        self._colorE = color

    def active(self):
        self.colorE = BLACK

    def inactive(self):
        self.colorE = LIGHTGREY

    @abstractmethod
    def connectingE(self):
        return None

    @abstractmethod
    def connectingE(self, nodes):
        pass

    @property
    def edge(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return self._edge

    @edge.setter
    def edge(self, edge: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        self._edge = edge

    @property
    def weightE(self) -> str:
        return self._weightE

    @weightE.setter
    def weightE(self, input_weight: str) -> None:
        self._weightE = input_weight

    def input_weightE(self, graph: Graph) -> None:
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
            graph.drawG()
            # self.drawE()
            # for node in self.connectingE:
            #     node.drawN() #Missing numbering
            # pygame.display.update()
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

    @abstractmethod
    def moveE(self):
        pass

    @abstractmethod
    def drawE(self):
        pass

    @abstractmethod
    def eraseE(self):
        pass

    @abstractmethod
    def deleteE(self):
        pass

class UEdge(Edge):

    def __init__(self, node1: Node, node2: Node):
        self.colorE = BLACK
        self.connectingE = {node1, node2}
        self.edge = (node1.posN, node2.posN)
        self.weightE = '1'
        self.update_textE()

    @property
    def connectingE(self) -> Set[Node]:
        return set(self._connectingE)

    @connectingE.setter
    def connectingE(self, nodes: Set[Node]) -> None:
        self._connectingE = nodes

    def moveE(self):
        self.eraseE()
        self.edge = tuple(node.posN for node in self.connectingE)
        self.update_textE()

    def drawE(self):
        pygame.draw.line(WIN, self.colorE, self.edge[0], self.edge[1])
        if SHOW_WEIGHTS:
            WIN.blit(self.textE, self.text_rectE)

    def eraseE(self):
        pygame.draw.line(WIN, WHITE, self.edge[0], self.edge[1])
        pygame.draw.rect(WIN, WHITE, self.text_rectE)

    def deleteE(self):
        self.eraseE()
        for node in self.connectingE:
            node.detach_edge(self)

class DEdge(Edge):

    def __init__(self, leaving_node: Node, entering_node: Node):
        self.colorE = BLACK
        self.weightE = '1'
        self.connectingE = (leaving_node, entering_node)
        self.edge = (leaving_node.posN, entering_node.posN)
        self.opposite = None #Edge in opposite direction (if one exists)
        self.update_textE()

    @property
    def connectingE(self) -> Tuple[Node, Node]:
        return self._connectingE

    @connectingE.setter
    def connectingE(self, nodes: Tuple[Node, Node]) -> None:
        self._connectingE = nodes

    @property
    def opposite(self) -> DEdge:
        return self._opposite

    @opposite.setter
    def opposite(self, opposite: DEdge) -> None:
        self._opposite = opposite

    def head_pos(self):
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        x, y = x1-x2, y1-y2
        r = SIZE+2
        if x1 == x2:
            return (x1, y1-r*y/abs(y))
        elif y1 == y2:
            return (x1-r*x/abs(x), y1)
        ratio = abs(y)/abs(x)
        new_x = math.sqrt(r**2/(ratio**2+1))
        new_x, new_y = int(x1 - (x/abs(x))*new_x), int(y1 - (y/abs(y))*(new_x*ratio))
        return (new_x, new_y)

    def edge_pos(self):
        x1, y1 = self.connectingE[0].posN
        x2, y2 = self.connectingE[1].posN
        x, y = x1-x2, y1-y2
        r = int(SIZE/2)
        if x1 == x2:
            return (x1-r*y/abs(y), y1), (x2-r*y/abs(y), y2)
        elif y1 == y2:
            return (x1, y1+r*x/abs(x)), (x2, y2+r*x/abs(x))
        ratio = abs(y)/abs(x)
        new_y = math.sqrt(r**2/(ratio**2+1))
        if (x1 < x2 and y1 < y2) or (x1 > x2 and y1 > y2):
            new_x, new_y = int(-(x/abs(x))*(new_y*ratio)), int((y/abs(y))*new_y)
        else:
            new_x, new_y = int((x/abs(x))*(new_y*ratio)), int(-(y/abs(y))*new_y)
        return (x1 + new_x, y1 + new_y), (x2 + new_x, y2 + new_y)

    def moveE(self):
        self.eraseE()
        if not bool(self.opposite):
            self.edge = tuple(node.posN for node in self.connectingE)
        else:
            self.edge = self.edge_pos()
        self.update_textE()

    def drawE(self):
        pygame.draw.line(WIN, self.colorE, self.edge[0], self.edge[1])
        pygame.draw.circle(WIN, self.colorE, self.head_pos(), 5)
        if SHOW_WEIGHTS:
            WIN.blit(self.textE, self.text_rectE)

    def eraseE(self):
        pygame.draw.line(WIN, WHITE, self.edge[0], self.edge[1])
        pygame.draw.circle(WIN, WHITE, self.head_pos(), 5)
        pygame.draw.rect(WIN, WHITE, self.text_rectE)

    def deleteE(self):
        self.eraseE()
        for node in self.connectingE:
            node.detach_edge(self)
        if bool(self.opposite):
            self.opposite.opposite = None
            self.opposite.moveE()

class Graph(ABC):

    def __init__(self):
        self.matrix = [] #Incidence matrix
        self.nodesG = []
        self.edgesG = []

    @property
    def matrix(self) -> List[List[int]]:
        return self._matrix.copy()

    @matrix.setter
    def matrix(self, matrix: List[List[int]]) -> None:
        self._matrix = matrix

    @property
    def nodesG(self) -> List[Node]:
        return self._nodesG.copy()

    @nodesG.setter
    def nodesG(self, nodes: List[Node]) -> None:
        self._nodesG = nodes

    @property
    def edgesG(self) -> list:
        return self._edgesG.copy()

    @edgesG.setter
    def edgesG(self, edges: List[Edge]) -> None:
        self._edgesG = edges

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
        node.deleteN()

    @abstractmethod
    def add_edge(self, edge: Edge):
        pass

    def remove_edge(self, edge: Edge):
        col_index = self._edgesG.index(edge)
        for row in self._matrix:
            row.pop(col_index)
        self._edgesG.remove(edge)
        edge.deleteE()

    def deselect_edges(self):
        for edge in self.edgesG:
            edge.inactive()

    def reset_edges(self):
        for edge in self.edgesG:
            edge.active()

    def drawG(self):
        for edge in self.edgesG:
            edge.drawE()
        for node in self.nodesG:
            node.drawN()
            text = font.render(str(self.nodesG.index(node)+1) , True , BLACK)
            text_rect = text.get_rect(center=node.posN)
            WIN.blit(text, text_rect)
        pygame.display.update()

class UGraph(Graph):

    def add_edge(self, edge: Edge):
        self._edgesG.append(edge)
        for node in edge.connectingE:
            node.attach_edge(edge)
        for index in range(len(self.nodesG)):
            self._matrix[index].append(int(self._nodesG[index] in edge.connectingE))

    def get_edge(self, node_pair: Set[Node]):
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
            edge.active()

    def min_cover(self):
        exposed = self.max_matching()
        for node in exposed:
            for edge in node.edgesN:
                edge.active()
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
            edge.active()
        return exposed

    def augmenting_path(self, current: Node, matching: Set[Edge], exposed: Set[Node], considered: Set[Edge], path: Set[Edge], label: Dict[Node, bool]):
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
                edge.active()

    def h_cycle(self, start: Node, current: Node, nodes: Set[Node], visited: Set[Node], cycle: Set[Edge]):
        if len(cycle) == len(nodes)-1 and start in current.connectedN and len(cycle) > 1:
            return cycle.union({self.get_edge({current, start})})
        else:
            for node in current.connectedN:
                if not node in visited:
                    temp = self.h_cycle(start, node, nodes, visited.union({node}), cycle.union({self.get_edge({current, node})}))
                    if bool(temp):
                        return temp
        return None

class DGraph(Graph):

    def add_edge(self, edge: Edge):
        for e in self._edgesG:
            if set(e.connectingE) == set(edge.connectingE):
                e.opposite = edge
                edge.opposite = e
                e.moveE()
                edge.moveE()
        self._edgesG.append(edge)
        for node in edge.connectingE:
            node.attach_edge(edge)
        for index in range(len(self.nodesG)):
            value = int(self._nodesG[index] in edge.connectingE)
            if value:
                if edge.connectingE.index(self._nodesG[index]):
                    self._matrix[index].append(-value)
                else:
                    self._matrix[index].append(value)

class Button: #Option button

    def __init__(self, x_pos, y_pos, width, height, text):
        self.colorB = WHITE
        self.border_rectB = pygame.Rect(x_pos, y_pos, width+1, height+1)
        self.rectB = pygame.Rect(x_pos+1, y_pos+1, width-1, height-1)
        self.textB = font.render(text, True, BLACK)
        self.text_rectB = self.textB.get_rect(center=(x_pos + width//2, y_pos + height//2))

    @property
    def colorB(self) -> Tuple:
        return self._colorB

    @colorB.setter
    def colorB(self, color) -> None:
        self._colorB = color

    @property
    def border_rectB(self) -> Rect:
        return self._border_rectB

    @border_rectB.setter
    def border_rectB(self, rect: Rect) -> None:
        self._border_rectB = rect

    @property
    def rectB(self) -> Rect:
        return self._rectB

    @rectB.setter
    def rectB(self, rect: Rect) -> None:
        self._rectB = rect

    @property
    def textB(self) -> Surface:
        return self._textB

    @textB.setter
    def textB(self, text: Surface) -> None:
        self._textB = text

    @property
    def text_rectB(self) -> Rect:
        return self._text_rectB

    @text_rectB.setter
    def text_rectB(self, text_rect: Rect) -> None:
        self._text_rectB = text_rect

    def click(self):
        pass

    def draw(self):
        pygame.draw.rect(WIN, BLACK, self.border_rectB)
        pygame.draw.rect(WIN, self.colorB, self.rectB)
        WIN.blit(self.textB, self.text_rectB)

class ButtonT(Button): #Toggle button

    def __init__(self, x_pos, y_pos, width, height, text, alt_text):
        super(ButtonT, self).__init__(x_pos, y_pos, width, height, text)
        self.alt_textB = font.render(alt_text, True, BLACK)
        self.alt_text_rectB = self.alt_textB.get_rect(center=(x_pos + width//2, y_pos + height//2))
        self.toggle = False

    @property
    def alt_textB(self) -> Surface:
        return self._alt_textB

    @alt_textB.setter
    def alt_textB(self, alt_text: Surface) -> None:
        self._alt_textB = alt_text

    @property
    def alt_text_rectB(self) -> Rect:
        return self._alt_text_rectB

    @alt_text_rectB.setter
    def alt_text_rectB(self, alt_text_rect: Rect) -> None:
        self._alt_text_rectB = alt_text_rect

    @property
    def toggle(self) -> bool:
        return self._toggle

    @toggle.setter
    def toggle(self, value: bool) -> None:
        self._toggle = value

    def click(self):
        self.toggle = not self.toggle
        self.textB, self.alt_textB = (self.alt_textB, self.textB)
        self.text_rectB, self.alt_text_rectB = (self.alt_text_rectB, self.text_rectB)

class Button1(Button):

    def is_selected(self):
        return self.colorB == GREY

    def hover(self):
        if not self.is_selected():
            self.colorB = LIGHTGREY

    def unhover(self):
        if not self.is_selected():
            self.colorB = WHITE

    def select(self):
        self.colorB = GREY

    def deselect(self):
        self.colorB = WHITE

    def click(self):
        if self.is_selected():
            self.deselect()
        else:
            self.select()

class Button2(Button):

    def __init__(self, x_pos, y_pos, width, height, text, function):
        super(Button2, self).__init__(x_pos, y_pos, width, height, text)
        self.execute = function

    def hover(self):
        self.colorB = LIGHTGREY

    def unhover(self):
        self.colorB = WHITE

    def click(self):
        return self.execute()

class Button3(ButtonT):

    def is_selected(self):
        return self.toggle

    def hover(self):
        self.colorB = LIGHTGREY

    def unhover(self):
        self.colorB = WHITE

class Button4(Button3):

    def __init__(self, x_pos, y_pos, width, height, text, alt_text, function):
        super(Button4, self).__init__(x_pos, y_pos, width, height, text, alt_text)
        self.execute = function

    def click(self):
        super(Button4, self).click()
        self.execute()

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

def valid_pos(nodes: List[Node], pos, exclude: Set[Node]):
    if not (SIZE*2 <= pos[0] <= WIDTH-SIZE*2 and SIZE*2 <= pos[1] <= WIDTH-SIZE*2):
        return False
    for node in nodes:
        if in_range(pos, node.posN, SIZE*3):
            if not node in exclude:
                return False
    return True

def closest_valid_pos(nodes: List[Node], pos, node_to_move: Node): #helper function of get_positions()
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

def get_positions(nodes: List[Node], pos, node_to_move: Node, valid: Set[Tuple], invalid: Set[Tuple]): #recursive function
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

def add_pos(nodes: List[Node], pos, node_to_move: Node, exclude: Set[Node], valid: Set[Tuple], invalid: Set[Tuple]):
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
    try:
        h=math.sqrt((SIZE*3)**2-a**2)
    except:
        h=0
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
        Button1(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'Add'),
        Button1(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Remove'),
        Button1(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'Connect'),
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
    graph = UGraph()
    prev_pos = (-1, -1)
    current_node = None
    current_edge = None
    node_to_move = None
    node_to_connect = None
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
                        if button.rectB.collidepoint(event.pos):
                            button.click()
                            if buttons2.index(button) == len(buttons2)-1:
                                graph.reset_edges()
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    if WIDTH < x:
                        for button in buttons:
                            if button.rectB.collidepoint(event.pos):
                                button.click()
                                if button != prev_button:
                                    try:
                                        prev_button.deselect()
                                    except:
                                        pass
                                prev_button = button
                                break
                        if bool(node_to_connect):
                            node_to_connect.deselect()
                            node_to_connect = None
                    elif bool(node_to_move):
                        node_to_move = None
                if not bool(node_to_move):
                    if bool(current_node):
                        if not in_range(pos, current_node.posN, SIZE):
                            current_node.unhover()
                            current_node = None
                    elif bool(current_edge):
                        if not current_edge.text_rectE.collidepoint(pos):
                            current_edge.active()
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
                                    edge.inactive()
                                    current_edge = edge
                                    break
                if pygame.mouse.get_pressed()[0]:
                    if x <= WIDTH:
                        if bool(node_to_move):
                            pos = closest_valid_pos(graph.nodesG, pos, node_to_move)
                            if not bool(pos):
                                pos = prev_pos
                            node_to_move.moveN(pos)
                            prev_pos = pos
                            for edge in node_to_move.edgesN:
                                edge.moveE()
                        elif buttons[0].is_selected(): #Add node
                            if bool(current_node):
                                node_to_move = current_node
                                continue
                            if valid_pos(graph.nodesG, pos, set()):
                                graph.add_node(Node(pos))
                        elif buttons[1].is_selected(): #Remove
                            if bool(current_node):
                                graph.remove_node(current_node)
                                current_node = None
                            elif bool(current_edge):
                                graph.remove_edge(current_edge)
                                current_edge = None
                        elif buttons[2].is_selected(): #Connect nodes
                            if bool(current_node):
                                if bool(node_to_connect):
                                    if current_node != node_to_connect:
                                        if not current_node in node_to_connect.connectedN:
                                            edge = UEdge(current_node, node_to_connect)
                                            graph.add_edge(edge)
                                            node_to_connect.deselect()
                                            node_to_connect = None
                                    else:
                                        node_to_connect.deselect()
                                        node_to_connect = None
                                else:
                                    node_to_connect = current_node
                                    node_to_connect.select()
                        elif bool(current_node):
                            node_to_move = current_node
                        elif buttons[3].is_selected():
                            if bool(current_edge):
                                running = current_edge.input_weightE(graph)
        if buttons[5].is_selected():
            graph.drawG()
            for button in buttons2:
                button.unhover()
                if button.rectB.collidepoint(pos):
                    button.hover()
                button.draw()
        else:
            graph.drawG()
            for button in buttons:
                button.unhover()
                if button.rectB.collidepoint(pos):
                    button.hover()
                button.draw()
    pygame.quit()

main()
