import os
import re
import shutil

def analizza_cartelle():
    # Definizione delle cartelle
    cartella_txt = 'github_repositories'
    cartella_csv = 'apk_results'
    cartella_destinazione = 'file_da_processare'
    
    # Crea la cartella di destinazione se non esiste
    if not os.path.exists(cartella_destinazione):
        os.makedirs(cartella_destinazione)
    
    # Pattern per estrarre le date dal nome del file
    pattern = re.compile(r'2018-\d{2}-\d{2}\.\.2018-\d{2}-\d{2}')
    
    # Debug iniziale
    print("\n=== Analisi iniziale ===")
    print(f"Cartella CSV: {cartella_csv}")
    print(f"Cartella TXT: {cartella_txt}")
    
    # Conta e analizza i file CSV
    date_csv = set()
    total_csv = 0
    csv_senza_data = 0
    
    for file in os.listdir(cartella_csv):
        if file.endswith('.csv'):
            total_csv += 1
            match = pattern.search(file)
            if match:
                date_csv.add(match.group())
            else:
                csv_senza_data += 1
    
    print(f"\n=== Analisi file CSV ===")
    print(f"Totale file CSV trovati: {total_csv}")
    print(f"File CSV con data valida: {len(date_csv)}")
    print(f"File CSV senza data nel nome: {csv_senza_data}")
    
    # Esempio dei primi 5 file CSV per debug
    print("\nEsempio primi 5 file CSV:")
    for file in list(os.listdir(cartella_csv))[:5]:
        print(f"- {file}")
    
    # Analizza i file TXT
    total_txt = 0
    txt_senza_data = 0
    files_copiati = 0
    
    print(f"\n=== Analisi file TXT ===")
    for file in os.listdir(cartella_txt):
        if file.endswith('.txt'):
            total_txt += 1
            match = pattern.search(file)
            if match:
                data = match.group()
                if data not in date_csv:
                    percorso_origine = os.path.join(cartella_txt, file)
                    percorso_destinazione = os.path.join(cartella_destinazione, file)
                    shutil.copy2(percorso_origine, percorso_destinazione)
                    files_copiati += 1
            else:
                txt_senza_data += 1
    
    # Esempio dei primi 5 file TXT per debug
    print("\nEsempio primi 5 file TXT:")
    for file in list(os.listdir(cartella_txt))[:5]:
        print(f"- {file}")
    
    # Report finale dettagliato
    print(f"\n=== Report Finale ===")
    print(f"File CSV totali: {total_csv}")
    print(f"File CSV con data valida: {len(date_csv)}")
    print(f"File CSV senza data: {csv_senza_data}")
    print(f"File TXT totali: {total_txt}")
    print(f"File TXT senza data: {txt_senza_data}")
    print(f"File TXT copiati: {files_copiati}")
    
    if files_copiati > 0:
        print(f"\nI nuovi file da processare sono stati salvati in: {cartella_destinazione}")
        print(f"Date uniche nei CSV: {sorted(list(date_csv))[:5]}... (prime 5)")

if __name__ == "__main__":
    analizza_cartelle()
