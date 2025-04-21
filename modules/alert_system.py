import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import json
import datetime

class AlertSystem:
    """
    Système d'alertes pour notifier en cas de détection d'imposteurs.
    Conforme aux exigences du cahier des charges pour le module d'alertes.
    """
    
    def __init__(self, config_file=None):
        """
        Initialise le système d'alertes.
        
        Args:
            config_file (str, optional): Chemin vers le fichier de configuration.
        """
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'votre_email@gmail.com',
            'sender_password': 'votre_mot_de_passe',
            'recipient_emails': ['destinataire@example.com']
        }
        
        # Charger la configuration depuis un fichier si spécifié
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.email_config.update(json.load(f))
    
    def send_email_alert(self, subject, message, image_path=None):
        """
        Envoie une alerte par email.
        
        Args:
            subject (str): Sujet de l'email
            message (str): Corps du message
            image_path (str, optional): Chemin vers l'image à joindre
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            # Ajouter le corps du message
            msg.attach(MIMEText(message, 'plain'))
            
            # Ajouter l'image en pièce jointe si spécifiée
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    msg.attach(image)
            
            # Connexion au serveur SMTP
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            # Envoyer l'email
            server.send_message(msg)
            server.quit()
            
            print(f"Alerte envoyée à {', '.join(self.email_config['recipient_emails'])}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'alerte par email: {e}")
            return False
    
    def send_impostor_alert(self, location, timestamp, confidence, image_path=None):
        """
        Envoie une alerte spécifique pour la détection d'un imposteur.
        
        Args:
            location (str): Emplacement de la détection
            timestamp (datetime): Horodatage de la détection
            confidence (float): Niveau de confiance de la détection
            image_path (str, optional): Chemin vers l'image de l'imposteur
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        subject = f"ALERTE SÉCURITÉ - Imposteur détecté à {location}"
        
        message = f"""
ALERTE DE SÉCURITÉ - ACCÈS NON AUTORISÉ DÉTECTÉ

Date et heure: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}
Emplacement: {location}
Niveau de confiance: {confidence:.2f}

Cette alerte a été générée automatiquement par le système de contrôle d'accès.
Veuillez vérifier l'accès et prendre les mesures appropriées.
"""
        
        return self.send_email_alert(subject, message, image_path)
    
    def log_alert(self, alert_type, details, timestamp=None):
        """
        Enregistre une alerte dans le journal des alertes.
        
        Args:
            alert_type (str): Type d'alerte (ex: 'impostor', 'system_error')
            details (dict): Détails de l'alerte
            timestamp (datetime, optional): Horodatage de l'alerte
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        log_entry = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'type': alert_type,
            'details': details
        }
        
        try:
            # Créer le répertoire des logs s'il n'existe pas
            os.makedirs('logs', exist_ok=True)
            
            # Nom du fichier de log basé sur la date
            log_file = os.path.join('logs', f"alerts_{timestamp.strftime('%Y-%m-%d')}.json")
            
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
            print(f"Erreur lors de l'enregistrement de l'alerte dans le journal: {e}")
            return False


# Exemple d'utilisation
if __name__ == "__main__":
    alert_system = AlertSystem()
    
    # Simuler une détection d'imposteur
    location = "Entrée principale"
    timestamp = datetime.datetime.now()
    confidence = 0.85
    
    # Enregistrer l'alerte dans le journal
    alert_system.log_alert('impostor', {
        'location': location,
        'confidence': confidence
    }, timestamp)
    
    # Envoyer une alerte par email (commenté pour éviter l'envoi réel)
    # alert_system.send_impostor_alert(location, timestamp, confidence)
