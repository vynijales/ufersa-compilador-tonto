from PyQt5.QtCore import QPointF, Qt

from parser.parser import parse_ontology
from ui.widgets.graph_viewer.edge_item import EdgeItem
from ui.widgets.graph_viewer.graph_viewer_core import GraphViewerCore
from ui.widgets.graph_viewer.node_item import NodeItem
from ui.widgets.graph_viewer.utils import ASTConverter


class GraphViewer(GraphViewerCore):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.set_grab_mode(True)
        self.set_keyboard_navigation_speed(15)

    def load_graph_from_json_data(self, graph_data):
        """
        Carrega o grafo na cena a partir de uma lista de dicionários.
        """
        if not graph_data:
            return

        # Limpa a cena anterior
        self.scene().clear()

        nodes = {}

        root_id = self._find_root_node(graph_data)

        # Calcula o layout hierárquico
        positions = self._calculate_tree_layout(graph_data, root_id)

        # 1. Cria os Nós com posições calculadas
        for i, node_data in enumerate(graph_data):
            node_id = i
            name = node_data.get("name", f"Nó {i}")
            original_data = node_data.get("data", {})

            # Usa a posição calculada pelo layout de árvore
            position = positions.get(node_id, QPointF(0, 0))

            node_item = NodeItem(name, node_id, position, original_data)
            self.scene().addItem(node_item)
            nodes[node_id] = node_item

        # 2. Cria as Arestas
        for source_id, node_data in enumerate(graph_data):
            source_node = nodes[source_id]

            # connections é a lista de IDs de destino
            for dest_id in node_data.get("connections", []):
                if dest_id in nodes:
                    dest_node = nodes[dest_id]
                    edge = EdgeItem(source_node, dest_node)
                    self.scene().addItem(edge)

        # 3. Ajusta o tamanho da cena baseado no conteúdo
        self._adjust_scene_size(positions)

    def _find_root_node(self, graph_data):
        """
        Encontra o nó raiz (que não é filho de nenhum outro nó).
        """
        all_children = set()
        for node_data in graph_data:
            all_children.update(node_data.get("connections", []))

        # O nó raiz é aquele que não aparece como filho de ninguém
        for i in range(len(graph_data)):
            if i not in all_children:
                return i

        # Se não encontrar, retorna 0 como fallback
        return 0

    def _calculate_tree_layout(self, graph_data, root_id):
        """
        Calcula as posições dos nós para um layout de árvore hierárquico.

        Este algoritmo funciona em três etapas:
        1. Atribui níveis aos nós (profundidade na árvore)
        2. Calcula a largura necessária para cada subárvore
        3. Posiciona os nós recursivamente, centralizando subárvores
        """
        # Configurações do layout - ajustáveis conforme necessário

        # Distância vertical entre níveis (aumentada para melhor visualização)
        level_height = 150

        # Espaçamento horizontal mínimo entre nós
        min_node_spacing = 200

        # Estruturas para armazenar informações do layout
        positions = {}
        levels = {}  # level -> [node_ids]
        subtree_widths = {}  # node_id -> largura da subárvore

        # Etapa 1: Calcular níveis de cada nó usando BFS
        self._assign_levels(graph_data, root_id, levels)

        # Primeiro cria os nós temporariamente para obter suas dimensões reais
        temp_nodes = self._create_temporary_nodes(graph_data)

        # Etapa 2: Calcular larguras das subárvores (processamento bottom-up)
        self._calculate_subtree_widths(
            graph_data, levels, subtree_widths, min_node_spacing, temp_nodes
        )

        # Etapa 3: Posicionar nós usando as larguras calculadas
        scene_width = max(800, self.scene().width())  # Largura mínima garantida

        # Posicionar o nó raiz centralizado no topo
        root_x = scene_width / 2
        root_y = 60  # Margem superior
        positions[root_id] = QPointF(root_x, root_y)

        # Posicionar recursivamente toda a árvore a partir da raiz
        self._position_subtree(
            graph_data, root_id, root_x, root_y, positions, subtree_widths, level_height
        )

        return positions

    def _assign_levels(self, graph_data, root_id, levels):
        """
        Atribui níveis (profundidade) aos nós usando BFS.

        Args:
            graph_data: Lista com dados dos nós
            root_id: ID do nó raiz
            levels: Dicionário que será preenchido {level: [node_ids]}
        """
        visited = set()
        queue = [(root_id, 0)]  # (node_id, level)

        while queue:
            node_id, level = queue.pop(0)

            if node_id in visited:
                continue

            visited.add(node_id)

            if level not in levels:
                levels[level] = []
            levels[level].append(node_id)

            # Adicionar filhos à fila
            node_data = graph_data[node_id]
            for child_id in node_data.get("connections", []):
                if child_id not in visited:
                    queue.append((child_id, level + 1))

    def _calculate_subtree_widths(
        self,
        graph_data,
        levels,
        subtree_widths,
        min_spacing,
        temp_nodes,
    ):
        """
        Calcula a largura necessária para cada subárvore (processamento bottom-up).

        A largura de uma subárvore é a soma das larguras de suas subárvores filhas,
        ou o espaçamento mínimo para nós folha.
        """
        max_level = max(levels.keys()) if levels else 0

        # Processar níveis de baixo para cima
        for level in range(max_level, -1, -1):
            for node_id in levels[level]:
                children = graph_data[node_id].get("connections", [])

                if not children:
                    # Nó folha: usa a largura real do nó + margem
                    node_width = (
                        temp_nodes[node_id].rect_width
                        if node_id in temp_nodes
                        else min_spacing
                    )
                    subtree_widths[node_id] = max(min_spacing, node_width + 40)
                else:
                    # Nó interno: soma das larguras dos filhos
                    total_children_width = sum(
                        subtree_widths.get(child_id, min_spacing)
                        for child_id in children
                    )
                    # A largura da subárvore é pelo menos a largura dos filhos ou do nó atual
                    node_width = (
                        temp_nodes[node_id].rect_width
                        if node_id in temp_nodes
                        else min_spacing
                    )
                    subtree_widths[node_id] = max(
                        min_spacing, total_children_width, node_width + 40
                    )

    def _position_subtree(
        self, graph_data, node_id, center_x, y, positions, subtree_widths, level_height
    ):
        """
        Posiciona recursivamente uma subárvore centrada em center_x.

        Args:
            node_id: ID do nó atual
            center_x: Posição X central para esta subárvore
            y: Posição Y do nó atual
            positions: Dicionário onde serão armazenadas as posições
            subtree_widths: Larguras pré-calculadas das subárvores
            level_height: Altura entre níveis
        """
        # Posicionar o nó atual
        positions[node_id] = QPointF(center_x, y)

        # Posicionar os filhos
        children = graph_data[node_id].get("connections", [])
        if not children:
            return

        # Calcular posições dos filhos
        child_y = y + level_height

        # Se há apenas um filho, centralizar sob o pai
        if len(children) == 1:
            child_id = children[0]
            self._position_subtree(
                graph_data,
                child_id,
                center_x,
                child_y,
                positions,
                subtree_widths,
                level_height,
            )
            return

        # Para múltiplos filhos, distribuir horizontalmente
        total_width = sum(subtree_widths.get(child_id, 80) for child_id in children)
        start_x = center_x - total_width / 2

        current_x = start_x
        for child_id in children:
            child_width = subtree_widths.get(child_id, 80)
            child_center_x = current_x + child_width / 2

            self._position_subtree(
                graph_data,
                child_id,
                child_center_x,
                child_y,
                positions,
                subtree_widths,
                level_height,
            )

            current_x += child_width

    def _adjust_scene_size(self, positions):
        """
        Ajusta o tamanho da cena baseado nas posições dos nós e centraliza a visualização.

        Garante que todos os nós sejam visíveis e adiciona margem apropriada.
        """

        if not positions:
            return

        # Encontra os limites da árvore
        min_x = min(pos.x() for pos in positions.values())
        max_x = max(pos.x() for pos in positions.values())
        min_y = min(pos.y() for pos in positions.values())
        max_y = max(pos.y() for pos in positions.values())

        # Adiciona margem confortável para visualização
        margin = 120
        scene_width = max(1000, (max_x - min_x) + 2 * margin)
        scene_height = max(700, (max_y - min_y) + 2 * margin)

        # Ajusta o offset se necessário para centralizar
        if min_x < margin:
            offset_x = margin - min_x
            # Aplica o offset a todos os nós
            for item in self.scene().items():
                if isinstance(item, NodeItem):
                    current_pos = item.pos()
                    item.setPos(current_pos.x() + offset_x, current_pos.y())

        # Define o novo tamanho da cena
        self.scene().setSceneRect(0, 0, scene_width, scene_height)

        # Centraliza a visualização na árvore
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def setText(self, text: str):
        self.text = text
        result = parse_ontology(text)
        self.load_graph(result)

    def toPlainText(self):
        return self.text

    def load_graph(self, result):
        # Extrai apenas a AST do resultado
        ast_root = {
            'package': result.get('package'),
            'imports': result.get('imports'),
            'declarations': result.get('declarations')
        }
        converter = ASTConverter()
        adjacency_list = converter.convert_ast_to_adjacency_list(ast_root)
        self.load_graph_from_json_data(adjacency_list)

    def _create_temporary_nodes(self, graph_data):
        """
        Cria nós temporariamente para calcular suas dimensões reais.
        """
        temp_nodes = {}
        for i, node_data in enumerate(graph_data):
            name = node_data.get("name", f"Nó {i}")
            original_data = node_data.get("data", {})
            temp_node = NodeItem(name, i, QPointF(0, 0), original_data)
            temp_nodes[i] = temp_node
        return temp_nodes
