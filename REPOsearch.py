import requests
import os
from datetime import datetime
import config
import time
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError

headers = {'Authorization': f'token {config.GITHUB_TOKEN}'}

def log_debug(messaggio):
    print(f"[DEBUG] {datetime.now()}: {messaggio}")

def esegui_richiesta_con_retry(url, headers, params, max_tentativi=10):
    for tentativo in range(max_tentativi):
        try:
            risposta = requests.get(url, headers=headers, params=params)
            risposta.raise_for_status()
            return risposta
        except (ConnectionError, NewConnectionError) as e:
            if tentativo < max_tentativi - 1:
                tempo_attesa = 60
                log_debug(f"Errore di connessione. Attendo {tempo_attesa} secondi prima del tentativo {tentativo + 2}")
                time.sleep(tempo_attesa)
            else:
                raise e

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

def cerca_repository_per_intervallo(query, intervallo):
    repository = []
    url = 'https://api.github.com/search/repositories'
    query_completa = f'{query} stars:{intervallo}'
    
    for pagina in range(1, 11):
        params = {'q': query_completa, 'page': pagina, 'per_page': 100, 'sort': 'stars', 'order': 'desc'}
        log_debug(f"Ricerca repository per '{query}' - Intervallo: {intervallo} - Pagina {pagina}")
        
        try:
            risposta = esegui_richiesta_con_retry(url, headers, params)
            controlla_limiti_api(risposta)
            dati = risposta.json()
            
            for repo in dati['items']:
                if repo['stargazers_count'] > 0:
                    repository.append((repo['full_name'], repo['stargazers_count']))
                    
            if len(dati['items']) < 100:
                break
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                controlla_limiti_api(e.response)
                continue
            log_debug(f"Errore nella ricerca: {e}")
            break
        except Exception as e:
            log_debug(f"Errore nella ricerca: {e}")
            break
            
    return repository

def salva_repository(cartella, nome_file, repository):
    os.makedirs(cartella, exist_ok=True)
    percorso_file = os.path.join(cartella, nome_file)
    
    with open(percorso_file, 'w') as file:
        for repo, stars in sorted(repository, key=lambda x: x[1], reverse=True):
            file.write(f"{repo},{stars}\n")
            
    log_debug(f"Salvato il file '{nome_file}' con {len(repository)} repository")

def main():
    intervalli_stelle = [
        *[f'{i}..{i}' for i in range(1, 11)],
        '11..25',
        '26..50',
        '51..100',
        '101..500',
        '>500'
    ]

    cartella_base = 'github_repositories'
    
    for query in config.QUERIES:
        query_safe = query.replace(' ', '_')
        tutti_repository = []
        
        for intervallo in intervalli_stelle:
            log_debug(f"Ricerca per '{query}' - Intervallo: {intervallo}")
            repository = cerca_repository_per_intervallo(query, intervallo)
            tutti_repository.extend(repository)
            
        nome_file = f'{query_safe}_repositories.txt'
        salva_repository(cartella_base, nome_file, tutti_repository)
        
        log_debug(f"Completata la ricerca per '{query}'")

if __name__ == '__main__':
    main()
