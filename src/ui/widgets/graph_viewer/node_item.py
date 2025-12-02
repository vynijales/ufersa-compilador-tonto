import math

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


class NodeItem(QGraphicsItem):
    """Representa um Nó (Retângulo) no Grafo."""

    def __init__(self, name, node_id, position=QPointF(0, 0)):
        super().__init__()

        self.setPos(position)
        self.node_id = node_id
        self.name = name
        self.edges = []

        # Torna o nó arrastável
        self.setFlag(QGraphicsItem.ItemIsMovable)
        # Permite que o nó envie um sinal de mudança de posição
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

        # Adiciona o rótulo de texto
        self.label = QGraphicsSimpleTextItem(name, self)

        # Calcula as dimensões baseado no texto
        text_rect = self.label.boundingRect()
        self.padding = 8  # Padding interno
        self.rect_width = text_rect.width() + 2 * self.padding
        self.rect_height = text_rect.height() + 2 * self.padding

        # Centraliza o texto no retângulo
        self.label.setPos(-text_rect.width() / 2, -text_rect.height() / 2)

        # Cores padrão
        self.brush = QBrush(QColor(70, 130, 180))  # Azul Aço
        self.pen = QPen(Qt.black, 1.5)

    def boundingRect(self):
        """Define o retângulo delimitador do nó."""
        return QRectF(
            -self.rect_width / 2,
            -self.rect_height / 2,
            self.rect_width,
            self.rect_height,
        )

    def paint(self, painter, option, widget=None):
        """Desenha o nó como um retângulo."""
        rect = self.boundingRect()

        # Desenha o retângulo de fundo
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(rect, 5, 5)  # Cantos arredondados

    def itemChange(self, change, value):
        """Atualiza as arestas quando o nó se move."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Notifica todas as arestas conectadas para que se atualizem
            for edge in self.edges:
                edge.adjust()
        elif change == QGraphicsItem.ItemSelectedChange:
            # Muda a aparência quando selecionado/arrastado
            if value:
                self.brush = QBrush(QColor(100, 150, 220))  # Azul mais claro
                self.pen = QPen(Qt.black, 2.5)  # Borda mais espessa
            else:
                self.brush = QBrush(QColor(70, 130, 180))  # Cor original
                self.pen = QPen(Qt.black, 1.5)  # Borda original
            self.update()  # Força redesenho
        return super().itemChange(change, value)

    def add_edge(self, edge):
        self.edges.append(edge)

    def set_hover_state(self, is_hovering):
        """
        Define o estado de hover do nó.

        Args:
            is_hovering (bool): True se o mouse está sobre o nó
        """
        if is_hovering:
            self.brush = QBrush(QColor(90, 140, 190))  # Cor de hover
            self.pen = QPen(Qt.black, 2)  # Borda ligeiramente mais espessa
        else:
            # Volta à cor normal apenas se não estiver selecionado
            if not self.isSelected():
                self.brush = QBrush(QColor(70, 130, 180))  # Cor original
                self.pen = QPen(Qt.black, 1.5)  # Borda original
        self.update()  # Força redesenho
