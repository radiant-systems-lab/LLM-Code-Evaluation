# Bioinformatics and Computational Biology
import numpy as np
from Bio import SeqIO, Align, Phylo
from Bio.Seq import Seq
from Bio.SeqUtils import molecular_weight, GC
from Bio.SeqRecord import SeqRecord
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx

def dna_sequence_analysis():
    """DNA sequence analysis and manipulation"""
    try:
        # Sample DNA sequences
        sequences = [
            "ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATC",
            "ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATT",
            "ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATG",
            "ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATA",
            "ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATC"
        ]
        
        # Create Seq objects
        seq_objects = [Seq(seq) for seq in sequences]
        
        # Basic sequence analysis
        analysis_results = []
        for i, seq in enumerate(seq_objects):
            analysis = {
                'sequence_id': f'seq_{i+1}',
                'length': len(seq),
                'gc_content': GC(seq),
                'molecular_weight': molecular_weight(seq, 'DNA'),
                'complement': str(seq.complement()),
                'reverse_complement': str(seq.reverse_complement()),
                'translation': str(seq.translate())
            }
            analysis_results.append(analysis)
        
        # Find ORFs (Open Reading Frames)
        def find_orfs(sequence, min_length=30):
            orfs = []
            start_codons = ['ATG']
            stop_codons = ['TAA', 'TAG', 'TGA']
            
            for frame in range(3):
                for i in range(frame, len(sequence) - 2, 3):
                    codon = sequence[i:i+3]
                    if codon in start_codons:
                        # Look for stop codon
                        for j in range(i + 3, len(sequence) - 2, 3):
                            stop_codon = sequence[j:j+3]
                            if stop_codon in stop_codons:
                                orf_length = j - i + 3
                                if orf_length >= min_length:
                                    orfs.append({
                                        'start': i,
                                        'end': j + 3,
                                        'length': orf_length,
                                        'frame': frame,
                                        'sequence': sequence[i:j+3]
                                    })
                                break
            return orfs
        
        # Find ORFs in first sequence
        orfs = find_orfs(sequences[0])
        
        # Sequence alignment simulation
        def pairwise_alignment_score(seq1, seq2):
            # Simple scoring: match=2, mismatch=-1, gap=-2
            if len(seq1) != len(seq2):
                return -1000  # Penalty for different lengths
            
            score = 0
            for i, (base1, base2) in enumerate(zip(seq1, seq2)):
                if base1 == base2:
                    score += 2
                else:
                    score -= 1
            return score
        
        # Calculate pairwise alignment scores
        alignment_scores = []
        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                score = pairwise_alignment_score(sequences[i], sequences[j])
                alignment_scores.append({
                    'seq1': f'seq_{i+1}',
                    'seq2': f'seq_{j+1}',
                    'score': score,
                    'identity': score / (len(sequences[i]) * 2)  # Normalized score
                })
        
        # Motif finding (simple pattern search)
        motifs = ['ATGC', 'CGAT', 'GATC', 'TCGA']
        motif_counts = {}
        
        for motif in motifs:
            counts = []
            for seq in sequences:
                count = 0
                for i in range(len(seq) - len(motif) + 1):
                    if seq[i:i+len(motif)] == motif:
                        count += 1
                counts.append(count)
            motif_counts[motif] = counts
        
        return {
            'sequences_analyzed': len(sequences),
            'average_length': np.mean([len(seq) for seq in sequences]),
            'average_gc_content': np.mean([result['gc_content'] for result in analysis_results]),
            'orfs_found': len(orfs),
            'longest_orf': max(orfs, key=lambda x: x['length'])['length'] if orfs else 0,
            'pairwise_alignments': len(alignment_scores),
            'best_alignment_score': max(alignment_scores, key=lambda x: x['score'])['score'] if alignment_scores else 0,
            'motifs_searched': len(motifs),
            'total_motif_occurrences': sum(sum(counts) for counts in motif_counts.values())
        }
        
    except Exception as e:
        return {'error': str(e)}

def protein_analysis():
    """Protein sequence analysis and structure prediction"""
    try:
        # Sample protein sequences
        protein_sequences = [
            "MKWVTFISLLLLFSSAYSRGVFRRDTHKSEIAHRFKDLGEEHFKGLVLIAFSQYLQQCPFDEHVKLVNELTEFAKTCVADESHAGCEKSLHTLFGDELCKVASLRETYGDMADCCEKQEPERNECFLSHKDDSPDLPKLKPDPNTLCDEFKADEKKFWGKYLYEIARRHPYFYAPELLYYANKYNGVFQECCQAEDKGACLLPKIETMREKVLASSARQRLRCASIQKFGERALKAWSVARLSQKFPKAEFVEVTKLVTDLTKVHKECCHGDLLECADDRADLAKYICDNQDTISSKLKECCDKPVNGFNLSYLQLGQFQPLFKKCAERFAEKLF",
            "MVLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSHPETLEKFDRVKHLKTEAEMKASEDLKKHGVTVLTALGAILKKKGHHEAELKPLAQSHATKHKIPIKYLEFISEAIIHVLHSRHPGNFGADAQGAMNKLTQFAQLF",
            "MKALIVLGLVLLVVLGVVGNLLLVLVAGDVSLPGLVTDLKLFGVVGNVLLIVLVVRVRKPSLLSPLVVDLLVDTLVKVVGHVLLLVVGVVLTVLIVLLVGLVVV"
        ]
        
        # Create Seq objects for proteins
        protein_seqs = [Seq(seq) for seq in protein_sequences]
        
        # Amino acid composition analysis
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        aa_composition = {}
        
        for aa in amino_acids:
            composition = []
            for seq in protein_sequences:
                count = seq.count(aa)
                percentage = (count / len(seq)) * 100
                composition.append(percentage)
            aa_composition[aa] = composition
        
        # Physical properties calculation
        def calculate_properties(sequence):
            # Hydrophobicity scale (Kyte-Doolittle)
            hydrophobicity_scale = {
                'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5, 'M': 1.9,
                'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8, 'W': -0.9, 'Y': -1.3,
                'P': -1.6, 'H': -3.2, 'E': -3.5, 'Q': -3.5, 'D': -3.5, 'N': -3.5,
                'K': -3.9, 'R': -4.5
            }
            
            # Molecular weight of amino acids
            aa_weights = {
                'A': 71.04, 'C': 103.01, 'D': 115.03, 'E': 129.04, 'F': 147.07,
                'G': 57.02, 'H': 137.06, 'I': 113.08, 'K': 128.09, 'L': 113.08,
                'M': 131.04, 'N': 114.04, 'P': 97.05, 'Q': 128.06, 'R': 156.10,
                'S': 87.03, 'T': 101.05, 'V': 99.07, 'W': 186.08, 'Y': 163.06
            }
            
            hydrophobicity = sum(hydrophobicity_scale.get(aa, 0) for aa in sequence) / len(sequence)
            molecular_weight = sum(aa_weights.get(aa, 0) for aa in sequence)
            
            # Charge calculation (simplified)
            positive_aa = 'RHK'
            negative_aa = 'DE'
            net_charge = sum(1 for aa in sequence if aa in positive_aa) - sum(1 for aa in sequence if aa in negative_aa)
            
            return {
                'hydrophobicity': hydrophobicity,
                'molecular_weight': molecular_weight,
                'net_charge': net_charge,
                'length': len(sequence)
            }
        
        protein_properties = [calculate_properties(seq) for seq in protein_sequences]
        
        # Secondary structure prediction (simplified)
        def predict_secondary_structure(sequence):
            # Simplified Chou-Fasman method approximation
            alpha_helix_propensity = {
                'A': 1.42, 'E': 1.51, 'L': 1.21, 'M': 1.45, 'Q': 1.11, 'H': 1.00,
                'K': 1.16, 'R': 0.98, 'S': 0.77, 'Y': 0.69, 'F': 1.13, 'W': 1.08,
                'I': 1.08, 'V': 1.06, 'T': 0.83, 'C': 0.70, 'D': 1.01, 'N': 0.67,
                'G': 0.57, 'P': 0.57
            }
            
            beta_sheet_propensity = {
                'V': 1.70, 'I': 1.60, 'Y': 1.47, 'F': 1.38, 'W': 1.37, 'L': 1.30,
                'T': 1.19, 'A': 0.83, 'M': 1.05, 'C': 1.19, 'R': 0.93, 'K': 0.74,
                'S': 0.75, 'H': 0.87, 'D': 0.54, 'E': 0.37, 'N': 0.89, 'Q': 1.10,
                'G': 0.75, 'P': 0.55
            }
            
            helix_score = sum(alpha_helix_propensity.get(aa, 1.0) for aa in sequence) / len(sequence)
            sheet_score = sum(beta_sheet_propensity.get(aa, 1.0) for aa in sequence) / len(sequence)
            
            # Predict dominant structure
            if helix_score > sheet_score:
                dominant_structure = 'alpha_helix'
            else:
                dominant_structure = 'beta_sheet'
            
            return {
                'helix_propensity': helix_score,
                'sheet_propensity': sheet_score,
                'dominant_structure': dominant_structure
            }
        
        structure_predictions = [predict_secondary_structure(seq) for seq in protein_sequences]
        
        # Domain prediction (simple hydrophobicity-based)
        def identify_domains(sequence, window_size=20):
            domains = []
            
            for i in range(0, len(sequence) - window_size + 1, window_size):
                window = sequence[i:i + window_size]
                properties = calculate_properties(window)
                
                domain_type = 'unknown'
                if properties['hydrophobicity'] > 1.0:
                    domain_type = 'transmembrane'
                elif properties['net_charge'] > 3:
                    domain_type = 'dna_binding'
                elif properties['hydrophobicity'] < -1.0:
                    domain_type = 'extracellular'
                
                domains.append({
                    'start': i,
                    'end': i + window_size,
                    'type': domain_type,
                    'hydrophobicity': properties['hydrophobicity']
                })
            
            return domains
        
        # Identify domains in first protein
        domains = identify_domains(protein_sequences[0])
        
        return {
            'proteins_analyzed': len(protein_sequences),
            'average_length': np.mean([len(seq) for seq in protein_sequences]),
            'total_amino_acids': sum(len(seq) for seq in protein_sequences),
            'hydrophobicity_range': [min(prop['hydrophobicity'] for prop in protein_properties),
                                   max(prop['hydrophobicity'] for prop in protein_properties)],
            'molecular_weight_range': [min(prop['molecular_weight'] for prop in protein_properties),
                                     max(prop['molecular_weight'] for prop in protein_properties)],
            'structure_predictions': len(structure_predictions),
            'domains_identified': len(domains),
            'amino_acid_types': len(amino_acids)
        }
        
    except Exception as e:
        return {'error': str(e)}

def phylogenetic_analysis():
    """Phylogenetic analysis and tree construction"""
    try:
        # Sample sequences for phylogenetic analysis
        species_sequences = {
            'Human': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATCG',
            'Chimp': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATCG',
            'Gorilla': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATCA',
            'Orangutan': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATCT',
            'Mouse': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATTT',
            'Rat': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGATGT',
            'Dog': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGAGCG',
            'Cat': 'ATGCGATCGTAGCTAGCTACGATCGATCGATCGATCGATCGATCGATCGATCATGCGAGCT'
        }
        
        # Calculate pairwise distances
        species = list(species_sequences.keys())
        n_species = len(species)
        distance_matrix = np.zeros((n_species, n_species))
        
        for i, sp1 in enumerate(species):
            for j, sp2 in enumerate(species):
                if i != j:
                    seq1 = species_sequences[sp1]
                    seq2 = species_sequences[sp2]
                    
                    # Calculate Hamming distance
                    distance = sum(c1 != c2 for c1, c2 in zip(seq1, seq2)) / len(seq1)
                    distance_matrix[i][j] = distance
        
        # Construct neighbor-joining tree (simplified)
        def neighbor_joining_simple(distance_matrix, species_names):
            n = len(species_names)
            if n < 3:
                return None
            
            # Find pair with minimum distance
            min_dist = float('inf')
            min_i, min_j = 0, 1
            
            for i in range(n):
                for j in range(i + 1, n):
                    if distance_matrix[i][j] < min_dist:
                        min_dist = distance_matrix[i][j]
                        min_i, min_j = i, j
            
            return {
                'closest_pair': (species_names[min_i], species_names[min_j]),
                'distance': min_dist,
                'tree_depth': 1  # Simplified
            }
        
        tree_info = neighbor_joining_simple(distance_matrix, species)
        
        # Bootstrap analysis simulation
        def bootstrap_analysis(sequences, n_bootstrap=100):
            bootstrap_support = {}
            seq_length = len(list(sequences.values())[0])
            
            for _ in range(n_bootstrap):
                # Random sampling with replacement
                bootstrap_positions = np.random.choice(seq_length, seq_length, replace=True)
                bootstrap_sequences = {}
                
                for species, seq in sequences.items():
                    bootstrap_seq = ''.join(seq[pos] for pos in bootstrap_positions)
                    bootstrap_sequences[species] = bootstrap_seq
                
                # Calculate tree for bootstrap sample
                # Simplified: just track which pairs cluster together
                # In practice, this would involve full tree reconstruction
                
            # Simulated bootstrap values
            bootstrap_support = {
                ('Human', 'Chimp'): 98,
                ('Gorilla', 'Orangutan'): 85,
                ('Mouse', 'Rat'): 95,
                ('Dog', 'Cat'): 78
            }
            
            return bootstrap_support
        
        bootstrap_values = bootstrap_analysis(species_sequences)
        
        # Molecular clock analysis
        def molecular_clock_analysis(distance_matrix, species_names):
            # Simplified molecular clock assuming constant rate
            # In practice, this would involve more sophisticated statistical methods
            
            clock_rates = {}
            for i, species in enumerate(species_names):
                # Average distance to all other species as proxy for divergence time
                avg_distance = np.mean([distance_matrix[i][j] for j in range(len(species_names)) if i != j])
                clock_rates[species] = avg_distance
            
            return clock_rates
        
        clock_rates = molecular_clock_analysis(distance_matrix, species)
        
        # Sequence diversity metrics
        def calculate_diversity_metrics(sequences):
            all_sequences = list(sequences.values())
            
            # Nucleotide diversity
            total_differences = 0
            total_comparisons = 0
            
            for i in range(len(all_sequences)):
                for j in range(i + 1, len(all_sequences)):
                    differences = sum(c1 != c2 for c1, c2 in zip(all_sequences[i], all_sequences[j]))
                    total_differences += differences
                    total_comparisons += 1
            
            nucleotide_diversity = total_differences / (total_comparisons * len(all_sequences[0]))
            
            # GC content variation
            gc_contents = []
            for seq in all_sequences:
                gc_count = seq.count('G') + seq.count('C')
                gc_content = gc_count / len(seq)
                gc_contents.append(gc_content)
            
            return {
                'nucleotide_diversity': nucleotide_diversity,
                'gc_content_mean': np.mean(gc_contents),
                'gc_content_std': np.std(gc_contents)
            }
        
        diversity_metrics = calculate_diversity_metrics(species_sequences)
        
        return {
            'species_analyzed': len(species),
            'sequence_length': len(list(species_sequences.values())[0]),
            'pairwise_distances_calculated': (n_species * (n_species - 1)) // 2,
            'closest_species_pair': tree_info['closest_pair'] if tree_info else None,
            'minimum_distance': tree_info['distance'] if tree_info else 0,
            'bootstrap_analyses': len(bootstrap_values),
            'highest_bootstrap_support': max(bootstrap_values.values()) if bootstrap_values else 0,
            'nucleotide_diversity': diversity_metrics['nucleotide_diversity'],
            'molecular_clock_calculated': True
        }
        
    except Exception as e:
        return {'error': str(e)}

def gene_expression_analysis():
    """Gene expression analysis and differential expression"""
    try:
        # Simulate gene expression data (RNA-seq like)
        n_genes = 1000
        n_samples = 12  # 6 control, 6 treatment
        
        np.random.seed(42)
        
        # Generate gene names
        gene_names = [f'GENE_{i:04d}' for i in range(n_genes)]
        
        # Generate expression data
        # Control samples
        control_expression = np.random.negative_binomial(10, 0.3, (n_genes, 6))
        
        # Treatment samples (some genes differentially expressed)
        treatment_expression = np.random.negative_binomial(10, 0.3, (n_genes, 6))
        
        # Introduce differential expression in 10% of genes
        n_de_genes = int(0.1 * n_genes)
        de_gene_indices = np.random.choice(n_genes, n_de_genes, replace=False)
        
        for idx in de_gene_indices:
            # Randomly make genes up or down regulated
            fold_change = np.random.choice([-2, 2])  # 2-fold up or down
            if fold_change > 0:
                treatment_expression[idx] = treatment_expression[idx] * 2
            else:
                treatment_expression[idx] = treatment_expression[idx] // 2
        
        # Combine data
        expression_data = np.hstack([control_expression, treatment_expression])
        sample_labels = ['Control'] * 6 + ['Treatment'] * 6
        
        # Create DataFrame
        expression_df = pd.DataFrame(
            expression_data.T,
            columns=gene_names,
            index=[f'Sample_{i}' for i in range(n_samples)]
        )
        expression_df['Condition'] = sample_labels
        
        # Differential expression analysis (simplified)
        def differential_expression_analysis(data, conditions):
            de_results = []
            
            control_indices = [i for i, cond in enumerate(conditions) if cond == 'Control']
            treatment_indices = [i for i, cond in enumerate(conditions) if cond == 'Treatment']
            
            for gene_idx, gene in enumerate(gene_names):
                control_values = data[control_indices, gene_idx]
                treatment_values = data[treatment_indices, gene_idx]
                
                # Simple t-test-like analysis
                control_mean = np.mean(control_values)
                treatment_mean = np.mean(treatment_values)
                
                if control_mean > 0:  # Avoid division by zero
                    fold_change = treatment_mean / control_mean
                    log2_fc = np.log2(fold_change) if fold_change > 0 else 0
                else:
                    log2_fc = 0
                
                # Simplified p-value calculation
                pooled_std = np.sqrt((np.var(control_values) + np.var(treatment_values)) / 2)
                if pooled_std > 0:
                    t_stat = abs(treatment_mean - control_mean) / pooled_std
                    # Very simplified p-value approximation
                    p_value = 2 * (1 - min(0.5 + t_stat / 10, 0.99))
                else:
                    p_value = 1.0
                
                de_results.append({
                    'gene': gene,
                    'log2_fold_change': log2_fc,
                    'p_value': p_value,
                    'control_mean': control_mean,
                    'treatment_mean': treatment_mean
                })
            
            return de_results
        
        de_results = differential_expression_analysis(expression_data, sample_labels)
        
        # Filter significant genes
        significant_genes = [gene for gene in de_results if gene['p_value'] < 0.05 and abs(gene['log2_fold_change']) > 1]
        upregulated = [gene for gene in significant_genes if gene['log2_fold_change'] > 1]
        downregulated = [gene for gene in significant_genes if gene['log2_fold_change'] < -1]
        
        # Gene set enrichment analysis (simplified)
        def pathway_analysis(gene_list):
            # Simulate pathway databases
            pathways = {
                'Cell_Cycle': ['GENE_0001', 'GENE_0010', 'GENE_0025', 'GENE_0050'],
                'Apoptosis': ['GENE_0005', 'GENE_0015', 'GENE_0035', 'GENE_0075'],
                'Immune_Response': ['GENE_0008', 'GENE_0020', 'GENE_0040', 'GENE_0080'],
                'Metabolism': ['GENE_0012', 'GENE_0030', 'GENE_0060', 'GENE_0090']
            }
            
            enriched_pathways = []
            de_gene_names = [gene['gene'] for gene in gene_list]
            
            for pathway, pathway_genes in pathways.items():
                overlap = len(set(de_gene_names) & set(pathway_genes))
                if overlap > 0:
                    enrichment_score = overlap / len(pathway_genes)
                    enriched_pathways.append({
                        'pathway': pathway,
                        'overlap': overlap,
                        'enrichment_score': enrichment_score
                    })
            
            return enriched_pathways
        
        enriched_pathways = pathway_analysis(significant_genes)
        
        # Principal component analysis
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(expression_data.T)
        
        # Clustering analysis
        kmeans = KMeans(n_clusters=2, random_state=42)
        cluster_labels = kmeans.fit_predict(expression_data.T)
        
        return {
            'total_genes': n_genes,
            'total_samples': n_samples,
            'differentially_expressed_genes': len(significant_genes),
            'upregulated_genes': len(upregulated),
            'downregulated_genes': len(downregulated),
            'enriched_pathways': len(enriched_pathways),
            'pca_explained_variance': pca.explained_variance_ratio_.sum(),
            'clustering_performed': True,
            'max_fold_change': max([abs(gene['log2_fold_change']) for gene in de_results]),
            'min_p_value': min([gene['p_value'] for gene in de_results])
        }
        
    except Exception as e:
        return {'error': str(e)}

def protein_protein_interaction():
    """Protein-protein interaction network analysis"""
    try:
        # Simulate protein interaction data
        proteins = [f'PROT_{i:03d}' for i in range(50)]
        
        # Generate random interactions
        np.random.seed(42)
        interactions = []
        
        for i in range(len(proteins)):
            for j in range(i + 1, len(proteins)):
                # Random probability of interaction
                if np.random.random() < 0.1:  # 10% chance of interaction
                    confidence = np.random.uniform(0.5, 1.0)
                    interactions.append({
                        'protein_a': proteins[i],
                        'protein_b': proteins[j],
                        'confidence': confidence
                    })
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes
        G.add_nodes_from(proteins)
        
        # Add edges
        for interaction in interactions:
            G.add_edge(
                interaction['protein_a'],
                interaction['protein_b'],
                weight=interaction['confidence']
            )
        
        # Network analysis
        # Centrality measures
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        
        # Find hub proteins (high degree centrality)
        hub_proteins = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Community detection
        communities = list(nx.connected_components(G))
        
        # Path analysis
        try:
            # Average shortest path length
            avg_path_length = nx.average_shortest_path_length(G)
        except:
            avg_path_length = 0  # Graph might not be connected
        
        # Clustering coefficient
        clustering_coefficient = nx.average_clustering(G)
        
        # Network motifs (simple triangles)
        triangles = sum(nx.triangles(G).values()) // 3
        
        # Functional annotation simulation
        def functional_annotation(protein_list):
            functions = ['Kinase', 'Transcription_Factor', 'Receptor', 'Enzyme', 'Structural']
            annotations = {}
            
            for protein in protein_list:
                annotations[protein] = np.random.choice(functions)
            
            return annotations
        
        protein_functions = functional_annotation(proteins)
        
        # Functional enrichment in hubs
        hub_protein_names = [hub[0] for hub in hub_proteins]
        hub_functions = [protein_functions[protein] for protein in hub_protein_names]
        function_counts = {func: hub_functions.count(func) for func in set(hub_functions)}
        
        return {
            'total_proteins': len(proteins),
            'total_interactions': len(interactions),
            'network_density': nx.density(G),
            'connected_components': len(communities),
            'hub_proteins': len(hub_proteins),
            'average_path_length': avg_path_length,
            'clustering_coefficient': clustering_coefficient,
            'triangular_motifs': triangles,
            'functional_categories': len(set(protein_functions.values())),
            'most_central_protein': max(degree_centrality, key=degree_centrality.get)
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Bioinformatics and computational biology operations...")
    
    # DNA sequence analysis
    dna_result = dna_sequence_analysis()
    if 'error' not in dna_result:
        print(f"DNA Analysis: {dna_result['sequences_analyzed']} sequences, {dna_result['orfs_found']} ORFs, {dna_result['average_gc_content']:.1f}% GC content")
    
    # Protein analysis
    protein_result = protein_analysis()
    if 'error' not in protein_result:
        print(f"Protein Analysis: {protein_result['proteins_analyzed']} proteins, {protein_result['average_length']:.0f} avg length, {protein_result['domains_identified']} domains")
    
    # Phylogenetic analysis
    phylo_result = phylogenetic_analysis()
    if 'error' not in phylo_result:
        print(f"Phylogenetics: {phylo_result['species_analyzed']} species, {phylo_result['nucleotide_diversity']:.4f} diversity")
    
    # Gene expression analysis
    expression_result = gene_expression_analysis()
    if 'error' not in expression_result:
        print(f"Gene Expression: {expression_result['differentially_expressed_genes']} DE genes, {expression_result['enriched_pathways']} enriched pathways")
    
    # Protein-protein interactions
    ppi_result = protein_protein_interaction()
    if 'error' not in ppi_result:
        print(f"PPI Network: {ppi_result['total_proteins']} proteins, {ppi_result['total_interactions']} interactions, {ppi_result['connected_components']} components")