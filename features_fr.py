"""
Module d'extraction de caractéristiques faciales avec face_recognition

Ce module fournit des fonctions pour extraire, comparer et stocker les caractéristiques
faciales en utilisant la bibliothèque face_recognition basée sur dlib.
"""

import cv2
import numpy as np
import os
import pickle
import face_recognition

def extract_features_face_recognition(image):
    """
    Extrait les caractéristiques faciales d'une image en utilisant face_recognition.
    
    Args:
        image: Image au format OpenCV (BGR)
        
    Returns:
        Un vecteur d'encodage facial ou None si aucun visage n'est détecté
    """
    try:
        # Vérifier si l'image est valide
        if image is None or image.size == 0:
            print("Image invalide ou vide")
            return None
            
        # S'assurer que l'image est au format 8-bit
        if image.dtype != np.uint8:
            print(f"Conversion du type d'image de {image.dtype} à uint8")
            image = np.uint8(image)
        
        # Convertir l'image BGR (OpenCV) en RGB (face_recognition)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Détecter les visages et extraire les encodages
        face_locations = face_recognition.face_locations(rgb_image)
        
        # Si aucun visage n'est détecté, retourner None
        if len(face_locations) == 0:
            print("Aucun visage détecté dans l'image")
            return None
        
        # Extraire les encodages du premier visage détecté
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) > 0:
            return face_encodings[0]
        else:
            print("Impossible d'extraire les encodages du visage")
            return None
    except Exception as e:
        print(f"Erreur lors de l'extraction des caractéristiques: {e}")
        return None

def compare_features_face_recognition(features1, features2, threshold=0.6):
    """
    Compare deux ensembles de caractéristiques faciales.
    
    Args:
        features1: Premier vecteur d'encodage facial
        features2: Deuxième vecteur d'encodage facial
        threshold: Seuil de similarité (0.0 à 1.0)
        
    Returns:
        True si les caractéristiques sont similaires, False sinon
    """
    if features1 is None or features2 is None:
        return False
    
    # Calculer la distance euclidienne entre les encodages
    distance = np.linalg.norm(features1 - features2)
    
    # Convertir la distance en similarité (plus la distance est petite, plus la similarité est grande)
    similarity = 1 - distance
    
    return similarity > threshold

def save_face_features_fr(name, features):
    """
    Enregistre les caractéristiques d'un visage dans un fichier.
    
    Args:
        name: Nom de la personne
        features: Vecteur d'encodage facial
    """
    # Créer le répertoire des caractéristiques s'il n'existe pas
    features_dir = os.path.join('dataset', 'features_fr')
    if not os.path.exists(features_dir):
        os.makedirs(features_dir)
    
    # Enregistrer les caractéristiques dans un fichier
    features_path = os.path.join(features_dir, f"{name}.pkl")
    with open(features_path, 'wb') as f:
        pickle.dump(features, f)
    
    print(f"Caractéristiques face_recognition enregistrées pour {name}")

def load_face_features_fr():
    """
    Charge les caractéristiques des visages connus.
    
    Returns:
        Un dictionnaire {nom: caractéristiques} des visages connus
    """
    features_dict = {}
    
    features_dir = os.path.join('dataset', 'features_fr')
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

def process_known_faces_fr():
    """
    Traite les visages connus pour extraire leurs caractéristiques avec face_recognition.
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
                features = extract_features_face_recognition(image)
                
                if features is not None:
                    # Enregistrer les caractéristiques
                    save_face_features_fr(name, features)
                else:
                    print(f"Aucun visage détecté dans l'image de {name}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'image de {name}: {e}")

def identify_person_fr(features, known_features_dict, threshold=0.6):
    """
    Identifie une personne à partir de ses caractéristiques faciales.
    
    Args:
        features: Vecteur d'encodage facial du visage à identifier
        known_features_dict: Dictionnaire des caractéristiques des visages connus
        threshold: Seuil de similarité (0.0 à 1.0)
        
    Returns:
        Le nom de la personne identifiée et le score de confiance, ou "Inconnu" et le score
    """
    if features is None or not known_features_dict:
        return "Inconnu", 0.0
    
    best_match = None
    best_similarity = -1
    
    for name, known_features in known_features_dict.items():
        # Calculer la distance euclidienne
        distance = np.linalg.norm(features - known_features)
        
        # Convertir la distance en similarité
        similarity = 1 - distance
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name
    
    if best_similarity > threshold:
        return best_match, best_similarity
    else:
        return "Inconnu", best_similarity

# Si ce script est exécuté directement, traiter les visages connus
if __name__ == "__main__":
    process_known_faces_fr()
