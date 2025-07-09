#!/usr/bin/env python3
"""
Simple background job to add vectors to nodes that don't have them.
Connects directly to FalkorDB and uses OpenAI API for embeddings.
"""

import os
import time
import logging
from typing import List, Dict, Any
import redis
import openai
from falkordb import FalkorDB

# Configuration
FALKORDB_HOST = os.getenv('FALKORDB_HOST', 'localhost')
FALKORDB_PORT = int(os.getenv('FALKORDB_PORT', '6379'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL', '300'))  # 5 minutes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVectorJob:
    def __init__(self):
        self.db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
    def find_nodes_needing_vectors(self, graph_name: str) -> List[Dict]:
        """Find nodes that have text but no embedding"""
        graph = self.db.select_graph(graph_name)
        
        result = graph.query(f"""
            MATCH (n) 
            WHERE n.text IS NOT NULL 
              AND n.embedding IS NULL
            RETURN n.id as id, n.text as text, labels(n)[0] as label
            LIMIT {BATCH_SIZE}
        """)
        
        return [{"id": row[0], "text": row[1], "label": row[2]} 
                for row in result.result_set]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def update_nodes_with_embeddings(self, graph_name: str, nodes: List[Dict], embeddings: List[List[float]]):
        """Update nodes with their embeddings"""
        graph = self.db.select_graph(graph_name)
        
        for node, embedding in zip(nodes, embeddings):
            try:
                # Convert embedding to string format for Cypher
                embedding_str = str(embedding).replace('[', '').replace(']', '')
                
                graph.query(f"""
                    MATCH (n) WHERE n.id = {node['id']}
                    SET n.embedding = vecf32([{embedding_str}])
                """)
                
                logger.info(f"Updated node {node['id']} with embedding")
                
            except Exception as e:
                logger.error(f"Failed to update node {node['id']}: {e}")
    
    def process_graph(self, graph_name: str):
        """Process one batch of nodes for a graph"""
        logger.info(f"Processing graph: {graph_name}")
        
        # Find nodes needing vectors
        nodes = self.find_nodes_needing_vectors(graph_name)
        if not nodes:
            logger.info(f"No nodes need vectors in graph {graph_name}")
            return 0
        
        logger.info(f"Found {len(nodes)} nodes needing vectors")
        
        # Generate embeddings
        texts = [node['text'] for node in nodes]
        embeddings = self.generate_embeddings(texts)
        
        # Update database
        self.update_nodes_with_embeddings(graph_name, nodes, embeddings)
        
        return len(nodes)
    
    def get_all_graphs(self) -> List[str]:
        """Get list of all graphs in the database"""
        try:
            return self.db.list()
        except Exception as e:
            logger.error(f"Failed to list graphs: {e}")
            return []
    
    def run_once(self):
        """Run one iteration of the job"""
        logger.info("Starting vector backfill job")
        
        graphs = self.get_all_graphs()
        total_processed = 0
        
        for graph_name in graphs:
            try:
                processed = self.process_graph(graph_name)
                total_processed += processed
            except Exception as e:
                logger.error(f"Error processing graph {graph_name}: {e}")
                continue
        
        logger.info(f"Completed job iteration. Processed {total_processed} nodes total")
        return total_processed
    
    def run_forever(self):
        """Run the job continuously"""
        logger.info(f"Starting continuous vector backfill job (interval: {SLEEP_INTERVAL}s)")
        
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Job iteration failed: {e}")
            
            logger.info(f"Sleeping for {SLEEP_INTERVAL} seconds")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable required")
        exit(1)
    
    job = SimpleVectorJob()
    
    # Run once or continuously based on argument
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        job.run_once()
    else:
        job.run_forever()