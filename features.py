"""
Module d'extraction de caractéristiques faciales avec OpenCV

Ce module fournit des fonctions pour extraire, comparer et stocker les caractéristiques
faciales en utilisant OpenCV comme solution alternative à face_recognition.
"""

import cv2
import numpy as np
import os
import pickle

def extract_features_opencv(image):
    """
    Extrait les caractéristiques faciales d'une image en utilisant OpenCV.
    
    Args:
        image: Image au format OpenCV (BGR)
        
    Returns:
        Un vecteur de caractéristiques ou None si aucun visage n'est détecté
    """
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Utiliser le détecteur de visage Haar Cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Si aucun visage n'est détecté, retourner None
    if len(faces) == 0:
        return None
    
    # Prendre le premier visage détecté (le plus grand)
    x, y, w, h = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)[0]
    
    # Extraire la région du visage
    face_roi = gray[y:y+h, x:x+w]
    
    # Redimensionner à une taille fixe
    face_roi = cv2.resize(face_roi, (100, 100))
    
    # Normaliser les valeurs des pixels
    face_roi = face_roi / 255.0
    
    # Aplatir l'image pour obtenir un vecteur de caractéristiques
    features = face_roi.flatten()
    
    return features

def compare_features(features1, features2, threshold=0.8):
    """
    Compare deux ensembles de caractéristiques faciales.
    
    Args:
        features1: Premier vecteur de caractéristiques
        features2: Deuxième vecteur de caractéristiques
        threshold: Seuil de similarité (0.0 à 1.0)
        
    Returns:
        True si les caractéristiques sont similaires, False sinon
    """
    if features1 is None or features2 is None:
        return False
    
    # Calculer la similarité cosinus
    dot_product = np.dot(features1, features2)
    norm1 = np.linalg.norm(features1)
    norm2 = np.linalg.norm(features2)
    
    similarity = dot_product / (norm1 * norm2)
    
    return similarity > threshold

def save_face_features(name, features):
    """
    Enregistre les caractéristiques d'un visage dans un fichier.
    
    Args:
        name: Nom de la personne
        features: Vecteur de caractéristiques
    """
    # Créer le répertoire des caractéristiques s'il n'existe pas
    features_dir = os.path.join('dataset', 'features')
    if not os.path.exists(features_dir):
        os.makedirs(features_dir)
    
    # Enregistrer les caractéristiques dans un fichier
    features_path = os.path.join(features_dir, f"{name}.pkl")
    with open(features_path, 'wb') as f:
        pickle.dump(features, f)
    
    print(f"Caractéristiques enregistrées pour {name}")

def load_face_features():
    """
    Charge les caractéristiques des visages connus.
    
    Returns:
        Un dictionnaire {nom: caractéristiques} des visages connus
    """
    features_dict = {}
    
    features_dir = os.path.join('dataset', 'features')
    if not os.path.exists(features_dir):
        os.makedirs(features_dir)
        return features_dict
    
    for file in os.listdir(features_dir):
        if file.endswith('.pkl'):
            name = os.path.splitext(file)[0]
            features_path = os.path.join(features_dir, file)
            
            try:
                with open(features_path, 'rb') as f:
                    features = pickle.load(f)
                features_dict[name] = features
            except Exception as e:
                print(f"Erreur lors du chargement des caractéristiques de {name}: {e}")
    
    return features_dict

def process_known_faces():
    """
    Traite les visages connus pour extraire leurs caractéristiques.
    """
    known_faces_dir = os.path.join('dataset', 'connu')
    
    if not os.path.exists(known_faces_dir):
        os.makedirs(known_faces_dir)
        return
    
    for file in os.listdir(known_faces_dir):
        if file.endswith(('.jpg', '.jpeg', '.png')):
            name = os.path.splitext(file)[0]
            image_path = os.path.join(known_faces_dir, file)
            
            try:
                # Charger l'image
                image = cv2.imread(image_path)
                
                # Extraire les caractéristiques
                features = extract_features_opencv(image)
                
                if features is not None:
                    # Enregistrer les caractéristiques
                    save_face_features(name, features)
                else:
                    print(f"Aucun visage détecté dans l'image de {name}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'image de {name}: {e}")

def identify_person(features, known_features_dict, threshold=0.8):
    """
    Identifie une personne à partir de ses caractéristiques faciales.
    
    Args:
        features: Vecteur de caractéristiques du visage à identifier
        known_features_dict: Dictionnaire des caractéristiques des visages connus
        threshold: Seuil de similarité (0.0 à 1.0)
        
    Returns:
        Le nom de la personne identifiée ou "Inconnu"
    """
    if features is None:
        return "Inconnu"
    
    best_match = None
    best_similarity = -1
    
    for name, known_features in known_features_dict.items():
        # Calculer la similarité cosinus
        dot_product = np.dot(features, known_features)
        norm1 = np.linalg.norm(features)
        norm2 = np.linalg.norm(known_features)
        
        similarity = dot_product / (norm1 * norm2)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name
    
    if best_similarity > threshold:
        return best_match
    else:
        return "Inconnu"

# Si ce script est exécuté directement, traiter les visages connus
if __name__ == "__main__":
    process_known_faces()
