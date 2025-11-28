"""
Feature Extraction Engine for ML-based Threat Detection
Extracts behavioral features from network traffic data
"""
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import numpy as np
from collections import defaultdict
import json


class FeatureExtractor:
    def __init__(self, es_host='localhost', es_port=9200):
        """Initialize feature extractor with Elasticsearch connection"""
        self.es = Elasticsearch([{'host': es_host, 'port': es_port}])
        
    def extract_device_features(self, mac, hours=1):
        """
        Extract behavioral features for a device over time window
        
        Args:
            mac: Device MAC address
            hours: Time window in hours (default: 1)
            
        Returns:
            dict: Feature vector for the device
        """
        # Time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Query parameters
        time_range = {
            "range": {
                "@timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat()
                }
            }
        }
        
        # Extract features from different indices
        dns_features = self._extract_dns_features(mac, time_range)
        ip_features = self._extract_ip_features(mac, time_range)
        
        # Combine all features
        features = {
            **dns_features,
            **ip_features,
            'timestamp': end_time.isoformat(),
            'time_window_hours': hours
        }
        
        return features
    
    def _extract_dns_features(self, mac, time_range):
        """Extract DNS-related features"""
        try:
            # Query DNS logs
            result = self.es.search(
                index="ip_dns",
                body={
                    "size": 1000,
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"mac.keyword": mac}},
                                time_range
                            ]
                        }
                    },
                    "aggs": {
                        "unique_domains": {
                            "cardinality": {"field": "dns.keyword"}
                        },
                        "threat_tags": {
                            "terms": {"field": "tags.keyword", "size": 10}
                        }
                    }
                }
            )
            
            hits = result['hits']['hits']
            aggs = result.get('aggregations', {})
            
            # Calculate features
            dns_query_count = len(hits)
            unique_domains = aggs.get('unique_domains', {}).get('value', 0)
            
            # Check for threats
            threat_count = 0
            threat_tags = []
            for hit in hits:
                tags = hit['_source'].get('tags', [])
                if tags:
                    threat_count += 1
                    threat_tags.extend(tags)
            
            # Domain entropy (measure of randomness - DGAs create high entropy)
            domain_entropy = self._calculate_domain_entropy([
                hit['_source'].get('dns', '') for hit in hits
            ])
            
            return {
                'dns_query_count': dns_query_count,
                'unique_domains': unique_domains,
                'dns_diversity': unique_domains / max(dns_query_count, 1),
                'threat_count': threat_count,
                'threat_ratio': threat_count / max(dns_query_count, 1),
                'domain_entropy': domain_entropy,
                'has_gsb_hits': 'GSB' in threat_tags
            }
            
        except Exception as e:
            print(f"Error extracting DNS features: {e}")
            return {
                'dns_query_count': 0,
                'unique_domains': 0,
                'dns_diversity': 0,
                'threat_count': 0,
                'threat_ratio': 0,
                'domain_entropy': 0,
                'has_gsb_hits': False
            }
    
    def _extract_ip_features(self, mac, time_range):
        """Extract IP connection features"""
        try:
            # Query IP logs
            result = self.es.search(
                index="mac_ip",
                body={
                    "size": 1000,
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"mac.keyword": mac}},
                                time_range
                            ]
                        }
                    },
                    "aggs": {
                        "unique_ips": {
                            "cardinality": {"field": "ip.keyword"}
                        }
                    }
                }
            )
            
            hits = result['hits']['hits']
            aggs = result.get('aggregations', {})
            
            connection_count = len(hits)
            unique_ips = aggs.get('unique_ips', {}).get('value', 0)
            
            # IP diversity
            ip_diversity = unique_ips / max(connection_count, 1)
            
            # Check for external IPs (basic heuristic)
            external_connections = 0
            for hit in hits:
                ip = hit['_source'].get('ip', '')
                if not ip.startswith('192.168.'):  # Not local network
                    external_connections += 1
            
            external_ratio = external_connections / max(connection_count, 1)
            
            return {
                'connection_count': connection_count,
                'unique_ips': unique_ips,
                'ip_diversity': ip_diversity,
                'external_connections': external_connections,
                'external_ratio': external_ratio
            }
            
        except Exception as e:
            print(f"Error extracting IP features: {e}")
            return {
                'connection_count': 0,
                'unique_ips': 0,
                'ip_diversity': 0,
                'external_connections': 0,
                'external_ratio': 0
            }
    
    def _calculate_domain_entropy(self, domains):
        """Calculate entropy of domain names (DGA detection)"""
        if not domains:
            return 0.0
        
        # Combine all domains into character frequency
        all_chars = ''.join(domains)
        if not all_chars:
            return 0.0
        
        # Calculate character frequency
        freq = defaultdict(int)
        for char in all_chars.lower():
            if char.isalnum():
                freq[char] += 1
        
        # Calculate entropy
        total = sum(freq.values())
        entropy = 0.0
        for count in freq.values():
            p = count / total
            entropy -= p * np.log2(p)
        
        return entropy
    
    def build_baseline(self, mac, days=7):
        """
        Build behavioral baseline for a device over multiple days
        
        Args:
            mac: Device MAC address
            days: Number of days to analyze
            
        Returns:
            dict: Baseline statistics (mean, std, min, max for each feature)
        """
        baseline_features = []
        
        # Collect features for each day
        for day in range(days):
            end_time = datetime.now() - timedelta(days=day)
            start_time = end_time - timedelta(hours=24)
            
            # Get features for this day
            features = self.extract_device_features(mac, hours=24)
            
            # Convert to numeric array (exclude non-numeric fields)
            numeric_features = {
                k: v for k, v in features.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)
            }
            
            if numeric_features:
                baseline_features.append(numeric_features)
        
        if not baseline_features:
            return None
        
        # Calculate statistics
        baseline = {}
        feature_names = baseline_features[0].keys()
        
        for feature_name in feature_names:
            values = [f[feature_name] for f in baseline_features]
            baseline[feature_name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values))
            }
        
        baseline['created_at'] = datetime.now().isoformat()
        baseline['days_analyzed'] = days
        
        return baseline
    
    def get_feature_vector(self, features):
        """
        Convert feature dict to numpy array for ML model
        
        Args:
            features: Dictionary of features
            
        Returns:
            numpy array of feature values
        """
        # Ordered list of features for consistent vector
        feature_order = [
            'dns_query_count',
            'unique_domains',
            'dns_diversity',
            'threat_count',
            'threat_ratio',
            'domain_entropy',
            'connection_count',
            'unique_ips',
            'ip_diversity',
            'external_connections',
            'external_ratio'
        ]
        
        # Extract values in order
        vector = []
        for feature_name in feature_order:
            value = features.get(feature_name, 0)
            # Convert boolean to int
            if isinstance(value, bool):
                value = int(value)
            vector.append(float(value))
        
        return np.array(vector)


if __name__ == "__main__":
    # Test feature extraction
    extractor = FeatureExtractor()
    
    # Example: Extract features for a test MAC
    test_mac = "aa:bb:cc:dd:ee:ff"
    
    print("Extracting features...")
    features = extractor.extract_device_features(test_mac, hours=1)
    print(json.dumps(features, indent=2))
    
    print("\nBuilding baseline...")
    baseline = extractor.build_baseline(test_mac, days=7)
    if baseline:
        print(json.dumps(baseline, indent=2))
    else:
        print("Not enough data for baseline")
