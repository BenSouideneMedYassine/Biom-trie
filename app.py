import cv2
import numpy as np
import os
from flask import Flask, render_template, Response, request, redirect, url_for
import time
import threading
import base64
import face_recognition
from features import extract_features_opencv, load_face_features, save_face_features, identify_person, process_known_faces
from features_fr import extract_features_face_recognition, load_face_features_fr, save_face_features_fr, identify_person_fr, process_known_faces_fr
from flask import session  # Ajoutez ceci avec les autres imports Flask
# Initialisation de l'application Flask
app = Flask(__name__)
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
from functools import wraps
import cv2
import numpy as np
import os
import time
import threading
import base64
import face_recognition
import json
from werkzeug.security import generate_password_hash, check_password_hash
from features import extract_features_opencv, load_face_features, save_face_features, identify_person, process_known_faces
from features_fr import extract_features_face_recognition, load_face_features_fr, save_face_features_fr, identify_person_fr, process_known_faces_fr
# from flask_wtf.csrf import CSRFProtect

app.secret_key = 'votre_cle_secrete_tres_secrete'
# csrf = CSRFProtect(app)  # Active la protection CSRF globale

# Décorateur pour les routes nécessitant une authentification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# Ajoutez cette section après les autres imports
# Chemin du fichier JSON pour stocker les utilisateurs
USERS_FILE = 'users.json'

# Fonctions pour gérer les utilisateurs
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def add_user(username, password):
    users = load_users()
    if username in users:
        return False  # L'utilisateur existe déjà
    users[username] = {
        'password': generate_password_hash(password),
        'role': 'user'  # Vous pouvez ajouter des rôles si nécessaire
    }
    save_users(users)
    return True

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False
    return check_password_hash(users[username]['password'], password)

# Ajoutez quelques utilisateurs par défaut au premier lancement
if not os.path.exists(USERS_FILE):
    default_users = {
        'admin': {
            'password': generate_password_hash('admin'),
            'role': 'admin'
        },
        'user': {
            'password': generate_password_hash('user'),
            'role': 'user'
        }
    }
    save_users(default_users)

# Modifiez la route /login pour utiliser le système JSON
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
        
#         if verify_user(username, password):
#             session['logged_in'] = True
#             session['username'] = username
#             flash('Connexion réussie!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Identifiants incorrects. Veuillez réessayer.', 'danger')
    
#     return render_template('login.html')
# Ajoutez cette fonction
def count_recent_failed_attempts(ip_address, minutes=5):
    alerts = load_alerts()
    now = time.time()
    count = 0
    
    for alert in reversed(alerts):
        alert_time = time.mktime(time.strptime(alert['timestamp'], "%Y-%m-%d %H:%M:%S"))
        if (now - alert_time) < (minutes * 60) and alert['ip_address'] == ip_address:
            count += 1
        else:
            break
    
    return count

# Modifiez la route login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip_address = request.remote_addr
        max_attempts = 5
        
        # Vérifier le nombre de tentatives récentes
        if count_recent_failed_attempts(ip_address) >= max_attempts:
            flash('Trop de tentatives de connexion. Veuillez réessayer plus tard.', 'danger')
            return redirect(url_for('login'))
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        else:
            save_alert(username, ip_address)
            remaining_attempts = max_attempts - count_recent_failed_attempts(ip_address) - 1
            flash(f'Identifiants incorrects. Il vous reste {remaining_attempts} tentatives.', 'danger')
    
    return render_template('login.html')
def purge_old_alerts(days=30):
    alerts = load_alerts()
    now = time.time()
    cutoff = now - (days * 24 * 60 * 60)
    
    filtered_alerts = []
    for alert in alerts:
        alert_time = time.mktime(time.strptime(alert['timestamp'], "%Y-%m-%d %H:%M:%S"))
        if alert_time > cutoff:
            filtered_alerts.append(alert)
    
    with open(ALERTS_FILE, 'w') as f:
        json.dump(filtered_alerts, f, indent=4)




@app.context_processor
def inject_alerts_count():
    if session.get('username') == 'admin':
        return dict(load_alerts=load_alerts)
    return dict(load_alerts=lambda: [])
# Modifiez votre fonction load_alerts pour marquer les nouvelles alertes
def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            try:
                alerts = json.load(f)
                # Marquer les alertes non vues (par exemple celles des dernières 24h)
                now = time.time()
                for alert in alerts:
                    alert_time = time.mktime(time.strptime(alert['timestamp'], "%Y-%m-%d %H:%M:%S"))
                    alert['is_new'] = (now - alert_time) < (24 * 60 * 60)
                return alerts
            except json.JSONDecodeError:
                return []
    return []
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def get_alerts_count():
    # Le cache expire après 60 secondes
    time.sleep(0.1)  # Simule un chargement lent
    return len(load_alerts())

# Puis dans le context processor
@app.context_processor
def inject_alerts_count():
    if session.get('username') == 'admin':
        return dict(get_alerts_count=get_alerts_count)
    return dict(get_alerts_count=lambda: 0)

@app.route('/delete_alert', methods=['POST'])
@login_required
def delete_alert():
    if session.get('username') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        alert_index = int(request.json.get('alert_index'))
        alerts = load_alerts()
        
        if 0 <= alert_index < len(alerts):
            alerts.pop(alert_index)
            with open(ALERTS_FILE, 'w') as f:
                json.dump(alerts, f, indent=4)
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Invalid index'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_all_alerts', methods=['POST'])
@login_required
def delete_all_alerts():
    if session.get('username') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump([], f)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# Appeler cette fonction périodiquement ou au démarrage

# Ajoutez cette constante avec les autres au début du fichier
ALERTS_FILE = 'alerts.json'

# Fonction pour charger les alertes
def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Fonction pour sauvegarder une nouvelle alerte
def save_alert(username, ip_address):
    alerts = load_alerts()
    new_alert = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'username': username,
        'ip_address': ip_address,
        'type': 'failed_login'
    }
    alerts.append(new_alert)
    
    # Garder seulement les 100 dernières alertes pour éviter un fichier trop gros
    alerts = alerts[-100:]
    
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=4)
from datetime import datetime


@app.route('/alerts')
@login_required
def view_alerts():
    alerts = load_alerts()
    alerts.reverse()  # Inversion en place
    return render_template('alerts.html',
                         alerts=alerts,
                         now=datetime.now())

# Ajoutez une route pour l'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
        elif add_user(username, password):
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        else:
            flash("Ce nom d'utilisateur est déjà pris.", 'danger')
    
    return render_template('register.html')

# Modifiez la route /logout pour effacer plus d'informations de session
@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))
# Variables globales
camera = None
camera_active = False
frame_global = None
detection_active = False
recognition_active = False
current_result = "Aucune détection"
known_faces = {}
known_face_encodings = []
known_face_names = []
known_features_dict = {}
known_features_fr_dict = {}
use_face_recognition = False  

# Fonction pour charger les visages connus depuis le dataset
def load_known_faces():
    global known_face_encodings, known_face_names, known_faces, known_features_dict, known_features_fr_dict
    
    # Créer les répertoires nécessaires s'ils n'existent pas
    os.makedirs(os.path.join('dataset', 'connu'), exist_ok=True)
    os.makedirs(os.path.join('dataset', 'features'), exist_ok=True)
    os.makedirs(os.path.join('dataset', 'features_fr'), exist_ok=True)
    
    if use_face_recognition:
        # Traiter les visages connus pour extraire leurs caractéristiques avec face_recognition
        process_known_faces_fr()
        
        # Charger les caractéristiques des visages connus
        known_features_fr_dict = load_face_features_fr()
        
        # Mettre à jour la liste des noms des personnes connues
        known_face_names = list(known_features_fr_dict.keys())
        
        print(f"Visages connus chargés avec face_recognition: {known_face_names}")
    else:
        # Charger les caractéristiques des visages connus avec OpenCV
        known_features_dict = load_face_features()
        
        # Traiter les visages connus pour extraire leurs caractéristiques
        process_known_faces()
        
        # Recharger les caractéristiques après le traitement
        known_features_dict = load_face_features()
        
        # Mettre à jour la liste des noms des personnes connues
        known_face_names = list(known_features_dict.keys())
        
        print(f"Visages connus chargés avec OpenCV: {known_face_names}")
    
    return known_face_names

# Fonction pour initialiser la caméra
def init_camera():
    global camera
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("Erreur: Impossible d'ouvrir la caméra")
            return False
        return True
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la caméra: {e}")
        return False

# Fonction pour libérer la caméra
def release_camera():
    global camera, camera_active
    if camera is not None:
        camera.release()
        camera = None
    camera_active = False

# Fonction pour capturer les images de la caméra
def capture_frames():
    global camera, frame_global, camera_active
    
    while camera_active:
        if camera is None:
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            print("Erreur: Impossible de lire la frame de la caméra")
            time.sleep(0.1)
            continue
            
        # Retourner l'image horizontalement pour un effet miroir
        frame = cv2.flip(frame, 1)
        
        # Si la détection est active, nous traiterons l'image ici
        if detection_active:
            # Détection de visage avec OpenCV (en attendant face_recognition)
            frame = detect_faces_opencv(frame)
        
        frame_global = frame
        
        # Petite pause pour réduire l'utilisation CPU
        time.sleep(0.03)

# Fonction pour détecter les visages et reconnaître les personnes
def detect_faces_opencv(frame):
    global current_result, known_features_dict, known_features_fr_dict
    
    try:
        # Vérifier si l'image est valide
        if frame is None or frame.size == 0:
            current_result = "Image de caméra invalide"
            return frame
            
        # S'assurer que l'image est au format 8-bit
        if frame.dtype != np.uint8:
            frame = np.uint8(frame)
        
        if use_face_recognition:
            try:
                # Utiliser face_recognition pour la détection et la reconnaissance
                # Convertir l'image BGR (OpenCV) en RGB (face_recognition)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Détecter les visages
                face_locations = face_recognition.face_locations(rgb_frame)
                
                # Dessiner un rectangle autour de chaque visage
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    if recognition_active:
                        try:
                            # Extraire les caractéristiques du visage détecté
                            face_encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
                            
                            if len(face_encodings) > 0 and known_features_fr_dict:
                                # Identifier la personne
                                person_name, confidence = identify_person_fr(face_encodings[0], known_features_fr_dict)
                                
                                # Afficher le nom de la personne et la confiance
                                label = f"{person_name} ({confidence:.2f})"
                                cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                
                                if person_name != "Inconnu":
                                    current_result = f"Personne identifiée: {person_name} (confiance: {confidence:.2f})"
                                else:
                                    current_result = "Personne inconnue détectée"
                            else:
                                cv2.putText(frame, "Inconnu", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                current_result = "Personne inconnue détectée"
                        except Exception as e:
                            print(f"Erreur lors de la reconnaissance: {e}")
                            cv2.putText(frame, "Erreur reconnaissance", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            current_result = f"Erreur de reconnaissance: {str(e)[:30]}"
                    else:
                        current_result = f"{len(face_locations)} visage(s) détecté(s)"
                
                if len(face_locations) == 0:
                    current_result = "Aucun visage détecté"
            except Exception as e:
                print(f"Erreur avec face_recognition: {e}")
                # Fallback à OpenCV en cas d'erreur
                use_opencv_fallback = True
                current_result = f"Erreur face_recognition: {str(e)[:30]}"
                # Continuer avec la méthode OpenCV ci-dessous
        else:
            use_opencv_fallback = True
        
        # Utiliser OpenCV si spécifié ou en cas d'erreur avec face_recognition
        if not use_face_recognition or 'use_opencv_fallback' in locals():
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Utiliser le détecteur de visage Haar Cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Dessiner un rectangle autour de chaque visage
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                if recognition_active:
                    try:
                        # Extraire les caractéristiques du visage détecté
                        face_img = frame[y:y+h, x:x+w]
                        features = extract_features_opencv(face_img)
                        
                        if features is not None and known_features_dict:
                            # Identifier la personne
                            person_name = identify_person(features, known_features_dict)
                            
                            # Afficher le nom de la personne
                            cv2.putText(frame, person_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            if person_name != "Inconnu":
                                current_result = f"Personne identifiée: {person_name}"
                            else:
                                current_result = "Personne inconnue détectée"
                        else:
                            cv2.putText(frame, "Inconnu", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            current_result = "Personne inconnue détectée"
                    except Exception as e:
                        print(f"Erreur lors de la reconnaissance OpenCV: {e}")
                        cv2.putText(frame, "Erreur", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        current_result = f"Erreur: {str(e)[:30]}"
                else:
                    current_result = f"{len(faces)} visage(s) détecté(s)"
            
            if len(faces) == 0:
                current_result = "Aucun visage détecté"
    
    except Exception as e:
        print(f"Erreur générale dans detect_faces_opencv: {e}")
        current_result = f"Erreur: {str(e)[:30]}"
    
    # Afficher le résultat sur l'image
    cv2.putText(frame, current_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame

# Fonction pour générer le flux vidéo
def generate_frames():
    global frame_global
    
    while True:
        if frame_global is None:
            # Si aucune frame n'est disponible, envoyer une image noire
            blank_image = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(blank_image, "Caméra inactive", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', blank_image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
            continue
            
        # Encoder la frame en JPEG
        _, buffer = cv2.imencode('.jpg', frame_global)
        frame = buffer.tobytes()
        
        # Envoyer la frame au navigateur
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Routes Flask
@app.route('/')
@login_required
def index():
    return render_template('index.html', detection_active=detection_active, 
                          recognition_active=recognition_active,
                          camera_active=camera_active,
                          result=current_result,
                          known_faces=known_face_names)

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_camera', methods=['POST'])
@login_required
def toggle_camera():
    global camera_active, camera
    
    if camera_active:
        camera_active = False
        release_camera()
    else:
        if init_camera():
            camera_active = True
            # Démarrer le thread de capture
            threading.Thread(target=capture_frames, daemon=True).start()
    
    return redirect(url_for('index'))

@app.route('/toggle_detection', methods=['POST'])
@login_required
def toggle_detection():
    global detection_active
    detection_active = not detection_active
    return redirect(url_for('index'))

@app.route('/toggle_recognition', methods=['POST'])
@login_required
def toggle_recognition():
    global recognition_active
    recognition_active = not recognition_active
    
    # Charger les visages connus si la reconnaissance est activée
    if recognition_active:
        load_known_faces()
    
    return redirect(url_for('index'))

@app.route('/add_face', methods=['POST'])
@login_required
def add_face():
    global frame_global, known_features_dict, known_features_fr_dict
    
    if frame_global is None:
        return redirect(url_for('index'))
    
    name = request.form.get('name', 'Inconnu')
    if not name:
        name = 'Inconnu'
    
    try:
        # Vérifier si l'image est valide
        if frame_global is None or frame_global.size == 0:
            print("Image invalide pour l'ajout de visage")
            return redirect(url_for('index'))
            
        # S'assurer que l'image est au format 8-bit
        if frame_global.dtype != np.uint8:
            frame_global = np.uint8(frame_global)
        
        # Sauvegarder l'image actuelle dans le dataset
        face_path = os.path.join('dataset', 'connu', f"{name}.jpg")
        cv2.imwrite(face_path, frame_global)
        print(f"Image sauvegardée pour {name} à {face_path}")
        
        if use_face_recognition:
            try:
                # Extraire les caractéristiques du visage avec face_recognition
                features_fr = extract_features_face_recognition(frame_global)
                
                # Sauvegarder les caractéristiques si un visage est détecté
                if features_fr is not None:
                    save_face_features_fr(name, features_fr)
                    print(f"Caractéristiques face_recognition sauvegardées pour {name}")
                else:
                    print(f"Aucun visage détecté pour {name} avec face_recognition")
            except Exception as e:
                print(f"Erreur lors de l'extraction des caractéristiques face_recognition: {e}")
                # Fallback à OpenCV
                try:
                    # Extraire les caractéristiques du visage avec OpenCV
                    features = extract_features_opencv(frame_global)
                    
                    # Sauvegarder les caractéristiques si un visage est détecté
                    if features is not None:
                        save_face_features(name, features)
                        print(f"Caractéristiques OpenCV sauvegardées pour {name} (fallback)")
                    else:
                        print(f"Aucun visage détecté pour {name} avec OpenCV (fallback)")
                except Exception as e2:
                    print(f"Erreur lors de l'extraction des caractéristiques OpenCV: {e2}")
        else:
            # Extraire les caractéristiques du visage avec OpenCV
            features = extract_features_opencv(frame_global)
            
            # Sauvegarder les caractéristiques si un visage est détecté
            if features is not None:
                save_face_features(name, features)
                print(f"Caractéristiques OpenCV sauvegardées pour {name}")
            else:
                print(f"Aucun visage détecté pour {name} avec OpenCV")
        
        # Recharger les visages connus
        load_known_faces()
        
    except Exception as e:
        print(f"Erreur générale lors de l'ajout du visage: {e}")
    
    return redirect(url_for('index'))

# Point d'entrée principal
if __name__ == '__main__':
    # Créer les répertoires nécessaires s'ils n'existent pas
    os.makedirs(os.path.join('dataset', 'connu'), exist_ok=True)
    os.makedirs(os.path.join('dataset', 'inconnu'), exist_ok=True)
    os.makedirs(os.path.join('dataset', 'features'), exist_ok=True)
    os.makedirs(os.path.join('dataset', 'features_fr'), exist_ok=True)
    
    # Charger les visages connus au démarrage
    load_known_faces()
    
    print("Serveur de biométrie faciale démarré sur http://localhost:5000") 
    print("Utilisez Ctrl+C pour arrêter le serveur")
    
    # Démarrer l'application Flask
    app.run(host='0.0.0.0', port=5000, debug=True)