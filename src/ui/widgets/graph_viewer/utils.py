class ASTConverter:
    def __init__(self):
        self.adjacency_list = []
        self.node_counter = 0

    def _generate_node_id(self, key_context):
        """Gera um ID/Nome mais descritivo para cada nó com base no contexto."""
        self.node_counter += 1
        return f"{key_context}_{self.node_counter}"

    def _traverse_and_build(self, node_data, key_context="Root"):
        """
        Função recursiva para percorrer a estrutura e construir a lista de adjacências.
        Retorna o índice onde o nó atual foi inserido.
        """
        if not isinstance(node_data, (dict, list)):
            # Se não for um dicionário ou lista, não é um nó que precisamos mapear
            # (Ex: 'teste', 'RED', 'string').
            # Retornamos None para indicar que não houve inserção de nó.
            return None

        # 1. Gerar o nome/ID do nó e inicializar a entrada na lista de adjacências
        # node_name = self._generate_node_id(key_context)
        node_name = key_context

        if isinstance(node_data, dict):
            node_type = node_data.get("type", key_context)
            node_name = f"{node_type}: {node_data.get('name')}"

        current_node_index = len(
            self.adjacency_list
        )  # O índice onde o nó ATUAL será inserido
        self.adjacency_list.append({"name": node_name, "connections": []})

        # Lista de conexões do nó atual
        children_indices = []

        if isinstance(node_data, dict):
            # 2. Processar Dicionário: Cada valor que é um dict ou list é um filho.
            for key, value in node_data.items():
                # Chamada recursiva para processar o valor
                # O key é usado como contexto (ex: 'declarations', 'attributes', 'content')
                child_index = self._traverse_and_build(value, key)

                if child_index is not None:
                    children_indices.append(child_index)

        elif isinstance(node_data, list):
            # 3. Processar Lista: Cada item na lista que é um dict ou list é um filho.
            for sub_index, sub_value in enumerate(node_data):
                # Usamos o sub_index para dar um contexto (ex: 'Item_0', 'Item_1', etc.)
                child_index = self._traverse_and_build(
                    sub_value, f"{key_context}_Item_{sub_index}"
                )

                if child_index is not None:
                    children_indices.append(child_index)

        # 4. Atualizar a lista de conexões do nó atual
        self.adjacency_list[current_node_index]["connections"] = children_indices

        # Retornar o índice onde o nó atual foi inserido para que o nó PAI possa se conectar a ele
        return current_node_index

    def convert_ast_to_adjacency_list(self, ast_dict):
        """Método principal para iniciar a conversão."""
        # Resetar o estado para uma nova conversão
        self.adjacency_list = []
        self.node_counter = 0

        # Iniciar a recursão com a AST completa
        self._traverse_and_build(ast_dict)

        return self.adjacency_list
