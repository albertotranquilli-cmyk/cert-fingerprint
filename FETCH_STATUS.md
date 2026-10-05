# cert-fingerprint — stato al 2026-10-05

## Stato attuale

- **CI**: verde. Run #7 success (syntax check + unit tests, uplift 3.0 su dati sintetici).
- **Fetch run #5**: in corso (workflow_dispatch, avviato 10:16 UTC). Scarica CT log di 18 domini via crt.sh. Durata attesa: ~2 ore.
- **results/SUMMARY.md**: non ancora presente — il fetch non ha ancora prodotto output.
- **PAPER.md**: bozza strutturata con abstract, metodo, red team (7 attacchi), limiti dichiarati. Sezione risultati in attesa dei numeri reali.

## Prossimi passi

1. Automazione cert-fetch-weekly (lunedì 08:00 Europe/Rome) verifica il run e aggiorna il README con i numeri.
2. Se il run fallisce: il bot documenta l'errore esatto in TEST_LOG.md.
3. Cross-correlazione con i s di tiaoxiu-signal: il passo che rende il paper pubblicabile su arXiv.

## Nota onesta

Il valore monetizzabile arriva solo con numeri reali. Il codice da solo non vende. Il primo numero vero è la priorità assoluta.
