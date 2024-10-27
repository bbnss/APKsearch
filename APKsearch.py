import requests
from csv import DictWriter
import os
from datetime import datetime
import config
from collections import defaultdict
import time
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError

headers = {'Authorization': f'token {config.GITHUB_TOKEN}'}
OUTPUT_FOLDER = 'apk_results'
MAX_TENTATIVI = 10  # Aumentato per gestire meglio le interruzioni di connessione

def log_debug(messaggio):
    print(f"[DEBUG] {datetime.now()}: {messaggio}")

def controlla_limiti_api(risposta):
    rimanenti = int(risposta.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(risposta.headers.get('X-RateLimit-Reset', 0))
    
    log_debug(f"Richieste API rimanenti: {rimanenti}")
    
    if rimanenti < 10:
        tempo_attuale = time.time()
        tempo_attesa = reset_time - tempo_attuale
        
        if tempo_attesa > 0:
            log_debug(f"Limite di richieste quasi raggiunto. Pausa di {int(tempo_attesa/60)} minuti")
            time.sleep(tempo_attesa + 60)

def richiesta_con_retry(url, params=None):
    for tentativo in range(MAX_TENTATIVI):
        try:
            risposta = requests.get(url, headers=headers, params=params)
            risposta.raise_for_status()
            controlla_limiti_api(risposta)
            return risposta.json()
        except (ConnectionError, NewConnectionError) as e:
            tempo_attesa = 60
            if tentativo < MAX_TENTATIVI - 1:
                log_debug(f"Errore di connessione. Attendo {tempo_attesa} secondi prima del tentativo {tentativo + 2}")
                time.sleep(tempo_attesa)
            else:
                raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                controlla_limiti_api(e.response)
                continue
            log_debug(f"Errore HTTP nella richiesta (tentativo {tentativo + 1}): {e}")
            if tentativo < MAX_TENTATIVI - 1:
                time.sleep(60)
            else:
                raise
        except Exception as e:
            log_debug(f"Errore generico nella richiesta (tentativo {tentativo + 1}): {e}")
            if tentativo < MAX_TENTATIVI - 1:
                time.sleep(60)
            else:
                raise

def ottieni_info_repository(repo_name):
    url_repo = f'https://api.github.com/repos/{repo_name}'
    try:
        repo_info = richiesta_con_retry(url_repo)
        return repo_info.get('description', '')
    except Exception as e:
        log_debug(f"Errore nel recupero delle informazioni del repository {repo_name}: {e}")
        return ''

def trova_link_apk(repo_name, stars, description):
    url_release = f'https://api.github.com/repos/{repo_name}/releases'
    log_debug(f"Controllo release per {repo_name}")
    
    apk_per_repo = defaultdict(list)
    
    try:
        release = richiesta_con_retry(url_release)
        for rel in release:
            for asset in rel.get('assets', []):
                if asset['name'].endswith('.apk'):
                    apk_info = {
                        'repository': f'https://github.com/{repo_name}',
                        'link_apk': asset['browser_download_url'],
                        'repo_name': repo_name,
                        'stars': stars,
                        'description': description,
                        'published_at': rel['published_at'][:10]
                    }
                    apk_per_repo[repo_name].append(apk_info)
        
        apk_per_repo[repo_name].sort(key=lambda x: x['published_at'], reverse=True)
        return apk_per_repo[repo_name][:3]
        
    except Exception as e:
        log_debug(f"Errore nel controllo delle release per {repo_name}: {e}")
        return []

def scrivi_su_csv(dati, nome_file):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    percorso_file = os.path.join(OUTPUT_FOLDER, nome_file)
    
    file_exists = os.path.isfile(percorso_file)
    with open(percorso_file, 'a', newline='', encoding='utf-8') as file:
        writer = DictWriter(file, fieldnames=['repository', 'link_apk', 'repo_name', 'stars', 'description', 'published_at'])
        if not file_exists:
            writer.writeheader()
        writer.writerows(dati)
    log_debug(f"Scritti {len(dati)} risultati su {nome_file}")

def processa_repository(repo_line):
    repo_name, stars = repo_line.strip().split(',')
    description = ottieni_info_repository(repo_name)
    return trova_link_apk(repo_name, int(stars), description)

def main():
    cartella_input = 'github_repositories'
    
    if not os.path.exists(cartella_input):
        log_debug(f"Cartella {cartella_input} non trovata")
        return

    for file_name in os.listdir(cartella_input):
        if file_name.endswith('.txt'):
            query = file_name.replace('_repositories.txt', '')
            file_path = os.path.join(cartella_input, file_name)
            log_debug(f'Elaborazione del file {file_name}')
            
            tutti_link_apk = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    risultati = processa_repository(line)
                    tutti_link_apk.extend(risultati)
            
            if tutti_link_apk:
                file_csv = f'{query}_apk_results.csv'
                scrivi_su_csv(tutti_link_apk, file_csv)
            else:
                log_debug(f'Nessun APK trovato per {file_name}')

    print("Ricerca completata. I risultati sono stati salvati nella cartella", OUTPUT_FOLDER)

if __name__ == '__main__':
    main()
