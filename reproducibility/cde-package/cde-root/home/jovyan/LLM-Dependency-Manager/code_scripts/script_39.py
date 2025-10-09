# Social Network Analysis and Graph Algorithms
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
import community as community_louvain
from collections import defaultdict, deque
import random

def social_network_construction():
    """Build and analyze social network structures"""
    try:
        # Generate synthetic social network
        n_users = 500
        
        # Create different network models
        # 1. Random network (Erdős–Rényi)
        p_random = 0.02
        G_random = nx.erdos_renyi_graph(n_users, p_random)
        
        # 2. Scale-free network (Barabási–Albert)
        m = 3  # Number of edges to attach from a new node
        G_scale_free = nx.barabasi_albert_graph(n_users, m)
        
        # 3. Small-world network (Watts-Strogatz)
        k = 6  # Each node connected to k nearest neighbors
        p_rewire = 0.1
        G_small_world = nx.watts_strogatz_graph(n_users, k, p_rewire)
        
        # Add node attributes (user profiles)
        for G in [G_random, G_scale_free, G_small_world]:
            for node in G.nodes():
                G.nodes[node]['age'] = np.random.randint(18, 65)
                G.nodes[node]['location'] = np.random.choice(['NYC', 'LA', 'Chicago', 'Houston', 'Miami'])
                G.nodes[node]['interests'] = np.random.choice(['Tech', 'Sports', 'Music', 'Art', 'Politics'], 
                                                           size=np.random.randint(1, 4), replace=False).tolist()
                G.nodes[node]['activity_level'] = np.random.exponential(10)
        
        # Add edge attributes (relationship strength)
        for G in [G_random, G_scale_free, G_small_world]:
            for edge in G.edges():
                G.edges[edge]['weight'] = np.random.uniform(0.1, 1.0)
                G.edges[edge]['interaction_frequency'] = np.random.poisson(5)
                G.edges[edge]['relationship_type'] = np.random.choice(['friend', 'family', 'colleague', 'acquaintance'])
        
        # Network analysis
        def analyze_network(G, name):
            # Basic metrics
            n_nodes = G.number_of_nodes()
            n_edges = G.number_of_edges()
            density = nx.density(G)
            
            # Centrality measures
            degree_centrality = nx.degree_centrality(G)
            betweenness_centrality = nx.betweenness_centrality(G, k=min(100, n_nodes))
            closeness_centrality = nx.closeness_centrality(G)
            eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
            
            # Most central nodes
            most_central_degree = max(degree_centrality, key=degree_centrality.get)
            most_central_betweenness = max(betweenness_centrality, key=betweenness_centrality.get)
            
            # Clustering and community structure
            clustering_coefficient = nx.average_clustering(G)
            transitivity = nx.transitivity(G)
            
            # Path lengths
            if nx.is_connected(G):
                avg_path_length = nx.average_shortest_path_length(G)
                diameter = nx.diameter(G)
            else:
                # For disconnected graphs, analyze largest component
                largest_cc = max(nx.connected_components(G), key=len)
                G_cc = G.subgraph(largest_cc)
                avg_path_length = nx.average_shortest_path_length(G_cc)
                diameter = nx.diameter(G_cc)
            
            # Degree distribution
            degrees = [G.degree(n) for n in G.nodes()]
            degree_stats = {
                'mean': np.mean(degrees),
                'std': np.std(degrees),
                'max': max(degrees),
                'min': min(degrees)
            }
            
            return {
                'name': name,
                'nodes': n_nodes,
                'edges': n_edges,
                'density': density,
                'clustering_coefficient': clustering_coefficient,
                'transitivity': transitivity,
                'avg_path_length': avg_path_length,
                'diameter': diameter,
                'degree_stats': degree_stats,
                'most_central_degree': most_central_degree,
                'max_degree_centrality': degree_centrality[most_central_degree],
                'max_betweenness_centrality': betweenness_centrality[most_central_betweenness]
            }
        
        # Analyze all networks
        random_analysis = analyze_network(G_random, 'Random')
        scale_free_analysis = analyze_network(G_scale_free, 'Scale-Free')
        small_world_analysis = analyze_network(G_small_world, 'Small-World')
        
        return {
            'network_models': 3,
            'total_users': n_users,
            'random_network': random_analysis,
            'scale_free_network': scale_free_analysis,
            'small_world_network': small_world_analysis,
            'networks_generated': True
        }
        
    except Exception as e:
        return {'error': str(e)}

def community_detection():
    """Community detection algorithms"""
    try:
        # Create a network with known community structure
        # Using the planted partition model
        n_communities = 4
        community_size = 50
        p_in = 0.3   # Probability of edge within community
        p_out = 0.05  # Probability of edge between communities
        
        G = nx.Graph()
        
        # Add nodes with community labels
        for i in range(n_communities):
            for j in range(community_size):
                node_id = i * community_size + j
                G.add_node(node_id, true_community=i)
        
        # Add edges
        for i in G.nodes():
            for j in range(i + 1, len(G.nodes())):
                comm_i = G.nodes[i]['true_community']
                comm_j = G.nodes[j]['true_community']
                
                if comm_i == comm_j:
                    if np.random.random() < p_in:
                        G.add_edge(i, j)
                else:
                    if np.random.random() < p_out:
                        G.add_edge(i, j)
        
        # Community detection algorithms
        
        # 1. Louvain algorithm
        louvain_communities = community_louvain.best_partition(G)
        louvain_modularity = community_louvain.modularity(louvain_communities, G)
        
        # 2. Greedy modularity optimization
        greedy_communities = list(nx.community.greedy_modularity_communities(G))
        
        # Convert to partition format for comparison
        greedy_partition = {}
        for i, community in enumerate(greedy_communities):
            for node in community:
                greedy_partition[node] = i
        
        greedy_modularity = nx.community.modularity(G, greedy_communities)
        
        # 3. Label propagation
        label_prop_communities = list(nx.community.label_propagation_communities(G))
        label_prop_partition = {}
        for i, community in enumerate(label_prop_communities):
            for node in community:
                label_prop_partition[node] = i
        
        # 4. Spectral clustering using NetworkX
        try:
            spectral_communities = list(nx.community.spectral_clustering(G, n_clusters=n_communities))
            spectral_partition = {}
            for i, community in enumerate(spectral_communities):
                for node in community:
                    spectral_partition[node] = i
        except:
            spectral_partition = {node: 0 for node in G.nodes()}  # Fallback
        
        # Evaluate community detection quality
        def evaluate_communities(true_partition, detected_partition):
            # Normalized Mutual Information
            from sklearn.metrics import normalized_mutual_info_score
            
            true_labels = [true_partition[node] for node in sorted(G.nodes())]
            detected_labels = [detected_partition.get(node, 0) for node in sorted(G.nodes())]
            
            nmi = normalized_mutual_info_score(true_labels, detected_labels)
            
            # Modularity
            communities = defaultdict(list)
            for node, comm in detected_partition.items():
                communities[comm].append(node)
            
            community_sets = [set(nodes) for nodes in communities.values()]
            if community_sets:
                modularity = nx.community.modularity(G, community_sets)
            else:
                modularity = 0
            
            return {
                'nmi': nmi,
                'modularity': modularity,
                'num_communities': len(set(detected_partition.values()))
            }
        
        # True partition
        true_partition = {node: data['true_community'] for node, data in G.nodes(data=True)}
        
        # Evaluate all methods
        louvain_eval = evaluate_communities(true_partition, louvain_communities)
        greedy_eval = evaluate_communities(true_partition, greedy_partition)
        label_prop_eval = evaluate_communities(true_partition, label_prop_partition)
        spectral_eval = evaluate_communities(true_partition, spectral_partition)
        
        # Community characteristics
        def analyze_communities(partition):
            communities = defaultdict(list)
            for node, comm in partition.items():
                communities[comm].append(node)
            
            sizes = [len(nodes) for nodes in communities.values()]
            
            return {
                'num_communities': len(communities),
                'avg_size': np.mean(sizes),
                'size_std': np.std(sizes),
                'largest_community': max(sizes),
                'smallest_community': min(sizes)
            }
        
        louvain_analysis = analyze_communities(louvain_communities)
        
        return {
            'network_nodes': G.number_of_nodes(),
            'network_edges': G.number_of_edges(),
            'true_communities': n_communities,
            'algorithms_tested': 4,
            'louvain': {
                'communities_found': louvain_analysis['num_communities'],
                'modularity': louvain_eval['modularity'],
                'nmi': louvain_eval['nmi']
            },
            'greedy': {
                'communities_found': greedy_eval['num_communities'],
                'modularity': greedy_eval['modularity'],
                'nmi': greedy_eval['nmi']
            },
            'label_propagation': {
                'communities_found': label_prop_eval['num_communities'],
                'modularity': label_prop_eval['modularity'],
                'nmi': label_prop_eval['nmi']
            },
            'spectral': {
                'communities_found': spectral_eval['num_communities'],
                'modularity': spectral_eval['modularity'],
                'nmi': spectral_eval['nmi']
            },
            'best_nmi': max(louvain_eval['nmi'], greedy_eval['nmi'], 
                          label_prop_eval['nmi'], spectral_eval['nmi'])
        }
        
    except Exception as e:
        return {'error': str(e)}

def influence_propagation():
    """Information and influence propagation models"""
    try:
        # Create social network
        n_nodes = 200
        G = nx.barabasi_albert_graph(n_nodes, 3)
        
        # Add node attributes
        for node in G.nodes():
            G.nodes[node]['threshold'] = np.random.uniform(0.1, 0.8)  # Threshold for adoption
            G.nodes[node]['influence'] = np.random.uniform(0.1, 1.0)   # Influence strength
            G.nodes[node]['susceptibility'] = np.random.uniform(0.1, 1.0)  # Susceptibility to influence
        
        # Linear Threshold Model
        def linear_threshold_model(G, initial_adopters, max_steps=20):
            adopters = set(initial_adopters)
            adoption_timeline = [len(adopters)]
            
            for step in range(max_steps):
                new_adopters = set()
                
                for node in G.nodes():
                    if node not in adopters:
                        # Calculate influence from neighbors
                        neighbor_influence = 0
                        for neighbor in G.neighbors(node):
                            if neighbor in adopters:
                                edge_weight = G.edges[node, neighbor].get('weight', 1.0)
                                influence = G.nodes[neighbor]['influence']
                                neighbor_influence += edge_weight * influence
                        
                        # Normalize by degree
                        if G.degree(node) > 0:
                            neighbor_influence /= G.degree(node)
                        
                        # Check if threshold is exceeded
                        threshold = G.nodes[node]['threshold']
                        if neighbor_influence >= threshold:
                            new_adopters.add(node)
                
                adopters.update(new_adopters)
                adoption_timeline.append(len(adopters))
                
                if len(new_adopters) == 0:  # No new adopters
                    break
            
            return adopters, adoption_timeline
        
        # Independent Cascade Model
        def independent_cascade_model(G, initial_adopters, max_steps=20):
            adopters = set(initial_adopters)
            newly_activated = set(initial_adopters)
            adoption_timeline = [len(adopters)]
            
            for step in range(max_steps):
                next_activated = set()
                
                for node in newly_activated:
                    for neighbor in G.neighbors(node):
                        if neighbor not in adopters:
                            # Activation probability based on edge weight and influence
                            edge_weight = G.edges[node, neighbor].get('weight', 0.1)
                            influence = G.nodes[node]['influence']
                            susceptibility = G.nodes[neighbor]['susceptibility']
                            
                            activation_prob = edge_weight * influence * susceptibility
                            
                            if np.random.random() < activation_prob:
                                next_activated.add(neighbor)
                
                adopters.update(next_activated)
                newly_activated = next_activated
                adoption_timeline.append(len(adopters))
                
                if len(newly_activated) == 0:
                    break
            
            return adopters, adoption_timeline
        
        # Select initial adopters (high centrality nodes)
        centrality = nx.degree_centrality(G)
        top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        initial_adopters = [node for node, _ in top_nodes]
        
        # Run propagation models
        lt_adopters, lt_timeline = linear_threshold_model(G, initial_adopters)
        ic_adopters, ic_timeline = independent_cascade_model(G, initial_adopters)
        
        # Viral coefficient analysis
        def calculate_viral_coefficient(timeline):
            if len(timeline) < 2:
                return 0
            
            growth_rates = []
            for i in range(1, len(timeline)):
                if timeline[i-1] > 0:
                    growth_rate = (timeline[i] - timeline[i-1]) / timeline[i-1]
                    growth_rates.append(growth_rate)
            
            return np.mean(growth_rates) if growth_rates else 0
        
        lt_viral_coeff = calculate_viral_coefficient(lt_timeline)
        ic_viral_coeff = calculate_viral_coefficient(ic_timeline)
        
        # Influence maximization (greedy algorithm)
        def greedy_influence_maximization(G, k=10, model='lt'):
            selected = []
            
            for _ in range(k):
                best_node = None
                best_spread = 0
                
                # Try each remaining node
                for node in G.nodes():
                    if node not in selected:
                        test_set = selected + [node]
                        
                        # Estimate spread
                        if model == 'lt':
                            adopters, _ = linear_threshold_model(G, test_set)
                        else:
                            adopters, _ = independent_cascade_model(G, test_set)
                        
                        spread = len(adopters)
                        
                        if spread > best_spread:
                            best_spread = spread
                            best_node = node
                
                if best_node is not None:
                    selected.append(best_node)
            
            return selected, best_spread
        
        # Find optimal seed sets
        lt_seeds, lt_max_spread = greedy_influence_maximization(G, k=5, model='lt')
        ic_seeds, ic_max_spread = greedy_influence_maximization(G, k=5, model='ic')
        
        # Network resilience analysis
        def analyze_network_resilience(G):
            original_components = nx.number_connected_components(G)
            largest_cc_size = len(max(nx.connected_components(G), key=len))
            
            # Remove high centrality nodes and measure impact
            betweenness = nx.betweenness_centrality(G)
            top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
            
            G_copy = G.copy()
            for node, _ in top_betweenness[:5]:  # Remove top 5
                G_copy.remove_node(node)
            
            new_components = nx.number_connected_components(G_copy)
            if nx.number_connected_components(G_copy) > 0:
                new_largest_cc = len(max(nx.connected_components(G_copy), key=len))
            else:
                new_largest_cc = 0
            
            resilience_score = new_largest_cc / largest_cc_size
            
            return {
                'original_components': original_components,
                'components_after_attack': new_components,
                'resilience_score': resilience_score,
                'nodes_removed': 5
            }
        
        resilience = analyze_network_resilience(G)
        
        return {
            'network_size': n_nodes,
            'initial_adopters': len(initial_adopters),
            'propagation_models': 2,
            'linear_threshold': {
                'final_adopters': len(lt_adopters),
                'adoption_rate': len(lt_adopters) / n_nodes,
                'steps_to_completion': len(lt_timeline),
                'viral_coefficient': lt_viral_coeff
            },
            'independent_cascade': {
                'final_adopters': len(ic_adopters),
                'adoption_rate': len(ic_adopters) / n_nodes,
                'steps_to_completion': len(ic_timeline),
                'viral_coefficient': ic_viral_coeff
            },
            'influence_maximization': {
                'lt_optimal_spread': lt_max_spread,
                'ic_optimal_spread': ic_max_spread,
                'seed_set_size': 5
            },
            'network_resilience': resilience['resilience_score'],
            'components_after_attack': resilience['components_after_attack']
        }
        
    except Exception as e:
        return {'error': str(e)}

def graph_machine_learning():
    """Machine learning on graphs and networks"""
    try:
        # Create graph with node features
        n_nodes = 300
        G = nx.barabasi_albert_graph(n_nodes, 4)
        
        # Generate node features
        n_features = 10
        node_features = {}
        
        for node in G.nodes():
            # Random features + some structure based on network position
            features = np.random.randn(n_features)
            
            # Add network-based features
            features[0] = G.degree(node)  # Degree
            features[1] = nx.clustering(G, node)  # Local clustering coefficient
            
            # Add some community-based features
            neighbors = list(G.neighbors(node))
            if neighbors:
                features[2] = np.mean([G.degree(n) for n in neighbors])  # Average neighbor degree
            
            node_features[node] = features
        
        # Create adjacency matrix
        A = nx.adjacency_matrix(G)
        
        # Feature matrix
        X = np.array([node_features[node] for node in sorted(G.nodes())])
        
        # Generate labels for nodes (e.g., user categories)
        # Based on network structure and features
        true_labels = []
        for node in sorted(G.nodes()):
            degree = G.degree(node)
            clustering = nx.clustering(G, node)
            
            if degree > 10 and clustering > 0.3:
                label = 0  # Influential connector
            elif degree > 8:
                label = 1  # Hub
            elif clustering > 0.5:
                label = 2  # Local cluster member
            else:
                label = 3  # Peripheral node
            
            true_labels.append(label)
        
        true_labels = np.array(true_labels)
        
        # Graph-based machine learning algorithms
        
        # 1. Node clustering using features
        kmeans = KMeans(n_clusters=4, random_state=42)
        feature_clusters = kmeans.fit_predict(X)
        
        # 2. Spectral clustering using graph structure
        try:
            # Compute graph Laplacian
            L = nx.normalized_laplacian_matrix(G)
            
            # Eigendecomposition
            eigenvals, eigenvecs = eigsh(L, k=4, which='SM')
            
            # K-means on eigenvectors
            spectral_clusters = KMeans(n_clusters=4, random_state=42).fit_predict(eigenvecs)
        except:
            # Fallback if spectral clustering fails
            spectral_clusters = np.random.randint(0, 4, n_nodes)
        
        # 3. Combined feature + structure clustering
        # Concatenate node features with spectral embedding
        try:
            combined_features = np.hstack([X, eigenvecs])
            combined_clusters = KMeans(n_clusters=4, random_state=42).fit_predict(combined_features)
        except:
            combined_clusters = feature_clusters
        
        # Evaluate clustering quality
        def evaluate_clustering(true_labels, pred_labels):
            from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
            
            ari = adjusted_rand_score(true_labels, pred_labels)
            nmi = normalized_mutual_info_score(true_labels, pred_labels)
            
            return {'ari': ari, 'nmi': nmi}
        
        feature_eval = evaluate_clustering(true_labels, feature_clusters)
        spectral_eval = evaluate_clustering(true_labels, spectral_clusters)
        combined_eval = evaluate_clustering(true_labels, combined_clusters)
        
        # Graph neural network simulation (simplified)
        def simulate_gnn():
            # Simulate GNN training process
            n_layers = 3
            hidden_dim = 64
            
            # Message passing simulation
            node_embeddings = X.copy()
            
            for layer in range(n_layers):
                new_embeddings = np.zeros((n_nodes, hidden_dim))
                
                for node in range(n_nodes):
                    # Aggregate neighbor features
                    neighbors = list(G.neighbors(node))
                    if neighbors:
                        neighbor_features = np.mean([node_embeddings[n] for n in neighbors], axis=0)
                        # Simple update rule
                        new_embeddings[node] = 0.5 * node_embeddings[node][:hidden_dim] + 0.5 * neighbor_features[:hidden_dim]
                    else:
                        new_embeddings[node] = node_embeddings[node][:hidden_dim]
                
                node_embeddings = new_embeddings
            
            # Final classification
            gnn_clusters = KMeans(n_clusters=4, random_state=42).fit_predict(node_embeddings)
            gnn_eval = evaluate_clustering(true_labels, gnn_clusters)
            
            return {
                'layers': n_layers,
                'embedding_dim': hidden_dim,
                'ari': gnn_eval['ari'],
                'nmi': gnn_eval['nmi']
            }
        
        gnn_result = simulate_gnn()
        
        # Link prediction
        def link_prediction():
            # Remove 20% of edges for testing
            edges = list(G.edges())
            n_test_edges = len(edges) // 5
            test_edges = random.sample(edges, n_test_edges)
            
            # Create training graph
            G_train = G.copy()
            G_train.remove_edges_from(test_edges)
            
            # Generate negative samples (non-edges)
            non_edges = list(nx.non_edges(G))
            negative_samples = random.sample(non_edges, n_test_edges)
            
            # Simple link prediction based on common neighbors
            def predict_link_score(u, v, graph):
                common_neighbors = len(list(nx.common_neighbors(graph, u, v)))
                jaccard = common_neighbors / len(set(graph.neighbors(u)) | set(graph.neighbors(v))) if len(set(graph.neighbors(u)) | set(graph.neighbors(v))) > 0 else 0
                return jaccard
            
            # Predict scores
            pos_scores = [predict_link_score(u, v, G_train) for u, v in test_edges]
            neg_scores = [predict_link_score(u, v, G_train) for u, v in negative_samples]
            
            # Calculate AUC
            from sklearn.metrics import roc_auc_score
            y_true = [1] * len(pos_scores) + [0] * len(neg_scores)
            y_scores = pos_scores + neg_scores
            
            try:
                auc = roc_auc_score(y_true, y_scores)
            except:
                auc = 0.5  # Random performance
            
            return {
                'test_edges': n_test_edges,
                'auc_score': auc,
                'avg_pos_score': np.mean(pos_scores),
                'avg_neg_score': np.mean(neg_scores)
            }
        
        link_pred_result = link_prediction()
        
        return {
            'graph_ml_methods': 4,  # Feature clustering, Spectral, Combined, GNN
            'nodes': n_nodes,
            'features_per_node': n_features,
            'true_classes': len(np.unique(true_labels)),
            'feature_clustering_ari': feature_eval['ari'],
            'spectral_clustering_ari': spectral_eval['ari'],
            'combined_clustering_ari': combined_eval['ari'],
            'gnn_simulation': gnn_result,
            'link_prediction': link_pred_result,
            'best_clustering_method': max(
                [('feature', feature_eval['ari']), 
                 ('spectral', spectral_eval['ari']), 
                 ('combined', combined_eval['ari'])], 
                key=lambda x: x[1]
            )[0]
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Social network analysis and graph algorithms operations...")
    
    # Social network construction
    network_result = social_network_construction()
    if 'error' not in network_result:
        print(f"Networks: {network_result['network_models']} models, {network_result['total_users']} users")
    
    # Community detection
    community_result = community_detection()
    if 'error' not in community_result:
        print(f"Communities: {community_result['algorithms_tested']} algorithms, best NMI: {community_result['best_nmi']:.3f}")
    
    # Influence propagation
    influence_result = influence_propagation()
    if 'error' not in influence_result:
        print(f"Influence: LT {influence_result['linear_threshold']['adoption_rate']:.1%}, IC {influence_result['independent_cascade']['adoption_rate']:.1%} adoption")
    
    # Graph machine learning
    graph_ml_result = graph_machine_learning()
    if 'error' not in graph_ml_result:
        print(f"Graph ML: Best clustering ARI {graph_ml_result['combined_clustering_ari']:.3f}, Link prediction AUC {graph_ml_result['link_prediction']['auc_score']:.3f}")