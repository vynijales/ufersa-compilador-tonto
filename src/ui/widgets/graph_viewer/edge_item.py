import math

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsPathItem


class EdgeItem(QGraphicsPathItem):
    """Representa uma Aresta (Seta) no Dígrafo."""

    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source = source_node
        self.dest = dest_node

        # Conecta as arestas aos seus respectivos nós para que possam ser atualizadas
        self.source.add_edge(self)
        self.dest.add_edge(self)

        self.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
        self.setZValue(-1)  # Coloca a aresta abaixo dos nós
        self.adjust()

    def adjust(self):
        """Calcula e desenha o caminho da seta."""
        if not self.source or not self.dest:
            return

        # Pontos centrais dos nós
        source_center = self.source.pos()
        dest_center = self.dest.pos()

        # Calcula o vetor direção
        direction = dest_center - source_center
        length = math.hypot(direction.x(), direction.y())

        if length == 0:
            return

        # Calcula pontos de intersecção com as bordas dos retângulos
        start_point = self._calculate_rect_intersection(
            source_center, dest_center, self.source
        )
        end_point = self._calculate_rect_intersection(
            dest_center, source_center, self.dest
        )

        # Cria o path da linha
        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)

        # Calcula e adiciona a ponta da seta
        arrow_head = self._create_arrow_head(start_point, end_point)
        path.addPolygon(arrow_head)

        self.setPath(path)

    def _calculate_rect_intersection(self, center, target, node):
        """
        Calcula o ponto de intersecção entre a linha center->target e a borda do retângulo do nó.
        """
        # Direção do centro para o target
        direction = target - center

        if abs(direction.x()) < 0.001 and abs(direction.y()) < 0.001:
            return center

        # Dimensões do retângulo (metade da largura e altura)
        half_width = node.rect_width / 2
        half_height = node.rect_height / 2

        # Normaliza a direção
        abs_dx = abs(direction.x())
        abs_dy = abs(direction.y())

        # Calcula os parâmetros t para intersecções com bordas verticais e horizontais
        if abs_dx > 0.001:
            t_vertical = half_width / abs_dx
        else:
            t_vertical = float("inf")

        if abs_dy > 0.001:
            t_horizontal = half_height / abs_dy
        else:
            t_horizontal = float("inf")

        # Usa o menor t (primeira intersecção)
        if t_vertical <= t_horizontal:
            # Intersecção com borda vertical (esquerda ou direita)
            intersection_x = half_width if direction.x() > 0 else -half_width
            intersection_y = direction.y() * t_vertical
        else:
            # Intersecção com borda horizontal (topo ou fundo)
            intersection_x = direction.x() * t_horizontal
            intersection_y = half_height if direction.y() > 0 else -half_height

        return center + QPointF(intersection_x, intersection_y)

    def _create_arrow_head(self, start_point, end_point):
        """
        Cria a ponta da seta no ponto final.
        """
        # Tamanho da seta
        arrow_size = 24
        arrow_angle = math.pi / 6  # 30 graus

        # Calcula o ângulo da linha
        direction = end_point - start_point
        line_angle = math.atan2(direction.y(), direction.x())

        # Pontos da seta
        arrow_head = QPolygonF()

        # Ponta da seta (no end_point)
        arrow_head.append(end_point)

        # Lado esquerdo da seta
        left_angle = line_angle + math.pi - arrow_angle
        left_point = end_point + QPointF(
            arrow_size * math.cos(left_angle), arrow_size * math.sin(left_angle)
        )
        arrow_head.append(left_point)

        # Ponta da seta (no end_point)
        arrow_head.append(end_point)
        # Lado direito da seta
        right_angle = line_angle + math.pi + arrow_angle
        right_point = end_point + QPointF(
            arrow_size * math.cos(right_angle), arrow_size * math.sin(right_angle)
        )
        arrow_head.append(right_point)

        return arrow_head
