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
            # Para strings simples em contextos específicos, cria nós
            if key_context == "package" and isinstance(node_data, str):
                return self._create_simple_node(node_data, "package")
            elif key_context.startswith("import_") and isinstance(node_data, str):
                return self._create_simple_node(node_data, "imports")
            return None

        # Verifica se é um elemento que deve ser ignorado (já exibido no nó pai)
        if isinstance(node_data, dict) and self._should_skip_node(
            node_data, key_context
        ):
            return None

        # 1. Gerar o nome/ID do nó e inicializar a entrada na lista de adjacências
        node_name = key_context

        if isinstance(node_data, dict):
            node_type = node_data.get("type", key_context)
            node_name = f"{node_type}: {node_data.get('name')}"

        current_node_index = len(self.adjacency_list)

        # Inclui os dados originais no nó se for um dicionário
        node_entry = {"name": node_name, "connections": []}
        if isinstance(node_data, dict):
            node_entry["data"] = node_data.copy()

        self.adjacency_list.append(node_entry)

        # Lista de conexões do nó atual
        children_indices = []

        if isinstance(node_data, dict):
            # 2. Processar Dicionário: Apenas chaves relevantes que devem gerar nós filhos
            for key, value in node_data.items():
                if self._should_process_key(key, node_data):
                    # Para package, só cria nó se não for null
                    if key == "package" and value is not None:
                        child_index = self._traverse_and_build(value, key)
                        if child_index is not None:
                            children_indices.append(child_index)
                    elif key != "package":
                        child_index = self._traverse_and_build(value, key)
                        if child_index is not None:
                            children_indices.append(child_index)

        elif isinstance(node_data, list):
            # 3. Processar Lista: Cada item na lista que é um dict ou list é um filho
            for sub_index, sub_value in enumerate(node_data):
                # Para imports, usa o valor da string como contexto
                if key_context == "imports" and isinstance(sub_value, str):
                    child_context = f"import_{sub_value}"
                else:
                    child_context = f"{key_context}_Item_{sub_index}"
                
                child_index = self._traverse_and_build(sub_value, child_context)
                if child_index is not None:
                    children_indices.append(child_index)

        # 4. Atualizar a lista de conexões do nó atual
        self.adjacency_list[current_node_index]["connections"] = children_indices

        return current_node_index

    def _create_simple_node(self, value, node_type):
        """
        Cria um nó simples para valores string (package, imports).
        """
        node_name = f"{node_type}: {value}" if value else f"{node_type}: (null)"
        current_node_index = len(self.adjacency_list)
        
        node_entry = {
            "name": node_name,
            "connections": [],
            "data": {"type": node_type, "name": value}
        }
        
        self.adjacency_list.append(node_entry)
        return current_node_index

    def _should_skip_node(self, node_data, key_context):
        """
        Determina se um nó deve ser ignorado por ser informação redundante.
        """
        # Ignora nós de atributos individuais, valores de enum, etc.
        skip_contexts = [
            "attributes",  # Lista de atributos já exibida no nó pai
            "values",  # Valores de enum já exibidos no nó pai
            "relations",  # Relações já exibidas no nó pai
            "content",  # Conteúdo já processado no nó pai
            "specifics",  # Específicos de genset já exibidos no nó pai
            "connector",  # Detalhes de conector já exibidos no nó pai
        ]

        return key_context in skip_contexts

    def _should_process_key(self, key, parent_data):
        """
        Determina se uma chave deve ser processada para gerar nós filhos.
        """
        # Chaves que devem ser ignoradas (informações internas do nó)
        internal_keys = {
            "type",
            "name",
            "values",
            "attributes",
            "relations",
            "content",
            "genset_restrictions",
            "specifics",
            "general",
            "relation_stereotype",
            "connector",
            "domain",
            "domain_cardinality",
            "image",
            "image_cardinality",
            "errors",
            "warnings",
        }

        # Processa chaves que representam estruturas hierárquicas reais
        structural_keys = {"declarations", "imports", "package"}

        return key in structural_keys

    def convert_ast_to_adjacency_list(self, ast_dict):
        """Método principal para iniciar a conversão."""
        # Resetar o estado para uma nova conversão
        self.adjacency_list = []
        self.node_counter = 0

        # Iniciar a recursão com a AST completa
        self._traverse_and_build(ast_dict)

        return self.adjacency_list
