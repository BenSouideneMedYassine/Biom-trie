import cv2
import numpy as np
import os
import time
import argparse

# Importer les modules de reconnaissance faciale
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("Utilisation de face_recognition pour une meilleure précision")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("face_recognition n'est pas disponible, utilisation d'OpenCV uniquement")

# Fonction pour détecter les visages avec OpenCV
def detect_faces_opencv(frame):
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Utiliser le détecteur de visage Haar Cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    return faces

# Fonction pour détecter les visages avec face_recognition
def detect_faces_face_recognition(frame):
    # Convertir l'image BGR (OpenCV) en RGB (face_recognition)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Détecter les visages
    face_locations = face_recognition.face_locations(rgb_frame)
    
    # Convertir les coordonnées au format OpenCV (x, y, w, h)
    faces = []
    for (top, right, bottom, left) in face_locations:
        faces.append((left, top, right-left, bottom-top))
    
    return faces, face_locations

# Fonction pour extraire les caractéristiques faciales avec face_recognition
def extract_features_face_recognition(frame, face_location):
    # Convertir l'image BGR (OpenCV) en RGB (face_recognition)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Extraire les encodages du visage
    face_encodings = face_recognition.face_encodings(rgb_frame, [face_location])
    
    if len(face_encodings) > 0:
        return face_encodings[0]
    else:
        return None

# Fonction pour comparer un visage avec le dataset
def compare_with_dataset(encoding, dataset_dir, threshold=0.6):
    best_match = "Inconnu"
    best_score = 1.0  # Plus petite distance = meilleure correspondance
    
    # Parcourir tous les fichiers d'encodage dans le dataset
    for filename in os.listdir(dataset_dir):
        if filename.endswith('.npy'):
            # Charger l'encodage
            known_encoding = np.load(os.path.join(dataset_dir, filename))
            
            # Calculer la distance
            distance = np.linalg.norm(encoding - known_encoding)
            
            # Si la distance est inférieure au seuil et meilleure que la précédente
            if distance < threshold and distance < best_score:
                best_score = distance
                best_match = os.path.splitext(filename)[0]
    
    return best_match, 1.0 - best_score  # Convertir la distance en score de confiance

# Fonction principale
def main():
    parser = argparse.ArgumentParser(description='Système de biométrie faciale')
    parser.add_argument('--dataset', type=str, default='dataset', help='Chemin vers le dataset')
    parser.add_argument('--mode', type=str, default='test', choices=['test', 'add'], help='Mode de fonctionnement')
    parser.add_argument('--name', type=str, help='Nom de la personne à ajouter au dataset')
    args = parser.parse_args()
    
    # Créer les répertoires nécessaires
    os.makedirs(os.path.join(args.dataset, 'connu'), exist_ok=True)
    os.makedirs(os.path.join(args.dataset, 'encodings'), exist_ok=True)
    
    # Initialiser la caméra
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return
    
    print("Appuyez sur 'q' pour quitter")
    if args.mode == 'add' and args.name:
        print(f"Mode: Ajout de {args.name} au dataset")
        print("Appuyez sur 'c' pour capturer une image")
    else:
        print("Mode: Test de reconnaissance faciale")
    
    while True:
        # Capturer une frame
        ret, frame = cap.read()
        
        if not ret:
            print("Erreur: Impossible de lire la frame")
            break
        
        # Retourner l'image horizontalement pour un effet miroir
        frame = cv2.flip(frame, 1)
        
        # Détecter les visages
        if FACE_RECOGNITION_AVAILABLE:
            faces, face_locations = detect_faces_face_recognition(frame)
        else:
            faces = detect_faces_opencv(frame)
            face_locations = None
        
        # Dessiner un rectangle autour de chaque visage
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # En mode test, essayer de reconnaître la personne
            if args.mode == 'test' and FACE_RECOGNITION_AVAILABLE:
                # Extraire les caractéristiques du visage
                encoding = extract_features_face_recognition(frame, face_locations[i])
                
                if encoding is not None:
                    # Comparer avec le dataset
                    name, confidence = compare_with_dataset(encoding, os.path.join(args.dataset, 'encodings'))
                    
                    # Afficher le nom et la confiance
                    label = f"{name} ({confidence:.2f})"
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Afficher l'image
        cv2.imshow('Biométrie Faciale', frame)
        
        # Attendre une touche
        key = cv2.waitKey(1) & 0xFF
        
        # Quitter si 'q' est pressé
        if key == ord('q'):
            break
        
        # Capturer une image si 'c' est pressé en mode ajout
        if args.mode == 'add' and args.name and key == ord('c'):
            if len(faces) == 1:
                # Sauvegarder l'image
                img_path = os.path.join(args.dataset, 'connu', f"{args.name}.jpg")
                cv2.imwrite(img_path, frame)
                print(f"Image sauvegardée: {img_path}")
                
                if FACE_RECOGNITION_AVAILABLE:
                    # Extraire et sauvegarder l'encodage
                    encoding = extract_features_face_recognition(frame, face_locations[0])
                    if encoding is not None:
                        np.save(os.path.join(args.dataset, 'encodings', f"{args.name}.npy"), encoding)
                        print(f"Encodage sauvegardé pour {args.name}")
                    else:
                        print("Erreur: Impossible d'extraire l'encodage")
            else:
                print(f"Erreur: {len(faces)} visages détectés. Un seul visage doit être présent.")
    
    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
