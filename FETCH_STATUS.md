# cert-fingerprint — stato al 2026-10-05 (post-fix)

## Fix applicati oggi

1. **fetch.yml**: aggiunto `timeout-minutes: 360` — il workflow non viene più ucciso a metà download.
2. **fetch_ct.py**: contatore ok/fail, exit code 1 se TUTTI i domini falliscono (il workflow fallisce davvero invece di sembrare riuscito), log con flush per vedere il progresso in tempo reale.
3. **Automazione cert-fetch-weekly**: riscritta — niente più "ripollo dopo". Ora: se il run è in corso, aspetta e ripolla fino a completamento (max 12 tentativi, 10 min tra uno e l'altro = 2 ore). Se fallisce, legge i log e documenta l'errore esatto. Se riesce, aggiorna il README con i numeri.

## Stato

- CI: verde (run #7).
- Fetch run #5: in corso con il vecchio workflow (senza timeout). Se fallisce per timeout, il nuovo workflow è già pronto e il bot lo ritriggherà.
- results/SUMMARY.md: non ancora presente.

## Prossimi passi

1. Il bot cert-fetch-weekly (domani 08:00 o run_now) verifica il run e aggiorna.
2. Cross-correlazione con i s di tiaoxiu-signal.
3. Post X: testo pronto in tiaoxiu-signal/POST.md — va incollato manualmente (nessun connettore X organico).
