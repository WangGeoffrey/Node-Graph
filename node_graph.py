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

    def get_connected(self):
        result = set()
        for edge in self.edges:
            node1, node2 = edge.get_connecting()
            if node1 != self:
                result.add(node1)
            else:
                result.add(node2)
        return result

    def get_pos(self):
        return self.pos

    def select(self):
        if self.color == GREY:
            self.color = LIGHTGREY
        else:
            self.color = GREY

    def get_edges(self):
        return self.edges

    def set_color(self, color):
        self.color = color

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
        self.distance(node1, node2)
        self.connecting = {node1, node2}
        self.edge = tuple(node.get_pos() for node in self.connecting)

    def distance(self, node1, node2):
        x1, y1 = node1.get_pos()
        x2, y2 = node2.get_pos()
        self.weight = int(math.sqrt((x1-x2)**2+(y1-y2)**2))
        self.text = font.render(str(self.weight), True, BLACK)
        self.text_rect = self.text.get_rect(center=(min(x1, x2)+abs(x1-x2)/2, min(y1, y2)+abs(y1-y2)/2))

    def get_text_rect(self):
        return self.text_rect

    def set_color(self, color):
        self.color = color

    def get_weight(self):
        return self.weight

    def get_connecting(self):
        return self.connecting

    def is_equal(self, edge):
        return self.connecting == edge.get_connecting()

    def move(self):
        self.erase()
        node1, node2 = self.connecting
        self.distance(node1, node2)
        self.edge = tuple(node.get_pos() for node in self.connecting)
    
    def draw(self, show):
        pygame.draw.line(WIN, self.color, self.edge[0], self.edge[1])
        if show:
            WIN.blit(self.text, self.text_rect)

    def erase(self):
        pygame.draw.line(WIN, WHITE, self.edge[0], self.edge[1])
        pygame.draw.rect(WIN, WHITE, self.text_rect)

class Graph:
    def __init__(self):
        self.matrix = [] #Incidence matrix
        self.nodes = []
        self.edges = []
        self.show_weights = True

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_edge(self, node_pair):
        for edge in self.edges:
            if edge.get_connecting() == node_pair:
                return edge
        return None

    def add_node(self, node):
        self.nodes.append(node)
        row = list(0 for element in self.edges)
        self.matrix.append(row)

    def remove_node(self, node):
        offset = 0
        row = self.matrix.pop(self.nodes.index(node))
        for col in range(len(row)):
            if row[col] == 1:
                self.remove_edge(self.edges[col-offset])
                offset += 1
        self.nodes.remove(node)

    def add_edge(self, edge):
        self.edges.append(edge)
        for index in range(len(self.nodes)):
            self.matrix[index].append(int(self.nodes[index] in edge.get_connecting()))

    def remove_edge(self, edge):
        col_index = self.edges.index(edge)
        for row in self.matrix:
            row.pop(col_index)
        self.edges.remove(edge)

    def toggle_show(self):
        if self.show_weights:
            self.show_weights = False
            for edge in self.edges:
                edge.erase()
            self.draw()
        else:
            self.show_weights = True

    def is_connectd_graph(self):
        connecting = connected(self.nodes[0], {self.nodes[0]})
        return connecting == set(self.nodes)

    def has_cycle(self, nodes, edges):
        if len(nodes) < 3:
            return False
        for node in nodes:
            incident = 0
            for edge in edges:
                incident += self.matrix[self.nodes.index(node)][self.edges.index(edge)]
            if incident < 2:
                break
        else:
            return True
        for node in nodes:
            if self.has_cycle(nodes.difference({node}), set(edge for edge in edges if node not in edge.get_connecting())):
                return True
        return False

    def MST(self): #Minimum Spanning Tree
        self.deselect_edges()
        if not (bool(self.nodes) and self.is_connectd_graph()):
            return False
        mst = set()
        trees = []
        edges = self.edges.copy()
        edges.sort(key=lambda x: x.get_weight())
        while len(mst) < len(self.nodes)-1:
            min = edges.pop(0)
            linked = min.get_connecting()
            index = 0
            while index < len(trees):
                tree = trees[index]
                if linked.issubset(tree):
                    break
                elif bool(linked.intersection(tree)):
                    linked = linked.union(tree)
                    trees.pop(index)
                else:
                    index += 1
            else:
                trees.append(linked)
                mst.add(min)
        for edge in mst:
            edge.set_color(BLACK)

    def min_cover(self):
        exposed = self.max_matching()
        for node in exposed:
            for edge in node.get_edges():
                edge.set_color(BLACK)
                break

    def max_matching(self):
        self.deselect_edges()
        matching = set()
        exposed = set(self.nodes)
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
            exposed = set(self.nodes)
            for edge in matching:
                exposed = exposed.difference(edge.get_connecting())
        for edge in matching:
            edge.set_color(BLACK)
        return exposed

    def augmenting_path(self, current, matching, exposed, considered, path, label):
        for node in current.get_connected():
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
        if not bool(self.nodes):
            return False
        start = self.nodes[0]
        cycle = self.h_cycle(start, start, set(self.nodes), {start}, set())
        if bool(cycle):
            for edge in cycle:
                edge.set_color(BLACK)

    def h_cycle(self, start, current, nodes, visited, cycle):
        if len(cycle) == len(nodes)-1 and start in current.get_connected() and len(cycle) > 1:
            return cycle.union({self.get_edge({current, start})})
        else:
            for node in current.get_connected():
                if not node in visited:
                    temp = self.h_cycle(start, node, nodes, visited.union({node}), cycle.union({self.get_edge({current, node})}))
                    if bool(temp):
                        return temp
        return None

    def deselect_edges(self):
        for edge in self.edges:
            edge.set_color(LIGHTGREY)

    def reset_edges(self):
        for edge in self.edges:
            edge.set_color(BLACK)

    def draw(self):
        for edge in self.edges:
            edge.draw(self.show_weights)
        for node in self.nodes:
            node.draw()
            text = font.render(str(self.nodes.index(node)+1) , True , BLACK)
            text_rect = text.get_rect(center=node.get_pos())
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

def connected(current, connecting):
    for node in current.get_connected():
        if not node in connecting:
            connecting.add(node)
            connecting = connected(node, connecting)
    return connecting

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
        Button(WIDTH+1, 0, SIDE_BAR, WIDTH//5, 'Add'),
        Button(WIDTH+1, WIDTH//5, SIDE_BAR, WIDTH//5, 'Remove'),
        Button(WIDTH+1, 2*WIDTH//5, SIDE_BAR, WIDTH//5, 'Connect'),
        Button4(WIDTH+1, 3*WIDTH//5, SIDE_BAR, WIDTH//5, 'Hide', 'Show', lambda: graph.toggle_show()),
        Button3(WIDTH+1, 4*WIDTH//5, SIDE_BAR, WIDTH//5, 'View', 'Return')
    ]
    buttons2 = [
        Button2(WIDTH+1, 0, SIDE_BAR, WIDTH//5, 'Hamilton Cycle', lambda: graph.hamiltonian_cycle()),
        Button2(WIDTH+1, WIDTH//5, SIDE_BAR, WIDTH//5, 'Max Matching', lambda: graph.max_matching()),
        Button2(WIDTH+1, 2*WIDTH//5, SIDE_BAR, WIDTH//5, 'MST', lambda: graph.MST()),
        buttons[3],
        buttons[4]
    ]
    graph = Graph()
    prev_pos = (-1, -1)
    move_node = False
    toggle_connect = False
    prev_button = buttons[0]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            x, y = pos = pygame.mouse.get_pos()
            if buttons[4].is_selected():
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
                if (prev_button == buttons[len(buttons)-1] or prev_button == buttons[len(buttons)-2]) or not prev_button.is_selected():
                    for node in graph.get_nodes():
                        if in_range(pos, node.get_pos(), SIZE):
                            node.set_color(LIGHTGREY)
                        else:
                            node.set_color(GREY)
                    else:
                        for edge in graph.get_edges():
                            if edge.get_text_rect().collidepoint(pos):
                                edge.set_color(LIGHTGREY)
                            else:
                                edge.set_color(BLACK)
                if pygame.mouse.get_pressed()[0]:
                    if x <= WIDTH:
                        if buttons[0].is_selected(): #Add node
                            if SIZE*2 < x < WIDTH-SIZE*2 and SIZE*2 < y < WIDTH-SIZE*2:
                                valid = True
                                for node in graph.get_nodes():
                                    if in_range(pos, node.get_pos(), SIZE*3):
                                        valid = False
                                        break
                                if valid:
                                    graph.add_node(Node(pos))
                        elif buttons[1].is_selected(): #Remove
                            for node in graph.get_nodes():
                                if in_range(pos, node.get_pos(), SIZE):
                                    node.erase()
                                    for edge in node.get_edges():
                                        edge.erase()
                                    graph.remove_node(node)
                                    for node in graph.get_nodes():
                                        node.update_edges(set(graph.get_edges()))
                                    break
                            else:
                                for edge in graph.get_edges():
                                    if edge.get_text_rect().collidepoint(pos):
                                        graph.remove_edge(edge)
                                        for node in edge.get_connecting():
                                            node.update_edges(set(graph.get_edges()))
                                        edge.erase()
                                        break
                        elif buttons[2].is_selected(): #Connect nodes
                            for node in graph.get_nodes():
                                if in_range(pos, node.get_pos(), SIZE):
                                    if toggle_connect:
                                        if node != node_to_connect:
                                            edge = Edge(node, node_to_connect)
                                            valid = True
                                            for existing_edge in node.get_edges():
                                                if existing_edge.is_equal(edge):
                                                    valid = False
                                                    break
                                            if valid:
                                                node_to_connect.select()
                                                node.connect(edge)
                                                node_to_connect.connect(edge)
                                                graph.add_edge(edge)
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
                            pos = closest_valid_pos(graph.get_nodes(), pos, node_to_move)
                            if not bool(pos):
                                pos = prev_pos
                            node_to_move.move(pos)
                            prev_pos = pos
                            for edge in node_to_move.get_edges():
                                edge.move()
                        else:
                            for node in graph.get_nodes():
                                if in_range(pos, node.get_pos(), SIZE):
                                    move_node = True
                                    node_to_move = node
                                    break
        if buttons[4].is_selected():
            graph.draw()
            for button in buttons2:
                button.clear()
                if button.get_rect().collidepoint(pos):
                    button.hovered()
                button.draw()
            pygame.draw.line(WIN, BLACK, (WIDTH, 3*WIDTH//5), (WIDTH, WIDTH))
            for i in range(6):
                pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//5), (WIDTH+SIDE_BAR, i*WIDTH//5))
        else:
            graph.draw()
            for button in buttons:
                button.clear()
                if button.get_rect().collidepoint(pos):
                    button.hovered()
                button.draw()
            pygame.draw.line(WIN, BLACK, (WIDTH, 0), (WIDTH, WIDTH))
            for i in range(6):
                pygame.draw.line(WIN, BLACK, (WIDTH, i*WIDTH//5), (WIDTH+SIDE_BAR, i*WIDTH//5))
    pygame.quit()

main()
