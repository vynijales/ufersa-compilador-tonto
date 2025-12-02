import math

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import (
    QPainterPath,
    QPen,
    QPolygonF,
)
from PyQt5.QtWidgets import (
    QGraphicsPathItem,
)


class EdgeItem(QGraphicsPathItem):
    """Representa uma Aresta (Seta) no Dígrafo."""

    def __init__(self, source_node, dest_node):
        super().__init__()
        self.source = source_node
        self.dest = dest_node

        # Conecta as arestas aos seus respectivos nós para que possam ser atualizadas
        self.source.add_edge(self)
        self.dest.add_edge(self)

        self.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
        self.setZValue(-1)  # Coloca a aresta abaixo dos nós
        self.adjust()

    def adjust(self):
        """Calcula e desenha o caminho da seta."""

        if not self.source or not self.dest:
            return

        # Pontos centrais dos nós
        source_point = self.source.pos()
        dest_point = self.dest.pos()

        line = dest_point - source_point
        length = math.hypot(line.x(), line.y())

        if length == 0:
            return

        # Normaliza o vetor e ajusta o comprimento para começar/terminar na borda do nó
        unit_vec = line / length
        start_point = source_point + unit_vec * (self.source.rect_width / 2)
        end_point = dest_point - unit_vec * (self.dest.rect_width / 2)
        # Calcula pontos de intersecção com as bordas dos retângulos
        start_point = self._calculate_rect_intersection(
            source_point, dest_point, self.source
        )
        end_point = self._calculate_rect_intersection(
            dest_point, source_point, self.dest
        )

        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)

        # Desenha a ponta da seta (indicador de dígrafo)
        arrow_size = 10
        angle = math.atan2(-line.y(), line.x())

        dest_polygon = QPolygonF()
        dest_polygon.append(end_point)
        dest_polygon.append(
            end_point
            + QPointF(
                math.sin(angle - math.pi / 3) * arrow_size,
                math.cos(angle - math.pi / 3) * arrow_size,
            )
        )
        dest_polygon.append(
            end_point
            + QPointF(
                math.sin(angle - math.pi + math.pi / 3) * arrow_size,
                math.cos(angle - math.pi + math.pi / 3) * arrow_size,
            )
        )

        path.addPolygon(dest_polygon)
        self.setPath(path)

    def _calculate_rect_intersection(self, center, target, node):
        """
        Calcula o ponto de intersecção entre a linha center->target e a borda do retângulo do nó.

        Args:
            center: Centro do nó atual
            target: Ponto de destino
            node: NodeItem para calcular a intersecção

        Returns:
            QPointF: Ponto na borda do retângulo
        """
        rect = node.boundingRect()

        # Converte para coordenadas do nó
        local_target = node.mapFromScene(
            node.mapToScene(QPointF(0, 0)) + (target - center)
        )

        # Se o target está no centro, retorna uma borda qualquer
        if abs(local_target.x()) < 0.001 and abs(local_target.y()) < 0.001:
            return center + QPointF(rect.width() / 2, 0)

        # Calcula intersecções com as bordas do retângulo
        half_width = rect.width() / 2
        half_height = rect.height() / 2

        # Normaliza o vetor direção
        dx = local_target.x()
        dy = local_target.y()

        # Calcula qual borda será intersectada primeiro
        if abs(dx) > 0.001:
            t_vertical = half_width / abs(dx)
        else:
            t_vertical = float("inf")

        if abs(dy) > 0.001:
            t_horizontal = half_height / abs(dy)
        else:
            t_horizontal = float("inf")

        # Usa o menor t (intersecção mais próxima)
        if t_vertical <= t_horizontal:
            # Intersecção com borda vertical
            x = half_width if dx > 0 else -half_width
            y = dy * t_vertical
        else:
            # Intersecção com borda horizontal
            x = dx * t_horizontal
            y = half_height if dy > 0 else -half_height

        # Converte de volta para coordenadas da cena
        return center + QPointF(x, y)
