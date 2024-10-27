import pandas as pd
import glob
import os
from datetime import datetime

def unisci_csv():
    # Imposta la directory di lavoro e inizia il logging
    start_time = datetime.now()
    directory = os.getcwd()
    print(f"\n=== Inizio elaborazione: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    # Trova tutti i file CSV nella directory
    files = glob.glob('*.csv')
    total_files = len(files)
    
    if not files:
        print("Errore: Nessun file CSV trovato nella directory")
        return
    
    print(f"Trovati {total_files} file CSV da elaborare")
    
    # Lista per contenere tutti i DataFrame
    dataframes = []
    files_elaborati = 0
    righe_totali = 0
    
    # Leggi ogni file CSV
    for file in files:
        try:
            df = pd.read_csv(file)
            righe_file = len(df)
            righe_totali += righe_file
            dataframes.append(df)
            files_elaborati += 1
            print(f"[{files_elaborati}/{total_files}] Elaborato: {file} - Righe: {righe_file:,}")
            
        except Exception as e:
            print(f"ERRORE nella lettura del file {file}: {str(e)}")
    
    if not dataframes:
        print("Errore: Nessun dato valido trovato nei file CSV")
        return
    
    print(f"\nStatistiche preliminari:")
    print(f"- File elaborati con successo: {files_elaborati} su {total_files}")
    print(f"- Totale righe lette: {righe_totali:,}")
    
    # Unisci tutti i DataFrame
    print("\nUnione dei dataframe in corso...")
    df_combinato = pd.concat(dataframes, ignore_index=True)
    print(f"Dimensione dataframe combinato: {len(df_combinato):,} righe")
    
    # Converti la colonna published_at in formato datetime
    try:
        print("\nConversione date in corso...")
        df_combinato['published_at'] = pd.to_datetime(df_combinato['published_at'])
        print("Conversione date completata")
    except Exception as e:
        print(f"ERRORE nella conversione delle date: {str(e)}")
        return
    
    # Rimuovi i duplicati
    print("\nRimozione duplicati in corso...")
    df_finale = df_combinato.sort_values('published_at', ascending=False).drop_duplicates(
        subset=['repository', 'link_apk', 'repo_name', 'stars', 'description'],
        keep='first'
    )
    
    # Riordina le colonne
    colonne_ordinate = ['repository', 'link_apk', 'repo_name', 'stars', 'description', 'published_at']
    df_finale = df_finale[colonne_ordinate]
    
    # Salva il risultato
    output_file = "file_combinato.csv"
    df_finale.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # Statistiche finali
    duplicati_rimossi = len(df_combinato) - len(df_finale)
    end_time = datetime.now()
    tempo_elaborazione = (end_time - start_time).total_seconds()
    
    print("\n=== Statistiche Finali ===")
    print(f"File elaborati: {files_elaborati:,}")
    print(f"Righe totali iniziali: {righe_totali:,}")
    print(f"Righe dopo unione: {len(df_combinato):,}")
    print(f"Righe dopo rimozione duplicati: {len(df_finale):,}")
    print(f"Duplicati rimossi: {duplicati_rimossi:,}")
    print(f"Percentuale duplicati: {(duplicati_rimossi/len(df_combinato)*100):.2f}%")
    print(f"Tempo di elaborazione: {tempo_elaborazione:.2f} secondi")
    print(f"\nFile salvato come: {output_file}")
    print(f"\n=== Elaborazione completata: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")

if __name__ == "__main__":
    unisci_csv()
