import numpy as np
from sklearn.metrics import precision_score, recall_score
import json
import os

class PerformanceEvaluator:
    def __init__(self):
        self.test_results = []
        self.metrics_file = 'performance/metrics.json'
        os.makedirs('performance', exist_ok=True)
    
    def add_test_result(self, true_label, predicted_label, confidence):
        self.test_results.append({
            'true': true_label,
            'predicted': predicted_label,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
    
    def calculate_metrics(self):
        y_true = [x['true'] for x in self.test_results]
        y_pred = [x['predicted'] for x in self.test_results]
        
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        
        # Taux de faux positifs
        fp_rate = sum(1 for x in self.test_results 
                     if x['true'] == 'Inconnu' and x['predicted'] != 'Inconnu') / len(self.test_results)
        
        metrics = {
            'precision': precision,
            'recall': recall,
            'false_positive_rate': fp_rate,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f)
        
        return metrics
    
    def generate_report(self):
        metrics = self.calculate_metrics()
        report = f"""
Rapport de Performance - {datetime.now().date()}
----------------------------------------
Précision: {metrics['precision']:.2%}
Rappel: {metrics['recall']:.2%}
Taux de Faux Positifs: {metrics['false_positive_rate']:.2%}

Détail des Tests:
"""
        for res in self.test_results[-10:]:  # Derniers 10 résultats
            report += f"{res['timestamp']} - True: {res['true']}, Pred: {res['predicted']} (conf: {res['confidence']:.2f})\n"
        
        return report