from __future__ import annotations
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Dict, List, Set, Tuple
import pygame
import math
import sys

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
RED = (255, 0, 0)

SIZE = 20 #Node radius

SHOW_WEIGHTS = True
CUSTOM_WEIGHTS = False
SHOW_VALUE = True

class Node:

    def __init__(self, pos: Tuple):
        self.colorN = GREY
        self.posN = pos
        self.edgesN = set()
        self.connectedN = set()
        self.active = False

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
        if self.active:
            pygame.draw.circle(WIN, RED, self.posN, SIZE)
            pygame.draw.circle(WIN, self.colorN, self.posN, SIZE - 2)
        else:
            pygame.draw.circle(WIN, self.colorN, self.posN, SIZE)

    def eraseN(self):
        pygame.draw.circle(WIN, WHITE, self.posN, SIZE)

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
        self.colorE = RED

    def inactive(self):
        self.colorE = LIGHTGREY

    def default(self):
        self.colorE = BLACK

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
    def default_valueE(self) -> str:
        return self._default_valueE

    @default_valueE.setter
    def default_valueE(self, distance: str) -> None:
        self._default_valueE = distance

    @property
    def weightE(self) -> str:
        return self._weightE

    @weightE.setter
    def weightE(self, input_weight: str) -> None:
        self._weightE = input_weight

    @property
    def costE(self) -> str:
        return self._costE

    @costE.setter
    def costE(self, input_cost: str) -> None:
        self._costE = input_cost

    def input_valueE(self, graph: Graph) -> None:
        run = True
        if SHOW_WEIGHTS:
            value = self.weightE
        else:
            value = self.costE
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        value = value[:-1]
                        if not bool(value):
                            value = '0'
                    else:
                        if event.unicode.isnumeric():
                            if int(value):
                                value += event.unicode
                            else:
                                value = event.unicode
            if SHOW_WEIGHTS:
                self.weightE = value
            else:
                self.costE = value
            self.moveE()
            graph.drawG()
            # self.drawE()
            # for node in self.connectingE:
            #     node.drawN() #Missing numbering
            # pygame.display.update()

    def distance(self) -> int:
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        return int(math.sqrt((x1-x2)**2+(y1-y2)**2))

    def get_weightE(self) -> int:
        if CUSTOM_WEIGHTS:
            return int(self.weightE)
        return int(self.default_valueE)

    def get_costE(self) -> int:
        if CUSTOM_WEIGHTS:
            return int(self.costE)
        return int(self.default_valueE)

    def set_costE(self, cost):
        if CUSTOM_WEIGHTS:
            self.costE = cost
        else:
            self.default_valueE = cost

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
            if SHOW_WEIGHTS:
                self.textE = font.render(self.weightE, True, BLACK)
            else:
                self.textE = font.render(self.costE, True, BLACK)
        else:
            self.default_valueE = str(self.distance())
            self.textE = font.render(self.default_valueE, True, BLACK)
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        self.text_rectE = self.textE.get_rect(center=(x1+self.text_pos*(x2-x1), y1+self.text_pos*(y2-y1)))

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
        self.edge = (node1.posN, node2.posN)
        self.connectingE = {node1, node2}
        self.default_valueE = str(self.distance())
        self.weightE = '1'
        self.costE = '1'
        self.text_pos = 1/2
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
        if SHOW_VALUE:
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
        self.edge = (leaving_node.posN, entering_node.posN)
        self.connectingE = (leaving_node, entering_node)
        self.default_valueE = str(self.distance())
        self.weightE = '1'
        self.costE = '1'
        self.custom_textE = None
        self.text_pos = 1/2
        self.parallel = None #Parallel edge (if one exists)
        self.update_textE()

    @property
    def connectingE(self) -> Tuple[Node, Node]:
        return self._connectingE

    @connectingE.setter
    def connectingE(self, nodes: Tuple[Node, Node]) -> None:
        self._connectingE = nodes

    @property
    def parallel(self) -> DEdge:
        return self._parallel

    @parallel.setter
    def parallel(self, parallel: DEdge) -> None:
        self._parallel = parallel
        if bool(parallel):
            self.text_pos = 4/7
        else:
            self.text_pos = 1/2

    @property
    def custom_textE(self) -> Surface:
        return self._custom_textE

    @custom_textE.setter
    def custom_textE(self, text: Surface):
        self._custom_textE = text

    def set_custom(self, text):
        self.textE = self.custom_textE = font.render(text, True, BLACK)
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        self.text_rectE = self.custom_textE.get_rect(center=(x1+self.text_pos*(x2-x1), y1+self.text_pos*(y2-y1)))

    def head_pos(self):
        x1, y1 = self.edge[0]
        x2, y2 = self.edge[1]
        x, y = x1-x2, y1-y2
        r = SIZE+2
        if x1 == x2:
            return (x2, y2+r*y/abs(y))
        elif y1 == y2:
            return (x2+r*x/abs(x), y2)
        ratio = abs(y)/abs(x)
        new_x = math.sqrt(r**2/(ratio**2+1))
        new_x, new_y = int(x2 + (x/abs(x))*new_x), int(y2 + (y/abs(y))*(new_x*ratio))
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

    def update_textE(self):
        if bool(self.custom_textE):
            self.textE = self.custom_textE
            if CUSTOM_WEIGHTS:
                if not SHOW_WEIGHTS:
                    self.textE = font.render(self.costE, True, BLACK)
            x1, y1 = self.edge[0]
            x2, y2 = self.edge[1]
            self.text_rectE = self.textE.get_rect(center=(x1+self.text_pos*(x2-x1), y1+self.text_pos*(y2-y1)))
        else:
            super(DEdge, self).update_textE()

    def moveE(self):
        self.eraseE()
        if not bool(self.parallel):
            self.edge = tuple(node.posN for node in self.connectingE)
        else:
            self.edge = self.edge_pos()
        self.update_textE()

    def drawE(self):
        pygame.draw.line(WIN, self.colorE, self.edge[0], self.edge[1])
        pygame.draw.circle(WIN, self.colorE, self.head_pos(), 5)
        WIN.blit(self.textE, self.text_rectE)

    def eraseE(self):
        pygame.draw.line(WIN, WHITE, self.edge[0], self.edge[1])
        pygame.draw.circle(WIN, WHITE, self.head_pos(), 5)
        pygame.draw.rect(WIN, WHITE, self.text_rectE)

    def deleteE(self):
        self.eraseE()
        for node in self.connectingE:
            node.detach_edge(self)
        if bool(self.parallel):
            self.parallel.parallel = None
            self.parallel.moveE()

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
    def edgesG(self) -> List[Edge]:
        return self._edgesG.copy()

    @edgesG.setter
    def edgesG(self, edges: List[Edge]) -> None:
        self._edgesG = edges

    def toggle_value(self):
        global SHOW_WEIGHTS
        SHOW_WEIGHTS = not SHOW_WEIGHTS
        for edge in self.edgesG:
            edge.moveE()

    def toggle_weight(self):
        global CUSTOM_WEIGHTS
        CUSTOM_WEIGHTS = not CUSTOM_WEIGHTS
        for edge in self.edgesG:
            edge.moveE()
        self.reset()

    def toggle_show(self):
        global SHOW_VALUE
        SHOW_VALUE = not SHOW_VALUE
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
            if self._edgesG[col-offset] in node.edgesN:
                self.remove_edge(self._edgesG[col-offset])
                offset += 1
        self._nodesG.remove(node)
        node.eraseN()

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

    def reset(self):
        for edge in self.edgesG:
            edge.default()

    def drawG(self):
        for edge in self.edgesG:
            edge.drawE()
        for node in self.nodesG:
            node.drawN()
            text = font.render(str(self.nodesG.index(node)+1), True, BLACK)
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
        if bool(self.nodesG) and self.is_connected_graph():
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

    def hamiltonian_cycle(self):
        self.deselect_edges()
        if bool(self.nodesG):
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

    def min_cover(self):
        exposed = self.max_matching(True)
        for node in exposed:
            for edge in node.edgesN:
                edge.active()
                break

    def max_matching(self, cover):
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
        if cover:
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

class DGraph(Graph):

    def __init__(self):
        super(DGraph, self).__init__()
        self.labeling = {}

    def add_edge(self, edge: Edge):
        for e in self._edgesG:
            if set(e.connectingE) == set(edge.connectingE):
                e.parallel = edge
                edge.parallel = e
                e.moveE()
                edge.moveE()
                break
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
            else:
                self._matrix[index].append(0)

    def get_edge(self, node_pair: Tuple(Node, Node)):
        for edge in self.edgesG:
            if edge.connectingE == node_pair:
                return edge
        return None

    def select(self, label):
        if len(self.nodesG) < len(label):
            return 1
        self.reset()
        current_node = None
        labeled = 0
        while labeled < len(label):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 2
                pos = pygame.mouse.get_pos()
                if bool(current_node):
                    if not in_range(pos, current_node.posN, SIZE):
                        current_node.unhover()
                        current_node = None
                if not bool(current_node):
                    for node in self.nodesG:
                        if in_range(pos, node.posN, SIZE):
                            node.hover()
                            current_node = node
                            break
                if event.type == pygame.MOUSEBUTTONUP:
                    if bool(current_node):
                        if current_node in self.labeling:
                            self.labeling.pop(current_node)
                            labeled = labeled - 1
                        else:
                            self.labeling[current_node] = label[labeled]
                            labeled = labeled + 1
                    if pos[0] > WIDTH:
                        self.labeling.clear()
                        self.reset()
                        return 1
                self.drawG()
        current_node.unhover()
        self.drawG()

    def shortest_path(self, nodes: Tuple(Node, Node)):
        if bool(nodes):
            start, end = nodes
        else:
            label = ['start', 'end']
            exit = self.select(label)
            if exit:
                return exit-1
            start = list(self.labeling.keys())[list(self.labeling.values()).index(label[0])]
            end = list(self.labeling.keys())[list(self.labeling.values()).index(label[1])]
        priority = 0
        edges = PriorityQueue()
        for node in start.connectedN:
            edge = self.get_edge((start, node))
            edges.put((edge.get_costE(), priority, edge))
            priority = priority + 1
        dist = {start: 0}
        labeling = {}
        entering = None
        while not edges.empty() and entering != end:
            cost, dummy, arc = edges.get()
            leaving, entering = arc.connectingE
            if entering in dist:
                continue
            for node in entering.connectedN:
                if node not in dist:
                    edge = self.get_edge((entering, node))
                    edges.put((cost + edge.get_costE(), priority, edge))
                    priority = priority + 1
            dist[entering] = cost
            labeling[entering] = leaving
        path = []
        if end in dist:
            while end != start:
                path.append(self.get_edge((labeling[end], end)))
                end = labeling[end]
        if bool(nodes):
            return path
        for edge in path:
            edge.active()

    def max_flow(self):
        label = ['s', 't']
        exit = self.select(label)
        if exit:
            return exit-1
        source = list(self.labeling.keys())[list(self.labeling.values()).index(label[0])]
        sink = list(self.labeling.keys())[list(self.labeling.values()).index(label[1])]
        while len(source.connectedN) != len(source.edgesN) or bool(sink.connectedN):
            exit = self.select(label)
            if exit:
                return exit-1
            source = list(self.labeling.keys())[list(self.labeling.values()).index(label[0])]
            sink = list(self.labeling.keys())[list(self.labeling.values()).index(label[1])]
        flow = {} #{(leaving node, entering node): (forward flow, backward flow, capacity of arc)}
        for edge in self.edgesG:
            arc = edge.connectingE
            flow[arc] = (0, 0, edge.get_weightE())
            arc = (arc[1], arc[0])
            if not arc in flow:
                flow[arc] = (0, 0, 0)
        path = self.augmenting_path(source, sink, flow, {source}, [], {source})
        while type(path) == list:
            path_flow = float('inf')
            for arc in path:
                spare_capacity = flow[arc][2] + flow[arc][1] - flow[arc][0]
                path_flow = min(path_flow, spare_capacity)
            for arc in path:
                f_flow, b_flow, capacity = flow[arc]
                f_flow, b_flow = max(f_flow + path_flow - b_flow, 0), max(b_flow - path_flow, 0)
                flow[arc] = (f_flow, b_flow, capacity)
                arc = (arc[1], arc[0])
                flow[arc] = (b_flow, f_flow, flow[arc][2])
            path = self.augmenting_path(source, sink, flow, {source}, [], {source})
        for node in path:
            node.active = True
        for arc in flow:
            edge = self.get_edge(arc)
            if bool(edge):
                edge.eraseE()
                edge.set_custom(str(flow[arc][0])+'/'+str(flow[arc][2]))

    def augmenting_path(self, current: Node, sink: Node, flow: Dict, visited: Set, aug_path: List, cut: Set):
        if sink in visited:
            return aug_path
        for edge in current.edgesN:
            arc = edge.connectingE
            if arc[1] in visited:
                if bool(edge.parallel) or arc[0] in visited:
                    continue
                arc = (arc[1], arc[0])
            f_flow, b_flow, capacity = flow[arc]
            if b_flow + capacity - f_flow > 0:
                cut.add(arc[1])
                path = self.augmenting_path(arc[1], sink, flow, visited.union({arc[1]}), aug_path + [arc], cut)
                if type(path) == list:
                    return path
        return cut

    def min_cost_flow(self):
        label = ['s', 't']
        exit = self.select(label)
        if exit:
            return exit-1
        source = list(self.labeling.keys())[list(self.labeling.values()).index(label[0])]
        sink = list(self.labeling.keys())[list(self.labeling.values()).index(label[1])]
        value = '0'
        text = font.render(value, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH-60, WIDTH-20))
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                pos = pygame.mouse.get_pos()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        value = value[:-1]
                        if not bool(value):
                            value = '0'
                    else:
                        if event.unicode.isnumeric():
                            if int(value):
                                value += event.unicode
                            else:
                                value = event.unicode
            pygame.draw.rect(WIN, WHITE, text_rect)
            text = font.render(value, True, BLACK)
            text_rect = text.get_rect(center=(WIDTH-60, WIDTH-20))
            WIN.blit(text, text_rect)
            self.drawG()
        pygame.draw.rect(WIN, WHITE, text_rect)
        self.SSPA(source, sink, int(value))

    def SSPA(self, source, sink, demand): #Successive Shortest Path Algorithm
        original_costs = {}
        flow = {} #{(leaving node, entering node): (forward flow, backward flow, capacity of arc)}
        for edge in self.edgesG:
            original_costs[edge] = str(edge.get_costE())
            arc = edge.connectingE
            flow[arc] = (0, 0, edge.get_weightE())
            arc = (arc[1], arc[0])
            if not arc in flow:
                flow[arc] = (0, 0, 0)
        supplied = 0
        while supplied < demand:
            path = self.shortest_path((source, sink))
            path_flow = float('inf')
            for edge in path:
                arc = edge.connectingE
                spare_capacity = flow[arc][2] + flow[arc][1] - flow[arc][0]
                path_flow = min(path_flow, spare_capacity)
            path_flow = min(demand - supplied, path_flow)
            for edge in path:
                arc = edge.connectingE
                spare_capacity = flow[arc][2] + flow[arc][1] - flow[arc][0]
                if spare_capacity == path_flow:
                    edge.set_costE(str(sys.maxsize))
            for edge in path:
                arc = edge.connectingE
                f_flow, b_flow, capacity = flow[arc]
                f_flow, b_flow = max(f_flow + path_flow - b_flow, 0), max(b_flow - path_flow, 0)
                flow[arc] = (f_flow, b_flow, capacity)
                arc = (arc[1], arc[0])
                flow[arc] = (b_flow, f_flow, flow[arc][2])
            supplied = supplied + path_flow
            if not path_flow:
                break
        for edge in self.edgesG:
            edge.set_costE(original_costs[edge])
        for arc in flow:
            edge = self.get_edge(arc)
            if bool(edge):
                edge.eraseE()
                edge.set_custom(str(flow[arc][0])+'/'+str(flow[arc][2]))

    def reset_labels(self):
        self.labeling.clear()
        self.drawG()

    def reset(self):
        super(DGraph, self).reset()
        self.reset_labels()
        for node in self.nodesG:
            node.active = False
        for edge in self.edgesG:
            edge.custom_textE = None
            edge.moveE()

    def drawG(self):
        for edge in self.edgesG:
            edge.drawE()
        for node in self.nodesG:
            node.drawN()
            if node in self.labeling:
                text = font.render(self.labeling[node], True, BLACK)
            else:
                text = font.render(str(self.nodesG.index(node)+1) , True , BLACK)
            text_rect = text.get_rect(center=node.posN)
            WIN.blit(text, text_rect)
        pygame.display.update()

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

    def hover(self):
        pass

    def unhover(self):
        pass

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

    def is_selected(self):
        return self.colorB == GREY

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
    buttons11 = [
        Button1(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'Add'),
        Button1(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Remove'),
        Button1(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'Connect'),
        Button4(WIDTH+1, 3*WIDTH//6, SIDE_BAR, WIDTH//6, 'Hide', 'Show', lambda: graph.toggle_show()),
        Button4(WIDTH+1, 4*WIDTH//6, SIDE_BAR, WIDTH//6, 'Custom', 'Default', lambda: graph.toggle_weight()),
        Button3(WIDTH+1, 5*WIDTH//6, SIDE_BAR, WIDTH//6, 'View', 'Return')
    ]
    buttons12 = [
        buttons11[0],
        buttons11[1],
        buttons11[2],
        Button4(WIDTH+1, 3*WIDTH//6, SIDE_BAR, WIDTH//6, 'Show costs', 'Show weights', lambda: graph.toggle_value()),
        buttons11[4],
        buttons11[5]
    ]
    buttons21 = [
        Button2(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'MST', lambda: graph.MST()),
        Button2(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Hamilton Cycle', lambda: graph.hamiltonian_cycle()),
        Button2(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'Max Matching', lambda: graph.max_matching(False)),
        Button2(WIDTH+1, 3*WIDTH//6, SIDE_BAR, WIDTH//6, 'Min Cover', lambda: graph.min_cover()),
        buttons11[4],
        buttons11[5]
    ]
    buttons22 = [
        Button2(WIDTH+1, 0, SIDE_BAR, WIDTH//6, 'Shortest Path', lambda: graph.shortest_path(False)),
        Button2(WIDTH+1, WIDTH//6, SIDE_BAR, WIDTH//6, 'Max Flow', lambda: graph.max_flow()),
        Button2(WIDTH+1, 2*WIDTH//6, SIDE_BAR, WIDTH//6, 'MCF', lambda: graph.min_cost_flow()),
        buttons12[3],
        buttons11[4],
        buttons11[5]
    ]
    buttons = buttons11
    alt_buttons = buttons21
    graph = UGraph()
    directed = False
    text = font.render('Undirected Graph', True, BLACK)
    text_rect = text.get_rect(center=(WIDTH-60, 10))
    WIN.blit(text, text_rect)
    prev_pos = (-1, -1)
    current_node = None
    current_edge = None
    node_to_move = None
    node_to_connect = None
    prev_button = buttons11[0]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            x, y = pos = pygame.mouse.get_pos()
            if buttons11[5].is_selected():
                if event.type == pygame.MOUSEBUTTONUP:
                    for button in buttons:
                        if button.rectB.collidepoint(event.pos):
                            running = not button.click()
                            if buttons.index(button) == len(buttons)-1:
                                graph.reset()
                                if type(graph) == UGraph:
                                    buttons = buttons11
                                else:
                                    buttons = buttons12
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    if WIDTH < x:
                        for button in buttons:
                            if button.rectB.collidepoint(event.pos):
                                button.click()
                                if buttons.index(button) == len(buttons)-1:
                                    buttons = alt_buttons
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
                if pygame.mouse.get_pressed()[2]:
                    del graph
                    pygame.draw.rect(WIN, WHITE, pygame.Rect(0, 0, WIDTH, WIDTH))
                    if directed:
                        graph = UGraph()
                        buttons = buttons11
                        alt_buttons = buttons21
                        text = font.render('Undirected Graph', True, BLACK)
                    else:
                        graph = DGraph()
                        buttons = buttons12
                        alt_buttons = buttons22
                        text = font.render('Directed Graph', True, BLACK)
                    WIN.blit(text, text_rect)
                    directed = not directed
                    SHOW_WEIGHTS = True
                    SHOW_VALUE = True
                if not bool(node_to_move):
                    if bool(current_node):
                        if not in_range(pos, current_node.posN, SIZE):
                            current_node.unhover()
                            current_node = None
                    elif bool(current_edge):
                        if not current_edge.text_rectE.collidepoint(pos):
                            current_edge.default()
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
                                if directed:
                                    graph.add_node(DNode(pos))
                                else:
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
                                            if directed:
                                                edge = DEdge(node_to_connect, current_node)
                                            else:
                                                edge = UEdge(node_to_connect, current_node)
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
                        elif buttons[4].is_selected():
                            if bool(current_edge):
                                running = not current_edge.input_valueE(graph)
        graph.drawG()
        for button in buttons:
            button.unhover()
            if button.rectB.collidepoint(pos):
                button.hover()
            button.draw()
    pygame.quit()

main()
