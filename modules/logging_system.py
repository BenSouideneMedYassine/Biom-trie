import os
import json
import datetime
import csv
from collections import defaultdict

class LoggingSystem:
    """
    Système de journalisation avancé pour enregistrer toutes les activités du système de contrôle d'accès.
    Conforme aux exigences du cahier des charges pour la gestion des logs.
    """
    
    def __init__(self, log_dir='logs'):
        """
        Initialise le système de journalisation.
        
        Args:
            log_dir (str): Répertoire où stocker les fichiers de logs
        """
        self.log_dir = log_dir
        
        # Créer les répertoires de logs s'ils n'existent pas
        os.makedirs(os.path.join(log_dir, 'access'), exist_ok=True)
        os.makedirs(os.path.join(log_dir, 'alerts'), exist_ok=True)
        os.makedirs(os.path.join(log_dir, 'system'), exist_ok=True)
        os.makedirs(os.path.join(log_dir, 'reports'), exist_ok=True)
    
    def log_access(self, person_id, person_name, access_granted, confidence, location='Main Entrance', timestamp=None):
        """
        Enregistre une tentative d'accès dans le journal.
        
        Args:
            person_id (str): Identifiant de la personne
            person_name (str): Nom de la personne
            access_granted (bool): Si l'accès a été accordé ou non
            confidence (float): Niveau de confiance de la reconnaissance
            location (str): Emplacement de la tentative d'accès
            timestamp (datetime, optional): Horodatage de la tentative
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        log_entry = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'person_id': person_id,
            'person_name': person_name,
            'access_granted': access_granted,
            'confidence': confidence,
            'location': location
        }
        
        try:
            # Nom du fichier de log basé sur la date
            log_file = os.path.join(self.log_dir, 'access', f"access_{timestamp.strftime('%Y-%m-%d')}.json")
            
            # Charger les logs existants ou créer une nouvelle liste
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Ajouter la nouvelle entrée
            logs.append(log_entry)
            
            # Enregistrer les logs mis à jour
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            # Également enregistrer au format CSV pour faciliter l'analyse
            csv_file = os.path.join(self.log_dir, 'access', f"access_{timestamp.strftime('%Y-%m-%d')}.csv")
            csv_exists = os.path.exists(csv_file)
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if not csv_exists:
                    writer.writeheader()
                writer.writerow(log_entry)
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de l'accès dans le journal: {e}")
            return False
    
    def log_system_event(self, event_type, details, timestamp=None):
        """
        Enregistre un événement système dans le journal.
        
        Args:
            event_type (str): Type d'événement (ex: 'startup', 'shutdown', 'error')
            details (dict): Détails de l'événement
            timestamp (datetime, optional): Horodatage de l'événement
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        log_entry = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'details': details
        }
        
        try:
            # Nom du fichier de log basé sur la date
            log_file = os.path.join(self.log_dir, 'system', f"system_{timestamp.strftime('%Y-%m-%d')}.json")
            
            # Charger les logs existants ou créer une nouvelle liste
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Ajouter la nouvelle entrée
            logs.append(log_entry)
            
            # Enregistrer les logs mis à jour
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de l'événement système dans le journal: {e}")
            return False
    
    def generate_daily_report(self, date=None):
        """
        Génère un rapport quotidien des accès.
        
        Args:
            date (datetime.date, optional): Date pour laquelle générer le rapport
            
        Returns:
            dict: Rapport généré
        """
        if date is None:
            date = datetime.datetime.now().date()
        
        date_str = date.strftime('%Y-%m-%d')
        access_log_file = os.path.join(self.log_dir, 'access', f"access_{date_str}.json")
        
        if not os.path.exists(access_log_file):
            print(f"Aucun log d'accès trouvé pour la date {date_str}")
            return None
        
        try:
            with open(access_log_file, 'r') as f:
                access_logs = json.load(f)
            
            # Statistiques à calculer
            total_access_attempts = len(access_logs)
            granted_access = sum(1 for log in access_logs if log['access_granted'])
            denied_access = total_access_attempts - granted_access
            
            # Accès par personne
            access_by_person = defaultdict(int)
            for log in access_logs:
                access_by_person[log['person_name']] += 1
            
            # Accès par heure
            access_by_hour = defaultdict(int)
            for log in access_logs:
                hour = datetime.datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S').hour
                access_by_hour[hour] += 1
            
            # Accès par emplacement
            access_by_location = defaultdict(int)
            for log in access_logs:
                access_by_location[log['location']] += 1
            
            # Créer le rapport
            report = {
                'date': date_str,
                'total_access_attempts': total_access_attempts,
                'granted_access': granted_access,
                'denied_access': denied_access,
                'access_rate': granted_access / total_access_attempts if total_access_attempts > 0 else 0,
                'access_by_person': dict(access_by_person),
                'access_by_hour': dict(access_by_hour),
                'access_by_location': dict(access_by_location)
            }
            
            # Enregistrer le rapport
            report_file = os.path.join(self.log_dir, 'reports', f"daily_report_{date_str}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            return report
            
        except Exception as e:
            print(f"Erreur lors de la génération du rapport quotidien: {e}")
            return None
    
    def get_access_history(self, person_id=None, person_name=None, start_date=None, end_date=None):
        """
        Récupère l'historique des accès pour une personne ou une période donnée.
        
        Args:
            person_id (str, optional): Identifiant de la personne
            person_name (str, optional): Nom de la personne
            start_date (datetime.date, optional): Date de début de la période
            end_date (datetime.date, optional): Date de fin de la période
            
        Returns:
            list: Liste des entrées de journal correspondant aux critères
        """
        if start_date is None:
            start_date = datetime.datetime.now().date() - datetime.timedelta(days=7)
        
        if end_date is None:
            end_date = datetime.datetime.now().date()
        
        # Générer la liste des dates dans la période
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += datetime.timedelta(days=1)
        
        # Récupérer les logs pour chaque date
        access_history = []
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            access_log_file = os.path.join(self.log_dir, 'access', f"access_{date_str}.json")
            
            if os.path.exists(access_log_file):
                try:
                    with open(access_log_file, 'r') as f:
                        logs = json.load(f)
                    
                    # Filtrer les logs selon les critères
                    for log in logs:
                        if person_id and log['person_id'] != person_id:
                            continue
                        if person_name and log['person_name'] != person_name:
                            continue
                        
                        access_history.append(log)
                        
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier de log {access_log_file}: {e}")
        
        return access_history


# Exemple d'utilisation
if __name__ == "__main__":
    logging_system = LoggingSystem()
    
    # Simuler quelques accès
    logging_system.log_access("001", "John Doe", True, 0.95)
    logging_system.log_access("002", "Jane Smith", True, 0.87)
    logging_system.log_access("003", "Unknown Person", False, 0.45)
    
    # Enregistrer un événement système
    logging_system.log_system_event("startup", {"version": "1.0.0", "config": "default"})
    
    # Générer un rapport quotidien
    report = logging_system.generate_daily_report()
    if report:
        print(f"Rapport généré avec succès: {report['total_access_attempts']} tentatives d'accès")
    
    # Récupérer l'historique d'accès pour une personne
    history = logging_system.get_access_history(person_name="John Doe")
    print(f"Historique d'accès pour John Doe: {len(history)} entrées")
