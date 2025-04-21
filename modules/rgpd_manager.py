import os
import json
import hashlib
from datetime import datetime, timedelta

class RGPDManager:
    def __init__(self, data_dir='dataset'):
        self.data_dir = data_dir
        self.consent_file = os.path.join(data_dir, 'consents.json')
        self.retention_days = 30  # Durée de conservation
        
    def add_consent(self, name, email, consent_text):
        consents = self.load_consents()
        consents[name] = {
            'email': email,
            'date': datetime.now().isoformat(),
            'consent_text': consent_text,
            'data_hash': hashlib.md5(name.encode()).hexdigest()
        }
        self.save_consents(consents)
    
    def delete_data(self, name):
        # Supprimer toutes les données d'une personne
        files_to_delete = [
            f'dataset/connu/{name}.jpg',
            f'dataset/features/{name}.pkl',
            f'dataset/features_fr/{name}.pkl'
        ]
        
        for file in files_to_delete:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
                
        # Mettre à jour les consentements
        consents = self.load_consents()
        consents.pop(name, None)
        self.save_consents(consents)
    
    def cleanup_expired_data(self):
        # Nettoyage automatique des données expirées
        limit_date = datetime.now() - timedelta(days=self.retention_days)
        
        for name, data in self.load_consents().items():
            if datetime.fromisoformat(data['date']) < limit_date:
                self.delete_data(name)
    
    def load_consents(self):
        if os.path.exists(self.consent_file):
            with open(self.consent_file) as f:
                return json.load(f)
        return {}
    
    def save_consents(self, consents):
        with open(self.consent_file, 'w') as f:
            json.dump(consents, f, indent=2)