# vector_db.py
import os
import sys
import logging
import chromadb
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.topics import TOPICS, TOPIC_EXAMPLES
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

class VectorDBManager:
    """
    Manages operations with the vector database, including creating embeddings
    without using an external LLM API, storing logs, and querying the database.
    """
    
    def __init__(self, collection_name="intellios_logs", 
                 persist_directory=None, 
                 topics_collection_name="topics"):
        """
        Initialize the Vector DB Manager.
        
        Args:
            collection_name: Name of the collection in the vector database
            persist_directory: Directory to persist the vector database (defaults to env var or ./vector_db)
            topics_collection_name: Name of the collection for topics
        """
        logger.info(f"Initializing VectorDBManager with collection '{collection_name}'")
        
        # Get persist directory from environment variable or use default
        if persist_directory is None:
            persist_directory = os.getenv("VECTOR_DB_PATH", "./vector_db")
        
        # Create the persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize the embedding model
        logger.info("Loading sentence transformer model for embeddings")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, efficient model
        
        # Initialize ChromaDB
        logger.info(f"Initializing ChromaDB with persist directory: {persist_directory}")
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        
        # Get or create main logs collection
        self.collection = self._get_or_create_collection(collection_name)
        
        # Get or create topics collection
        self.topics_collection = self._get_or_create_collection(topics_collection_name)
        
        # Initialize topics if needed
        self._initialize_topics()
        
        # Cache topic embeddings for performance
        self._topic_embeddings = {}
        self._load_topic_embeddings()
    
    def _get_or_create_collection(self, collection_name):
        """Helper method to get or create a collection."""
        try:
            # First try to get the collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
            return collection
        except chromadb.errors.NotFoundError:
            # If it doesn't exist, create it
            logger.info(f"Collection not found, creating new collection: {collection_name}")
            return self.client.create_collection(name=collection_name)
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Error accessing ChromaDB collection: {e}")
            logger.info(f"Attempting to create new collection: {collection_name}")
            return self.client.create_collection(name=collection_name)
    
    def _initialize_topics(self):
        """Initialize the topics collection if it's empty."""
        if self.topics_collection.count() == 0:
            logger.info("Initializing topics collection with predefined topics")
            
            ids = []
            documents = []
            metadatas = []
            
            # Create entries for each topic
            for topic, description in TOPICS.items():
                topic_id = f"topic_{topic}"
                ids.append(topic_id)
                
                # Combine description with examples for better embedding
                examples_text = " ".join(TOPIC_EXAMPLES.get(topic, []))
                document = f"{description}. {examples_text}"
                documents.append(document)
                
                # Store metadata
                metadata = {
                    "topic": topic,
                    "description": description,
                }
                metadatas.append(metadata)
            
            # Add topics to collection
            self.topics_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} topics to the topics collection")
    
    def _load_topic_embeddings(self):
        """Load topic embeddings into memory for faster matching."""
        logger.info("Loading topic embeddings into memory")
        
        topic_data = self.topics_collection.get()
        
        if not topic_data["documents"]:
            logger.warning("No topics found in topics collection")
            return
        
        for i, topic_doc in enumerate(topic_data["documents"]):
            topic = topic_data["metadatas"][i]["topic"]
            embedding = self.create_embedding(topic_doc)
            self._topic_embeddings[topic] = embedding
        
        logger.info(f"Loaded embeddings for {len(self._topic_embeddings)} topics")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for a text string using Sentence Transformers.
        This doesn't require an external LLM API.
        
        Args:
            text: The text to create an embedding for
            
        Returns:
            A list of floats representing the embedding
        """
        logger.debug(f"Creating embedding for text: {text[:100]}...")
        embedding = self.model.encode(text)
        return embedding.tolist()  # Convert numpy array to list
    
    def add_logs_with_topic_matches(self, logs: List[Dict[str, Any]], n_matches: int = 3) -> List[Dict[str, Any]]:
        """
        Add logs to the vector database and return them enriched with topic matches.
        
        Args  :
            logs: List of parsed log dictionaries
            n_matches: Number of topic matches to include per log
            
        Returns:
            The logs enriched with topic matches
        """
        if not logs:
            logger.warning("No logs provided to add to vector database")
            return []
        
        logger.info(f"Adding {len(logs)} logs to vector database with topic matches")
        
        # Store the logs in the database
        try:
            enriched_logs = []
            
            for log in logs:
                # Create a text representation for embedding
                document = (
                    f"Event Type: {log.get('event_type', 'Unknown')}, "
                    f"Summary: {log.get('summary', 'No summary')}"
                )
                
                if log.get('app_name'):
                    document += f", App: {log['app_name']}"
                    
                if log.get('status'):
                    document += f", Status: {log['status']}"
                
                # Get topic matches
                log_embedding = self.create_embedding(document)
                topic_matches = self.match_with_topics(log_embedding, n_results=n_matches)
                
                # Add topic matches to the log
                enriched_log = log.copy()
                enriched_log['topic_matches'] = topic_matches
                enriched_logs.append(enriched_log)
            
            # Now actually add the logs to the database
            self.add_logs(logs)
            
            return enriched_logs
        except Exception as e:
            logger.error(f"Failed to add logs with topic matches: {e}")
            return logs  # Return the original logs without topic matches
    
    def add_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add logs to the vector database and match with topics.
        
        Args:
            logs: List of parsed log dictionaries
            
        Returns:
            The same logs with topic matches added
        """
        if not logs:
            logger.warning("No logs provided to add to vector database")
            return []
        
        logger.info(f"Adding {len(logs)} logs to vector database")
        
        ids = []
        documents = []
        metadatas = []
        enriched_logs = []
        
        for i, log in enumerate(logs):
            # Create a unique ID for each log
            log_id = f"log_{int(time.time())}_{i}"
            ids.append(log_id)
            
            # Create a text representation for embedding
            document = (
                f"Event Type: {log.get('event_type', 'Unknown')}, "
                f"Summary: {log.get('summary', 'No summary')}"
            )
            
            if log.get('app_name'):
                document += f", App: {log['app_name']}"
                
            if log.get('status'):
                document += f", Status: {log['status']}"
                
            documents.append(document)
            
            # Match log with topics
            topic_matches = self.match_log_with_topics(document)
            
            # Add topic matches to the log
            enriched_log = log.copy()
            enriched_log['topic_matches'] = topic_matches
            enriched_logs.append(enriched_log)
            
            # Prepare metadata - make sure it's serializable
            metadata = {}
            for key, value in enriched_log.items():
                # Convert all values to strings to ensure they can be serialized
                try:
                    if isinstance(value, (dict, list)):
                        metadata[key] = json.dumps(value)
                    else:
                        metadata[key] = str(value)
                except (TypeError, ValueError):
                    metadata[key] = str(value)
            
            metadatas.append(metadata)
        
        # Add logs to the collection
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(logs)} logs to vector database")
        except Exception as e:
            logger.error(f"Failed to add logs to vector database: {e}")
        
        return enriched_logs
    
    def match_with_topics(self, log_embedding: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Match a log embedding with predefined topics.
        
        Args:
            log_embedding: The embedding vector of the log
            n_results: Number of top topic matches to return
            
        Returns:
            List of topic matches with scores
        """
        # Calculate similarity with each topic
        similarities = []
        
        for topic, topic_embedding in self._topic_embeddings.items():
            # Calculate cosine similarity
            similarity = self._cosine_similarity(log_embedding, topic_embedding)
            similarities.append((topic, similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N matches
        topic_matches = []
        for topic, score in similarities[:n_results]:
            topic_matches.append({
                "topic": topic,
                "description": TOPICS.get(topic, ""),
                "score": round(score, 4)
            })
        
        return topic_matches
    
    def match_log_with_topics(self, log_text: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Match a log with predefined topics.
        
        Args:
            log_text: The text representation of the log
            top_n: Number of top topic matches to return
            
        Returns:
            List of topic matches with scores
        """
        # Create embedding for the log
        log_embedding = self.create_embedding(log_text)
        
        # Calculate similarity with each topic
        similarities = []
        
        for topic, topic_embedding in self._topic_embeddings.items():
            # Calculate cosine similarity
            similarity = self._cosine_similarity(log_embedding, topic_embedding)
            similarities.append((topic, similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N matches
        topic_matches = []
        for topic, score in similarities[:top_n]:
            topic_matches.append({
                "topic": topic,
                "description": TOPICS.get(topic, ""),
                "score": round(score, 4)
            })
        
        return topic_matches
    
    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)
    
    def query_logs(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector database for logs similar to the query text.
        
        Args:
            query_text: The text to search for
            n_results: Maximum number of results to return
            
        Returns:
            A list of log dictionaries matching the query
        """
        logger.info(f"Querying vector database with: '{query_text}'")
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Process and return results
            if results['metadatas'] and results['metadatas'][0]:
                logger.info(f"Found {len(results['metadatas'][0])} matching logs")
                
                # Convert serialized JSON back to Python objects
                processed_results = []
                for metadata in results['metadatas'][0]:
                    processed_metadata = {}
                    for key, value in metadata.items():
                        try:
                            # Try to parse JSON strings back to Python objects
                            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                                try:
                                    processed_metadata[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    processed_metadata[key] = value
                            else:
                                processed_metadata[key] = value
                        except Exception:
                            processed_metadata[key] = value
                    
                    processed_results.append(processed_metadata)
                
                return processed_results
            else:
                logger.info("No matching logs found")
                return []
        except Exception as e:
            logger.error(f"Failed to query vector database: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            A dictionary with statistics about the vector database
        """
        try:
            log_count = self.collection.count()
            topic_count = self.topics_collection.count()
            return {
                "collection_name": self.collection.name,
                "log_count": log_count,
                "topic_count": topic_count
            }
        except Exception as e:
            logger.error(f"Failed to get vector database stats: {e}")
            return {"error": str(e)}
            
    def clear_collection(self) -> bool:
        """
        Clear all documents from the logs collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Clearing collection '{self.collection.name}'")
            self.collection.delete()
            
            # Recreate the collection
            self.collection = self.client.create_collection(name=self.collection.name)
            logger.info(f"Collection '{self.collection.name}' cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
