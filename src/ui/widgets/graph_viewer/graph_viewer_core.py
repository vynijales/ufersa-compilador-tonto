from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import (
    QCursor,
)
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from ui.widgets.graph_viewer.node_item import NodeItem


class GraphViewerCore(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(QGraphicsScene(parent), parent)
        self.scene().setSceneRect(0, 0, 780, 580)
        # scene.setBackgroundBrush(QColor(60, 64, 80))

        # Configuração inicial de navegação
        self.setDragMode(self.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorUnderMouse)

        # Estados para controle de grab
        self._grab_mode = True
        self._is_grabbing = False
        self._last_grab_pos = QPointF()

        # Timer para navegação com teclado
        self._keyboard_timer = QTimer()
        self._keyboard_timer.timeout.connect(self._handle_keyboard_navigation)
        self._pressed_keys = set()
        self._keyboard_speed = 10  # Pixels por tick do timer

        # Configuração de foco para receber eventos de teclado
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Habilita tracking de mouse para atualizar cursor em tempo real
        self.setMouseTracking(True)

    def set_grab_mode(self, enabled):
        """
        Ativa ou desativa o modo grab para navegação com mouse.

        Args:
            enabled (bool): True para ativar grab, False para desativar
        """
        self._grab_mode = enabled

        if enabled:
            self.setDragMode(self.DragMode.ScrollHandDrag)
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self.setDragMode(self.DragMode.NoDrag)  # Desativa drag padrão do Qt
            # Cursor será definido dinamicamente em _update_cursor_for_item_under_mouse
        else:
            self.setDragMode(self.DragMode.NoDrag)
            self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_grab_mode(self):
        self.set_grab_mode(not self._grab_mode)
        return self._grab_mode

    def is_grab_mode_active(self):
        return self._grab_mode

    def pan_to_point(self, x, y):
        """Move a visualização para centralizar no ponto especificado."""
        self.centerOn(QPointF(x, y))

    def pan_by_offset(self, dx, dy):
        """Move a visualização por um offset específico."""
        # Obtém a posição atual do centro da visualização
        current_center = self.mapToScene(self.viewport().rect().center())

        # Move para a nova posição
        new_center = QPointF(current_center.x() + dx, current_center.y() + dy)
        self.centerOn(new_center)

    def reset_view(self):
        self.resetTransform()
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def zoom_to_fit(self):
        if self.scene().items():
            self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def set_keyboard_navigation_speed(self, speed):
        self._keyboard_speed = max(1, speed)

    def wheelEvent(self, event):
        """Evento de scroll do mouse para zoom."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        self.scale(factor, factor)

    def _is_node_item(self, item):
        """
        Verifica se o item é um nó ou parte de um nó (incluindo texto).

        Args:
            item: Item gráfico a ser verificado

        Returns:
            bool: True se for um nó ou parte de um nó
        """
        if isinstance(item, NodeItem):
            return True

        # Verifica se é um texto que pertence a um nó
        if isinstance(item, QGraphicsSimpleTextItem):
            return isinstance(item.parentItem(), NodeItem)

        return False

    def _handle_node_hover(self, pos):
        """
        Gerencia o estado de hover dos nós.

        Args:
            pos: Posição do mouse na view
        """
        # Encontra todos os itens sob o cursor
        item_under_cursor = self.itemAt(pos)

        # Reset hover state para todos os nós visíveis
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                item.set_hover_state(False)

        # Aplica hover state apenas no nó sob o cursor
        if self._is_node_item(item_under_cursor):
            if isinstance(item_under_cursor, NodeItem):
                item_under_cursor.set_hover_state(True)
            elif isinstance(item_under_cursor, QGraphicsSimpleTextItem):
                parent = item_under_cursor.parentItem()
                if isinstance(parent, NodeItem):
                    parent.set_hover_state(True)

    def _update_cursor_for_item_under_mouse(self, pos):
        """
        Atualiza o cursor baseado no item sob o mouse.

        Args:
            pos: Posição do mouse na view
        """
        if not self._grab_mode:
            self.setCursor(QCursor(Qt.ArrowCursor))
            return

        item_under_cursor = self.itemAt(pos)

        # Se há um nó sob o cursor, usa cursor padrão (permite arrastar o nó)
        if self._is_node_item(item_under_cursor):
            self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            # Se não há nó sob o cursor, usa cursor de grab (permite arrastar a cena)
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mousePressEvent(self, event):
        """Evento de pressionar botão do mouse."""
        if event.button() == Qt.LeftButton and self._grab_mode:
            self._is_grabbing = True
            self._last_grab_pos = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            # Verifica se há um item (nó) sob o cursor
            item_under_cursor = self.itemAt(event.pos())

            # Se não há item sob o cursor ou o item não é um nó, permite grab da cena
            if not self._is_node_item(item_under_cursor):
                self._is_grabbing = True
                self._last_grab_pos = event.pos()
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                # Se há um nó sob o cursor, não ativa grab da cena
                self._is_grabbing = False

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Evento de movimento do mouse."""
        if self._is_grabbing and (event.buttons() & Qt.LeftButton):
            # Calcula o offset do movimento
            delta = event.pos() - self._last_grab_pos
            self._last_grab_pos = event.pos()

            # Move a visualização na direção oposta ao movimento do mouse
            h_value = self.horizontalScrollBar().value() - delta.x()
            v_value = self.verticalScrollBar().value() - delta.y()

            self.horizontalScrollBar().setValue(h_value)
            self.verticalScrollBar().setValue(v_value)

        # Sempre atualiza cursor e hover state durante movimento do mouse
        self._update_cursor_for_item_under_mouse(event.pos())
        self._handle_node_hover(event.pos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Evento de soltar botão do mouse."""
        if event.button() == Qt.LeftButton and self._is_grabbing:
            self._is_grabbing = False
            if self._grab_mode:
                self.setCursor(QCursor(Qt.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
            # Atualiza cursor baseado na posição atual do mouse
            self._update_cursor_for_item_under_mouse(event.pos())

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Evento de pressionar tecla."""
        key = event.key()

        navigation_keys = {
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_W,
            Qt.Key_S,
            Qt.Key_A,
            Qt.Key_D,
        }

        if key in navigation_keys:
            self._pressed_keys.add(key)
            if not self._keyboard_timer.isActive():
                self._keyboard_timer.start(16)  # ~60 FPS

        # Atalhos especiais
        elif key == Qt.Key_Space:
            self.toggle_grab_mode()
        elif key == Qt.Key_Home or key == Qt.Key_R:
            self.reset_view()
        elif key == Qt.Key_F or (
            event.modifiers() & Qt.ControlModifier and key == Qt.Key_F
        ):
            self.zoom_to_fit()

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Evento de soltar tecla."""
        key = event.key()

        if key in self._pressed_keys:
            self._pressed_keys.remove(key)

        # Para o timer se não há mais teclas pressionadas
        if not self._pressed_keys and self._keyboard_timer.isActive():
            self._keyboard_timer.stop()

        super().keyReleaseEvent(event)

    def _handle_keyboard_navigation(self):
        """Manipula a navegação contínua por teclado."""
        if not self._pressed_keys:
            return

        dx = dy = 0

        # Movimentos horizontais
        if Qt.Key_Left in self._pressed_keys or Qt.Key_A in self._pressed_keys:
            dx -= self._keyboard_speed
        if Qt.Key_Right in self._pressed_keys or Qt.Key_D in self._pressed_keys:
            dx += self._keyboard_speed

        # Movimentos verticais
        if Qt.Key_Up in self._pressed_keys or Qt.Key_W in self._pressed_keys:
            dy -= self._keyboard_speed
        if Qt.Key_Down in self._pressed_keys or Qt.Key_S in self._pressed_keys:
            dy += self._keyboard_speed

        # Aplica o movimento
        if dx != 0 or dy != 0:
            self.pan_by_offset(dx, dy)

    def focusInEvent(self, event):
        """Evento de ganhar foco."""
        super().focusInEvent(event)
        # Garante que o widget pode receber eventos de teclado

    def focusOutEvent(self, event):
        """Evento de perder foco."""
        # Para a navegação por teclado quando perde o foco
        self._pressed_keys.clear()
        if self._keyboard_timer.isActive():
            self._keyboard_timer.stop()
        super().focusOutEvent(event)
