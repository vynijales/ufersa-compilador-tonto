
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem


class NodeItem(QGraphicsItem):
    """Representa um Nó no estilo tabela UML/Ontologia."""

    def __init__(self, name, node_id, position=QPointF(0, 0), data=None):
        super().__init__()

        self.setPos(position)
        self.node_id = node_id
        self.name = name
        self.data = data or {}
        self.edges = []

        # Configurações visuais
        self.padding = 8
        self.line_height = 16
        self.header_height = 20
        self.min_width = 120

        # Torna o nó arrastável
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

        # Cores baseadas no tipo do nó
        self.colors = self._get_colors_for_type()

        # Calcula dimensões e prepara seções
        self.sections = self._prepare_sections()
        self._calculate_dimensions()

        # Cria elementos de texto como filhos
        self._create_text_items()

    def _get_colors_for_type(self):
        """Retorna cores baseadas no tipo do elemento da AST."""
        node_type = self.data.get("type", "default")

        color_schemes = {
            "enum": {
                "bg": QColor(255, 230, 204),
                "header": QColor(255, 140, 0),
                "border": QColor(204, 102, 0),
            },
            "datatype": {
                "bg": QColor(230, 255, 230),
                "header": QColor(76, 175, 80),
                "border": QColor(56, 142, 60),
            },
            "kind": {
                "bg": QColor(255, 240, 245),
                "header": QColor(233, 30, 99),
                "border": QColor(194, 24, 91),
            },
            "role": {
                "bg": QColor(255, 245, 250),
                "header": QColor(233, 30, 99),
                "border": QColor(194, 24, 91),
            },
            "relation_external": {
                "bg": QColor(227, 242, 253),
                "header": QColor(33, 150, 243),
                "border": QColor(25, 118, 210),
            },
            "genset": {
                "bg": QColor(248, 231, 28),
                "header": QColor(205, 220, 57),
                "border": QColor(175, 180, 43),
            },
            "relator": {
                "bg": QColor(240, 230, 250),
                "header": QColor(138, 43, 226),
                "border": QColor(102, 51, 153),
            },
            "subkind": {
                "bg": QColor(255, 240, 220),
                "header": QColor(255, 152, 0),
                "border": QColor(230, 126, 34),
            },
            "phase": {
                "bg": QColor(230, 245, 255),
                "header": QColor(3, 169, 244),
                "border": QColor(2, 136, 209),
            },
            "mode": {
                "bg": QColor(232, 245, 233),
                "header": QColor(76, 175, 80),
                "border": QColor(46, 125, 50),
            },
            "quality": {
                "bg": QColor(255, 248, 225),
                "header": QColor(255, 193, 7),
                "border": QColor(255, 143, 0),
            },
            "event": {
                "bg": QColor(255, 235, 238),
                "header": QColor(244, 67, 54),
                "border": QColor(211, 47, 47),
            },
            "situation": {
                "bg": QColor(224, 247, 250),
                "header": QColor(0, 188, 212),
                "border": QColor(0, 151, 167),
            },
            "package": {
                "bg": QColor(227, 233, 255),
                "header": QColor(63, 81, 181),
                "border": QColor(48, 63, 159),
            },
            "imports": {
                "bg": QColor(224, 255, 255),
                "header": QColor(0, 150, 136),
                "border": QColor(0, 121, 107),
            },
            "default": {
                "bg": QColor(245, 245, 245),
                "header": QColor(158, 158, 158),
                "border": QColor(117, 117, 117),
            },
        }

        return color_schemes.get(node_type, color_schemes["default"])

    def _prepare_sections(self):
        """Prepara as seções do nó baseado nos dados da AST."""
        sections = []
        node_type = self.data.get("type", "")

        # Cabeçalho sempre presente
        stereotype = f"<<{node_type}>>" if node_type else ""
        sections.append(
            {
                "type": "header",
                "content": [stereotype, self.name] if stereotype else [self.name],
            }
        )

        # Seções específicas por tipo
        if node_type == "enum":
            values = self.data.get("values", [])
            if values:
                sections.append(
                    {"type": "values", "title": "Values:", "content": values}
                )

        elif node_type == "datatype":
            attributes = self.data.get("attributes", [])
            if attributes:
                attr_content = []
                for attr in attributes:
                    attr_name = attr.get("name", "")
                    attr_type = attr.get("datatype", "")
                    attr_content.append(f"{attr_name}: {attr_type}")
                sections.append(
                    {
                        "type": "attributes",
                        "title": "Attributes:",
                        "content": attr_content,
                    }
                )

        elif node_type == "kind":
            # Adiciona informação de especialização se existir
            specializes = self.data.get("specializes")
            if specializes:
                sections.append(
                    {
                        "type": "specialization",
                        "title": "Specializes:",
                        "content": [specializes],
                    }
                )

            content = self.data.get("content", {})
            if content:  # Verifica se content não é None
                attributes = content.get("attributes", [])
                relations = content.get("relations", [])

                if attributes:
                    attr_content = []
                    for attr in attributes:
                        attr_name = attr.get("name", "")
                        attr_type = attr.get("datatype", "")
                        attr_content.append(f"{attr_name}: {attr_type}")
                    sections.append(
                        {
                            "type": "attributes",
                            "title": "Attributes:",
                            "content": attr_content,
                        }
                    )

                if relations:
                    rel_content = []
                    for rel in relations:
                        rel_entry = self._format_relation(rel)
                        if rel_entry:
                            rel_content.append(rel_entry)
                    if rel_content:
                        sections.append(
                            {"type": "relations", "title": "Relations:", "content": rel_content}
                        )
            else:
                # Content é None ou vazio
                sections.append(
                    {
                        "type": "empty_content",
                        "title": "Content:",
                        "content": ["(empty)"],
                    }
                )

        elif node_type == "role":
            # Adiciona informação de especialização se existir
            specializes = self.data.get("specializes")
            if specializes:
                sections.append(
                    {
                        "type": "specialization",
                        "title": "Specializes:",
                        "content": [specializes],
                    }
                )

            content = self.data.get("content", {})
            if content:  # Verifica se content não é None
                attributes = content.get("attributes", [])
                relations = content.get("relations", [])

                if attributes:
                    attr_content = []
                    for attr in attributes:
                        attr_name = attr.get("name", "")
                        attr_type = attr.get("datatype", "")
                        attr_content.append(f"{attr_name}: {attr_type}")
                    sections.append(
                        {
                            "type": "attributes",
                            "title": "Attributes:",
                            "content": attr_content,
                        }
                    )

                if relations:
                    rel_content = []
                    for rel in relations:
                        rel_entry = self._format_relation(rel)
                        if rel_entry:
                            rel_content.append(rel_entry)
                    if rel_content:
                        sections.append(
                            {"type": "relations", "title": "Relations:", "content": rel_content}
                        )
            else:
                # Content é None ou vazio
                sections.append(
                    {
                        "type": "empty_content",
                        "title": "Content:",
                        "content": ["(empty)"],
                    }
                )

        elif node_type in ["relator", "subkind", "phase", "mode", "quality", "event", "situation"]:
            # Adiciona informação de categoria se existir (para subkinds, phases, roles)
            category = self.data.get("category")
            if category:
                sections.append(
                    {
                        "type": "category",
                        "title": "Category:",
                        "content": [category],
                    }
                )

            # Adiciona informação de especialização se existir
            specializes = self.data.get("specializes")
            if specializes:
                sections.append(
                    {
                        "type": "specialization",
                        "title": "Specializes:",
                        "content": [specializes],
                    }
                )

            content = self.data.get("content", {})
            if content:  # Verifica se content não é None
                attributes = content.get("attributes", [])
                relations = content.get("relations", [])

                if attributes:
                    attr_content = []
                    for attr in attributes:
                        attr_name = attr.get("name", "")
                        attr_type = attr.get("datatype", "")
                        attr_content.append(f"{attr_name}: {attr_type}")
                    sections.append(
                        {
                            "type": "attributes",
                            "title": "Attributes:",
                            "content": attr_content,
                        }
                    )

                if relations:
                    rel_content = []
                    for rel in relations:
                        rel_entry = self._format_relation(rel)
                        if rel_entry:
                            rel_content.append(rel_entry)
                    if rel_content:
                        sections.append(
                            {"type": "relations", "title": "Relations:", "content": rel_content}
                        )

            # Se content existe mas está vazio, mostra seções apropriadas
            if content is not None:
                # Adiciona informação sobre atributos vazios se necessário
                if not content.get("attributes") and not content.get("relations"):
                    sections.append(
                        {
                            "type": "info",
                            "title": "Info:",
                            "content": ["No attributes or relations defined"],
                        }
                    )
            else:
                # Content é None
                sections.append(
                    {
                        "type": "empty_content",
                        "title": "Content:",
                        "content": ["(null)"],
                    }
                )

        elif node_type in ["package", "imports"]:
            # Nós simples para package e imports - apenas mostram o nome
            node_name = self.data.get("name", "")
            if node_name:
                sections.append(
                    {
                        "type": "value",
                        "title": "Value:",
                        "content": [node_name],
                    }
                )

        elif node_type == "relation_external":
            relation_info = []

            stereotype = self.data.get("relation_stereotype", "")
            if stereotype:
                relation_info.append(f"<<{stereotype}>>")

            connector = self.data.get("connector", {})
            if connector:
                label = connector.get("label", "")
                conn_type = connector.get("connector", "")
                if label:
                    relation_info.append(f"Label: {label}")
                if conn_type:
                    relation_info.append(f"Connector: {conn_type}")

            domain = self.data.get("domain", "")
            domain_card = self.data.get("domain_cardinality", "")
            image = self.data.get("image", "")
            image_card = self.data.get("image_cardinality", "")

            if domain:
                domain_str = f"{domain}"
                if domain_card:
                    domain_str += f" {domain_card}"
                relation_info.append(f"Domain: {domain_str}")

            if image:
                image_str = f"{image}"
                if image_card:
                    image_str += f" {image_card}"
                relation_info.append(f"Image: {image_str}")

            if relation_info:
                sections.append(
                    {
                        "type": "relation_info",
                        "title": "Details:",
                        "content": relation_info,
                    }
                )

        elif node_type == "genset":
            genset_info = []

            restrictions = self.data.get("genset_restrictions", [])
            if restrictions:
                genset_info.append(f"Restrictions: {', '.join(restrictions)}")

            specifics = self.data.get("specifics", [])
            if specifics:
                genset_info.append(f"Specifics: {', '.join(specifics)}")

            general = self.data.get("general", "")
            if general:
                genset_info.append(f"General: {general}")

            if genset_info:
                sections.append(
                    {
                        "type": "genset_info",
                        "title": "Generalization:",
                        "content": genset_info,
                    }
                )

        return sections

    def _calculate_dimensions(self):
        """Calcula as dimensões necessárias para o nó."""
        font = QFont("Arial", 9)
        header_font = QFont("Arial", 10, QFont.Bold)

        max_width = self.min_width
        total_height = 0

        for section in self.sections:
            if section["type"] == "header":
                # Cabeçalho
                for line in section["content"]:
                    text_width = self._get_text_width(line, header_font)
                    max_width = max(max_width, text_width + 2 * self.padding)
                total_height += len(section["content"]) * self.header_height
            else:
                # Título da seção
                if "title" in section:
                    title_width = self._get_text_width(section["title"], header_font)
                    max_width = max(max_width, title_width + 2 * self.padding)
                    total_height += self.line_height

                # Conteúdo da seção
                for line in section["content"]:
                    text_width = self._get_text_width(line, font)
                    max_width = max(max_width, text_width + 2 * self.padding)
                    total_height += self.line_height

                total_height += 4  # Espaço entre seções

        self.rect_width = max_width
        self.rect_height = total_height + self.padding

    def _get_text_width(self, text, font):
        """Calcula a largura do texto com a fonte especificada."""
        from PyQt5.QtGui import QFontMetrics

        metrics = QFontMetrics(font)
        return metrics.width(text)

    def _create_text_items(self):
        """Cria os itens de texto como elementos filhos."""
        font = QFont("Arial", 9)
        header_font = QFont("Arial", 10, QFont.Bold)

        current_y = -self.rect_height / 2 + self.padding

        for section in self.sections:
            if section["type"] == "header":
                # Renderiza cabeçalho
                for line in section["content"]:
                    text_item = QGraphicsSimpleTextItem(line, self)
                    text_item.setFont(header_font)
                    text_item.setPos(
                        -self._get_text_width(line, header_font) / 2, current_y
                    )
                    current_y += self.header_height
            else:
                # Título da seção
                if "title" in section:
                    text_item = QGraphicsSimpleTextItem(section["title"], self)
                    text_item.setFont(header_font)
                    text_item.setPos(-self.rect_width / 2 + self.padding, current_y)
                    current_y += self.line_height

                # Conteúdo da seção
                for line in section["content"]:
                    text_item = QGraphicsSimpleTextItem(f"  {line}", self)  # Indentação
                    text_item.setFont(font)
                    text_item.setPos(-self.rect_width / 2 + self.padding, current_y)
                    current_y += self.line_height

                current_y += 4  # Espaço entre seções

    def boundingRect(self):
        """Define o retângulo delimitador do nó."""
        return QRectF(
            -self.rect_width / 2,
            -self.rect_height / 2,
            self.rect_width,
            self.rect_height,
        )

    def paint(self, painter, option, widget=None):
        """Desenha o nó no estilo tabela UML."""
        rect = self.boundingRect()

        # Desenha fundo
        painter.setBrush(QBrush(self.colors["bg"]))
        painter.setPen(QPen(self.colors["border"], 1.5))
        painter.drawRoundedRect(rect, 3, 3)

        # Desenha cabeçalho destacado
        if self.sections and self.sections[0]["type"] == "header":
            header_lines = len(self.sections[0]["content"])
            header_height = header_lines * self.header_height

            header_rect = QRectF(
                rect.left(), rect.top(), rect.width(), header_height + self.padding
            )

            painter.setBrush(QBrush(self.colors["header"]))
            painter.setPen(QPen(self.colors["border"], 1.5))
            painter.drawRoundedRect(header_rect, 3, 3)

            # Desenha linha separadora
            separator_y = header_rect.bottom()
            painter.drawLine(
                QPointF(rect.left(), separator_y), QPointF(rect.right(), separator_y)
            )

        # Desenha linhas separadoras entre seções
        current_y = -self.rect_height / 2 + self.padding

        for i, section in enumerate(self.sections):
            if section["type"] == "header":
                current_y += len(section["content"]) * self.header_height
                if i < len(self.sections) - 1:  # Não desenha linha após a última seção
                    painter.drawLine(
                        QPointF(rect.left() + 5, current_y),
                        QPointF(rect.right() - 5, current_y),
                    )
            else:
                if "title" in section:
                    current_y += self.line_height
                current_y += len(section["content"]) * self.line_height + 4

    def itemChange(self, change, value):
        """Atualiza as arestas quando o nó se move."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Notifica todas as arestas conectadas para que se atualizem
            for edge in self.edges:
                edge.adjust()
        elif change == QGraphicsItem.ItemSelectedChange:
            # Muda a aparência quando selecionado/arrastado
            if value:
                # Destaque quando selecionado
                original_colors = self.colors.copy()
                self.colors["border"] = QColor(255, 87, 34)  # Laranja para seleção
                self.update()
            else:
                # Volta às cores originais
                self.colors = self._get_colors_for_type()
                self.update()
        return super().itemChange(change, value)

    def add_edge(self, edge):
        """Adiciona uma aresta conectada a este nó."""
        self.edges.append(edge)

    def set_hover_state(self, is_hovering):
        """
        Define o estado de hover do nó.

        Args:
            is_hovering (bool): True se o mouse está sobre o nó
        """
        if is_hovering:
            # Escurece ligeiramente as cores no hover
            self.colors["bg"] = self.colors["bg"].darker(110)
            self.colors["header"] = self.colors["header"].darker(110)
        else:
            # Restaura cores originais
            if not self.isSelected():
                self.colors = self._get_colors_for_type()

        self.update()

    def _format_relation(self, relation):
        """
        Formata uma relação para exibição no nó.
        """
        rel_type = relation.get("type", "")
        rel_stereotype = relation.get("relation_stereotype", "")

        # Para relações internas (mediation)
        if rel_type == "relation_internal":
            connector = relation.get("connector", {})
            connector_type = connector.get("connector", "--")

            domain_card = relation.get("domain_cardinality", "")
            image = relation.get("image", "")
            image_card = relation.get("image_cardinality", "")

            # Formato melhorado: @stereotype [card] -- [card] Target
            parts = []

            if rel_stereotype:
                parts.append(f"@{rel_stereotype}")

            # Monta a string da relação de forma mais legível
            relation_parts = []

            if domain_card:
                relation_parts.append(domain_card)

            relation_parts.append(connector_type)

            if image_card:
                relation_parts.append(image_card)

            if image:
                relation_parts.append(image)

            if relation_parts:
                parts.append(" ".join(relation_parts))

            result = " ".join(parts) if parts else "mediation relation"
            return result

        # Para outros tipos de relação
        elif rel_type == "relation_external":
            label = relation.get("label", "")
            return f"→ {label}" if label else "→ external relation"

        # Para relações simples (nome e tipo)
        else:
            rel_name = relation.get("name", "")
            if rel_name:
                return f"{rel_name}: {rel_type}"
            else:
                return rel_type if rel_type else "unnamed relation"
