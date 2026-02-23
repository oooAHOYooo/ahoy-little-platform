"""
Search Indexer - In-memory search index for Ahoy Indie Media
Builds and maintains a searchable index of all content (music, shows, artists)
"""

import json
import re
import math
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
import unicodedata


class SearchIndexer:
    """In-memory search index with TF-IDF scoring and fuzzy matching"""
    
    def __init__(self):
        self.documents = {}  # doc_id -> document data
        self.term_to_docs = defaultdict(set)  # term -> set of doc_ids
        self.doc_terms = defaultdict(set)  # doc_id -> set of terms
        self.term_frequencies = defaultdict(Counter)  # doc_id -> term -> count
        self.total_docs = 0
        self.field_weights = {
            'title': 3.0,
            'name': 3.0,
            'tags': 2.0,
            'genres': 2.0,
            'description': 1.0,
            'summary': 1.0,
            'artist': 2.0,
            'host': 2.0,
            'album': 1.5,
            'category': 1.5
        }
        
    def normalize_text(self, text: str) -> str:
        """Normalize text: lowercase, strip diacritics, collapse whitespace"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove diacritics
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Collapse whitespace and remove special chars except spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms"""
        normalized = self.normalize_text(text)
        return [term for term in normalized.split() if len(term) > 1]
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def fuzzy_match(self, query_terms: List[str], doc_terms: Set[str], max_distance: int = 1) -> Set[str]:
        """Find fuzzy matches for query terms in document terms"""
        matches = set()
        for query_term in query_terms:
            for doc_term in doc_terms:
                if query_term == doc_term:
                    matches.add(doc_term)
                elif len(query_term) > 2 and len(doc_term) > 2:
                    distance = self.levenshtein_distance(query_term, doc_term)
                    if distance <= max_distance:
                        matches.add(doc_term)
        return matches
    
    def extract_text_fields(self, doc: Dict[str, Any], doc_type: str) -> Dict[str, str]:
        """Extract searchable text fields from a document"""
        fields = {}
        
        if doc_type == 'music':
            fields.update({
                'title': doc.get('title', ''),
                'artist': doc.get('artist', ''),
                'album': doc.get('album', ''),
                'tags': ' '.join(doc.get('tags', [])),
                'genres': doc.get('genre', ''),
                'description': doc.get('description', '')
            })
        elif doc_type == 'show':
            fields.update({
                'title': doc.get('title', ''),
                'host': doc.get('host', ''),
                'description': doc.get('description', ''),
                'tags': ' '.join(doc.get('tags', [])),
                'category': doc.get('category', ''),
                'summary': doc.get('summary', '')
            })
        elif doc_type == 'artist':
            fields.update({
                'name': doc.get('name', ''),
                'description': doc.get('description', ''),
                'genres': ' '.join(doc.get('genres', [])),
                'tags': ' '.join(doc.get('tags', [])),
                'summary': doc.get('summary', '')
            })
        
        return fields
    
    def build_document(self, doc: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Build a searchable document from raw data"""
        fields = self.extract_text_fields(doc, doc_type)
        
        # Tokenize all text fields
        all_terms = set()
        for field, text in fields.items():
            terms = self.tokenize(text)
            all_terms.update(terms)
        
        # Build document
        search_doc = {
            'id': doc.get('id', ''),
            'kind': doc_type,
            'title': doc.get('title', doc.get('name', '')),
            'url': self._build_url(doc, doc_type),
            'summary': self._build_summary(doc, doc_type),
            'tags': doc.get('tags', []),
            'genres': doc.get('genres', []),
            'duration': doc.get('duration_seconds', 0),
            'added_date': doc.get('added_date', doc.get('published_date', '')),
            'fields': fields,
            'terms': all_terms,
            # Add image fields for different content types
            'cover_art': doc.get('cover_art', '') if doc_type == 'music' else '',
            'thumbnail': doc.get('thumbnail', '') if doc_type == 'show' else '',
            'image': doc.get('image', '') if doc_type == 'artist' else '',
            'artist': doc.get('artist', '') if doc_type == 'music' else '',
            'host': doc.get('host', '') if doc_type == 'show' else '',
            'name': doc.get('name', '') if doc_type == 'artist' else ''
        }
        
        return search_doc
    
    def _build_url(self, doc: Dict[str, Any], doc_type: str) -> str:
        """Build URL for a document"""
        if doc_type == 'music':
            return f"/music#{doc.get('id', '')}"
        elif doc_type == 'show':
            return f"/shows#{doc.get('id', '')}"
        elif doc_type == 'artist':
            return f"/artists#{doc.get('id', '')}"
        return "#"
    
    def _build_summary(self, doc: Dict[str, Any], doc_type: str) -> str:
        """Build a summary for a document"""
        if doc_type == 'music':
            return f"{doc.get('artist', '')} - {doc.get('album', '')}"
        elif doc_type == 'show':
            return doc.get('description', '')[:120] + '...' if len(doc.get('description', '')) > 120 else doc.get('description', '')
        elif doc_type == 'artist':
            return doc.get('description', '')[:120] + '...' if len(doc.get('description', '')) > 120 else doc.get('description', '')
        return ""
    
    def add_document(self, doc: Dict[str, Any], doc_type: str):
        """Add a document to the index"""
        search_doc = self.build_document(doc, doc_type)
        doc_id = search_doc['id']
        
        if not doc_id:
            return
        
        self.documents[doc_id] = search_doc
        self.total_docs += 1
        
        # Index terms
        for field, text in search_doc['fields'].items():
            terms = self.tokenize(text)
            weight = self.field_weights.get(field, 1.0)
            
            for term in terms:
                self.term_to_docs[term].add(doc_id)
                self.doc_terms[doc_id].add(term)
                self.term_frequencies[doc_id][term] += weight
    
    def compute_tf_idf(self, term: str, doc_id: str) -> float:
        """Compute TF-IDF score for a term in a document"""
        if doc_id not in self.term_frequencies or term not in self.term_frequencies[doc_id]:
            return 0.0
        
        # Term frequency
        tf = self.term_frequencies[doc_id][term]
        
        # Document frequency
        df = len(self.term_to_docs[term])
        
        # IDF
        idf = math.log(self.total_docs / df) if df > 0 else 0
        
        return tf * idf
    
    def search(self, query: str, limit: int = 20, offset: int = 0, 
               kinds: List[str] = None, sort: str = 'relevance') -> Dict[str, Any]:
        """Search the index"""
        if not query.strip():
            return {
                'results': [],
                'total': 0,
                'query': query,
                'limit': limit,
                'offset': offset
            }
        
        # Parse query
        query_terms = self.tokenize(query)
        if not query_terms:
            return {
                'results': [],
                'total': 0,
                'query': query,
                'limit': limit,
                'offset': offset
            }
        
        # Find matching documents
        matching_docs = set()
        for term in query_terms:
            # Exact matches
            if term in self.term_to_docs:
                matching_docs.update(self.term_to_docs[term])
            
            # Fuzzy matches
            for doc_id, doc_terms in self.doc_terms.items():
                fuzzy_matches = self.fuzzy_match([term], doc_terms)
                if fuzzy_matches:
                    matching_docs.add(doc_id)
        
        # Score documents
        scored_docs = []
        for doc_id in matching_docs:
            if doc_id not in self.documents:
                continue
            
            doc = self.documents[doc_id]
            
            # Filter by kind
            if kinds and doc['kind'] not in kinds:
                continue
            
            # Calculate score
            score = 0.0
            for term in query_terms:
                # TF-IDF score
                tf_idf = self.compute_tf_idf(term, doc_id)
                score += tf_idf
                
                # Prefix boost
                for doc_term in self.doc_terms[doc_id]:
                    if doc_term.startswith(term):
                        score += 0.5
            
            # Add to results
            scored_docs.append((doc_id, score, doc))
        
        # Sort results
        if sort == 'relevance':
            scored_docs.sort(key=lambda x: x[1], reverse=True)
        elif sort == 'recent':
            scored_docs.sort(key=lambda x: x[2].get('added_date', ''), reverse=True)
        
        # Apply pagination
        total = len(scored_docs)
        paginated_docs = scored_docs[offset:offset + limit]
        
        # Build results
        results = []
        for doc_id, score, doc in paginated_docs:
            result = {
                'id': doc['id'],
                'kind': doc['kind'],
                'title': doc['title'],
                'url': doc['url'],
                'summary': doc['summary'],
                'tags': doc['tags'],
                'genres': doc['genres'],
                'score': round(score, 3),
                'snippet': self._build_snippet(doc, query_terms)
            }
            
            # Add type-specific fields
            if doc['kind'] == 'music':
                result['artist'] = doc['fields'].get('artist', '')
                result['album'] = doc['fields'].get('album', '')
                result['duration'] = doc.get('duration', 0)
                result['cover_art'] = doc.get('cover_art', '')
            elif doc['kind'] == 'show':
                result['host'] = doc['fields'].get('host', '')
                result['duration'] = doc.get('duration', 0)
                result['thumbnail'] = doc.get('thumbnail', '')
            elif doc['kind'] == 'artist':
                result['name'] = doc['fields'].get('name', '')
                result['image'] = doc.get('image', '')
            
            results.append(result)
        
        return {
            'results': results,
            'total': total,
            'query': query,
            'limit': limit,
            'offset': offset
        }
    
    def _build_snippet(self, doc: Dict[str, Any], query_terms: List[str]) -> str:
        """Build a snippet highlighting matched terms"""
        # Find the best field to extract snippet from
        best_field = None
        best_score = 0
        
        for field, text in doc['fields'].items():
            if not text:
                continue
            
            score = 0
            for term in query_terms:
                if term in text.lower():
                    score += 1
            
            if score > best_score:
                best_score = score
                best_field = text
        
        if not best_field:
            return doc.get('summary', '')[:120] + '...' if len(doc.get('summary', '')) > 120 else doc.get('summary', '')
        
        # Extract snippet around matched terms
        text = best_field.lower()
        snippet_start = 0
        snippet_end = len(text)
        
        for term in query_terms:
            pos = text.find(term)
            if pos != -1:
                snippet_start = max(0, pos - 60)
                snippet_end = min(len(text), pos + len(term) + 60)
                break
        
        snippet = best_field[snippet_start:snippet_end]
        if snippet_start > 0:
            snippet = '...' + snippet
        if snippet_end < len(best_field):
            snippet = snippet + '...'
        
        return snippet
    
    def clear(self):
        """Clear the entire index"""
        self.documents.clear()
        self.term_to_docs.clear()
        self.doc_terms.clear()
        self.term_frequencies.clear()
        self.total_docs = 0

    def reindex(self, data_sources: Dict[str, str]):
        """Rebuild the entire index from JSON data sources (Legacy)"""
        self.clear()
        
        # Load and index data
        for source_name, file_path in data_sources.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if source_name == 'music' and 'tracks' in data:
                    for track in data['tracks']:
                        self.add_document(track, 'music')
                elif source_name == 'shows' and 'shows' in data:
                    for show in data['shows']:
                        self.add_document(show, 'show')
                elif source_name == 'artists' and 'artists' in data:
                    for artist in data['artists']:
                        self.add_document(artist, 'artist')
                        
            except Exception as e:
                print(f"Error loading {source_name}: {e}")
        
        print(f"Indexed {self.total_docs} documents from JSON")

    def reindex_from_data(self, music_tracks=None, shows=None, artists=None):
        """Rebuild the entire index from provided data objects (DB-backed)"""
        self.clear()
        
        if music_tracks:
            for track in music_tracks:
                self.add_document(track, 'music')
        
        if shows:
            for show in shows:
                self.add_document(show, 'show')
        
        if artists:
            for artist in artists:
                self.add_document(artist, 'artist')
        
        print(f"Indexed {self.total_docs} documents from data objects")


# Global search index instance
search_index = SearchIndexer()
