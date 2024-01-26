from collections import defaultdict
from copy import copy
from multiprocessing import Pool
import numpy as np
import torch

class Match:


    def set_match_stopwords(self, stopwords):
        """
        Set the stopwords for invalid relations.

        Args:
            stopwords (set): The set of stopwords to be used.

        Returns:
            None
        """

        self.invalid_relations_set = stopwords

    def parse_sentence(self, sentence, tokenizer, encoder, nlp):
        """
        Parses a sentence to extract triplets of relations between entities.

        Args:
            sentence (str): The input sentence to parse.
            tokenizer (Tokenizer): The tokenizer used to tokenize the sentence.
            encoder (Encoder): The encoder used to encode the inputs.
            nlp (NLP): The natural language processing library used for additional processing.

        Returns:
            list: A list of triplets representing the extracted relations between entities.
        """

        # TRAM mobility data
        tokenizer_name = str(tokenizer.__str__)

        # Create mapping for inputs
        inputs, tokenid2word_mapping, token2id, noun_chunks = self.create_mapping(
            sentence, return_pt=True, nlp=nlp, tokenizer=tokenizer)

        # Encode inputs using the encoder
        with torch.no_grad():
            outputs = encoder(**inputs, output_attentions=True)

        trim = True

        # Process attention matrix
        attention = self.process_matrix(outputs[2], avg_head=True, trim=trim)

        merged_attention = self.compress_attention(
            attention, tokenid2word_mapping)

        # Build attention graph
        attn_graph = self.build_graph(merged_attention)

        tail_head_pairs = []

        # Generate pairs of noun chunks
        for head in noun_chunks:
            for tail in noun_chunks:
                if head != tail:
                    tail_head_pairs.append((token2id[head], token2id[tail]))

        black_list_relation = set([token2id[n] for n in noun_chunks])

        all_relation_pairs = []

        id2token = {value: key for key, value in token2id.items()}

        # Use Beam search method (BFS) to get relations for each pair of (head, tail)
        with Pool(1) as pool:
            params = [(pair[0], pair[1], attn_graph, max(
                tokenid2word_mapping), black_list_relation, ) for pair in tail_head_pairs]
            for output in pool.imap_unordered(self.bfs, params):
                if len(output):
                    all_relation_pairs += [(o, id2token) for o in output]

        triplet_text = []
        
        # Filter and process relation sets to build triplets
        with Pool(1, self.global_initializer, (nlp,)) as pool:
            for triplet in pool.imap_unordered(self.filter_relation_sets, all_relation_pairs):
                if len(triplet) > 0:
                    triplet_text.append(triplet)

        return triplet_text

    def create_mapping(self, sentence, return_pt=False, nlp=None, tokenizer=None):
        """
        Create a mapping of tokens in a sentence to their corresponding IDs and word mappings.

        Args:
            sentence (str): The input sentence to be processed.
            return_pt (bool, optional): Whether to return PyTorch tensors. Defaults to False.
            nlp (object, optional): The NLP object for sentence processing. Defaults to None.
            tokenizer (object, optional): The tokenizer object for tokenization. Defaults to None.

        Returns:
            dict: A dictionary containing the token mappings and other relevant information.
        """
        doc = nlp(sentence)

        start_chunk = []
        end_chunk = []
        noun_chunks = []
        for chunk in doc.noun_chunks:
            noun_chunks.append(chunk.text)
            start_chunk.append(chunk.start)
            end_chunk.append(chunk.end)

        sentence_mapping = []
        token2id = {}
        mode = 0  # 1 in chunk, 0 not in chunk
        chunk_id = 0
        for idx, token in enumerate(doc):
            if idx in start_chunk:
                mode = 1
                sentence_mapping.append(noun_chunks[chunk_id])
                token2id[sentence_mapping[-1]] = len(token2id)
                chunk_id += 1
            elif idx in end_chunk:
                mode = 0

            if mode == 0:
                sentence_mapping.append(token.text)
                token2id[sentence_mapping[-1]] = len(token2id)

        token_ids = []
        tokenid2word_mapping = []

        for token in sentence_mapping:
            subtoken_ids = tokenizer(str(token), add_special_tokens=False)['input_ids']
            tokenid2word_mapping += [token2id[token]] * len(subtoken_ids)
            token_ids += subtoken_ids

        tokenizer_name = str(tokenizer.__str__)
        outputs = {
            'input_ids': [tokenizer.cls_token_id] + token_ids + [tokenizer.sep_token_id],
            'attention_mask': [1] * (len(token_ids) + 2),
            'token_type_ids': [0] * (len(token_ids) + 2)
        }

        if return_pt:
            for key, value in outputs.items():
                outputs[key] = torch.from_numpy(np.array(value)).long().unsqueeze(0)

        return outputs, tokenid2word_mapping, token2id, noun_chunks

    def process_matrix(self, attentions, layer_idx=-1, head_num=0, avg_head=False, trim=True):
        """
        Process the attention matrix.

        Args:
            attentions (list): List of attention matrices.
            layer_idx (int): Index of the layer to consider. Default is -1 (last layer).
            head_num (int): Index of the attention head to consider. Default is 0 (first head).
            avg_head (bool): Whether to average over all attention heads. Default is False.
            trim (bool): Whether to trim the attention matrix. Default is True.

        Returns:
            numpy.ndarray: Processed attention matrix.
        """
        # Get the attention matrix
        if avg_head:
            attn = torch.mean(attentions[0][layer_idx], 0)
        else:
            attn = attentions[0][layer_idx][head_num]

        # Convert the attention matrix to a numpy array
        attention_matrix = attn.detach().numpy()

        # Trim the attention matrix if necessary
        if trim:
            attention_matrix = attention_matrix[1:-1, 1:-1]

        return attention_matrix

    def compress_attention(self, attention, tokenid2word_mapping, operator=np.mean):
        """
        Compresses the attention matrix by applying an operator to rows with the same token ID.

        Args:
            attention (np.ndarray): The attention matrix.
            tokenid2word_mapping (dict): A dictionary mapping token IDs to words.
            operator (function): The operator to be applied to rows with the same token ID. Default is np.mean.

        Returns:
            np.ndarray: The compressed attention matrix.
        """
        # Compress attention matrix by grouping rows with the same token ID
        new_index = []
        prev = -1
        for idx, row in enumerate(attention):
            token_id = tokenid2word_mapping[idx]
            if token_id != prev:
                new_index.append([row])
                prev = token_id
            else:
                new_index[-1].append(row)

        # Apply operator to each group of rows
        new_matrix = []
        for row in new_index:
            new_matrix.append(operator(np.array(row), 0))

        new_matrix = np.array(new_matrix)
        attention = np.array(new_matrix).T

        # Compress attention matrix again after transposing
        prev = -1
        new_index = []
        for idx, row in enumerate(attention):
            token_id = tokenid2word_mapping[idx]
            if token_id != prev:
                new_index.append([row])
                prev = token_id
            else:
                new_index[-1].append(row)

        # Apply operator to each group of rows after transposing
        new_matrix = []
        for row in new_index:
            new_matrix.append(operator(np.array(row), 0))

        new_matrix = np.array(new_matrix)
        return new_matrix.T

    def build_graph(self,matrix):
        """Builds a graph from a matrix.

        Args:
            matrix (list of list): The matrix representing the graph.

        Returns:
            defaultdict: The graph represented as a defaultdict with adjacency lists.
        """
        graph = defaultdict(list)

        for idx in range(len(matrix)):
            for col in range(idx + 1, len(matrix)):
                graph[idx].append((col, matrix[idx][col]))

        return graph

    def bfs(self, args):
        """
        Perform a breadth-first search from node s to node end in a graph.

        Args:
            args (tuple): A tuple containing the following elements:
                s: The start node.
                end: The end node.
                graph: The graph represented as an adjacency list.
                max_size: The maximum size of the graph.
                black_list_relation: A list of relations to ignore.

        Returns:
            bool: True if there is a path from s to end, False otherwise.
        """
        s, end, graph, max_size, black_list_relation = args
        return self.BFS(s, end, graph, max_size, black_list_relation)

    def BFS(self, s, end, graph, max_size=-1, black_list_relation=[]):
        """
        Perform a breadth-first search from node s to node end in the given graph.

        Args:
            s (int): The source node.
            end (int): The target node.
            graph (dict): The graph representation.
            max_size (int, optional): The maximum size of the graph. Defaults to -1.
            black_list_relation (list, optional): The list of relations to exclude. Defaults to [].

        Returns:
            list: The list of candidate facts, where each candidate fact is a tuple (path, confidence).
        """
        # Initialize visited array
        visited = [False] * (max(graph.keys()) + 100)

        # Create a queue for BFS
        queue = []

        # Mark the source node as visited and enqueue it
        queue.append((s, [(s, 0)]))

        found_paths = []
        visited[s] = True
        while queue:
            s, path = queue.pop(0)
            for i, conf in graph[s]:
                if i == end:
                    found_paths.append(path + [(i, conf)])
                    break
                if not visited[i]:
                    queue.append((i, copy(path) + [(i, conf)]))
                    visited[i] = True

        candidate_facts = []
        for path_pairs in found_paths:
            if len(path_pairs) < 3:
                continue
            path = []
            cum_conf = 0
            for (node, conf) in path_pairs:
                path.append(node)
                cum_conf += conf

            if path[1] in black_list_relation:
                continue

            candidate_facts.append((path, cum_conf))

        candidate_facts = sorted(candidate_facts, key=lambda x: x[1], reverse=True)
        return candidate_facts

    def global_initializer(self, nlp_object):
        """
        Initializes the global spacy_nlp object.
        
        Args:
            nlp_object: The Spacy NLP object to be assigned to the global spacy_nlp variable.
        """
        # Assign the nlp_object to the global spacy_nlp variable
        global spacy_nlp
        spacy_nlp = nlp_object

    def filter_relation_sets(self, params):
        """
        Filter the relation sets based on certain conditions.

        Args:
            params (tuple): A tuple containing the triplet and id2token dictionary.

        Returns:
            dict: A dictionary containing the filtered relation sets.

        """

        triplet, id2token = params

        triplet_idx = triplet[0]
        confidence = triplet[1]
        head, tail = triplet_idx[0], triplet_idx[-1]
        
        # Check if head and tail exist in id2token
        if head in id2token and tail in id2token:
            head = id2token[head]
            tail = id2token[tail]

            relations = []
            
            # Iterate over the indices in triplet_idx excluding the first and last element
            for idx in triplet_idx[1:-1]:
                if idx in id2token:
                    relations.append(spacy_nlp(id2token[idx])[0].lemma_)

            # Check if relations list is not empty, if relations are valid, and if head and tail are not in the invalid_relations_set
            if len(relations) > 0 and self.check_relations_validity(relations) and head.lower() not in self.invalid_relations_set and tail.lower() not in self.invalid_relations_set:
                return {'h': head, 't': tail, 'r': relations, 'c': confidence}
        
        return {}

    def check_relations_validity(self, relations):
        """
        Check the validity of relations.

        Args:
            relations (list): The list of relations to check.

        Returns:
            bool: True if all relations are valid, False otherwise.
        """
        # Iterate over each relation
        for rel in relations:
            # Check if the relation is in the set of invalid relations or if it is numeric
            if rel.lower() in self.invalid_relations_set or rel.isnumeric():
                # Return False if the relation is invalid
                return False
        # Return True if all relations are valid
        return True
