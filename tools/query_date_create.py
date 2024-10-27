from datetime import datetime, timedelta

# Funzione per generare le query
def generate_queries(start_date, end_date):
    queries = []
    current_date = start_date

    while current_date >= end_date:
        # Calcola la data di inizio della settimana (7 giorni di intervallo)
        week_end = current_date
        week_start = current_date - timedelta(days=6)
        
        # Invertiamo week_start e week_end per avere l'ordine corretto
        queries.append(f"'app android pushed:{week_start.strftime('%Y-%m-%d')}..{week_end.strftime('%Y-%m-%d')}',")
        
        # Aggiorna la data corrente alla fine della settimana precedente
        current_date = week_start - timedelta(days=1)

    return queries

# Data di oggi
today = datetime.now()
# Data di inizio (1 gennaio 2018)
start_date = datetime(2018, 1, 1)

# Genera le query
queries = generate_queries(today, start_date)

# Stampa le query
for query in queries:
    print(query)

