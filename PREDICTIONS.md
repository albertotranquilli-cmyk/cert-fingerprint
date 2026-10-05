# PREDICTIONS.md — cosa deve mostrare il fetch CT per confermare il segnale storico

Aggiornato: 2026-10-05. Costruito su dati storici tiaoxiu-signal (ASF panel, 71 repo, s=0.334, z=22.6).

## Ipotesi di lavoro

Il segnale tiaoxiu-signal (attivita' GitHub che segue il calendario cinese) deve avere un **substrato infrastrutturale**: i certificati TLS emessi per domini cinesi devono mostrare picchi nei make-up days (调休), mentre i controlli occidentali e giapponesi no.

## Predizioni numeriche (derivate da s)

| Gruppo | s storico | Uplift atteso (1+s) | Range accettabile |
|---|---:|---:|---|
| Domini cinesi (12) | 0.334 | **1.334** | uplift > 1.20 |
| Controlli US (6) | ~0 | **1.000** | uplift in [0.85, 1.15] |
| Controlli JP (3) | ~0 | **1.000** | uplift in [0.85, 1.15] |
| Repo >=1% zh (se mappabili) | 0.65 | 1.650 | uplift > 1.40 |
| Repo <1% zh | 0.06 | 1.060 | uplift in [0.95, 1.20] |
| Baidu/Alibaba | 0.59 | 1.590 | uplift > 1.35 |

## Test statistici richiesti

1. **CN vs US**: Welch t-test, p < 0.01 (one-sided). Con 12 vs 6 domini e rumore realistico, la simulazione da 20000 run da tiaoxiu-signal predice t ≈ 4.5, p ≈ 2.6e-6.
2. **JP vs US**: p > 0.10 (nessun segnale — controllo negativo).
3. **Mediana CN > 1.20** e **mediana US in [0.85, 1.15]** contemporaneamente.

## Coerenze incrociate gia' note da tiaoxiu-signal

- 78% dell'eccesso ASF cade nelle ore d'ufficio Pechino (09-19 CST) vs 37% del gap normale -> il segnale e' ora-condizionato, non solo giorno-condizionato.
- Top 10 repo = 62% del segnale; rimuovendo i top 5, s scende a 0.229 ma resta alto -> segnale diffuso, non 1-2 repo anomali.
- z = 22.6 -> probabilita' che sia caso < 10^-100.

## Esito possibile

- **CONFERMA**: uplift CN > 1.20, US/JP piatti, p < 0.01. Due substrati indipendenti (GitHub activity + CT issuance) misurano la stessa cosa -> paper arXiv pronto.
- **SMENTITA PARZIALE**: uplift CN tra 1.05 e 1.20. Segnale reale ma debole su questo substrato -> documentare, non pubblicare.
- **SMENTITA**: uplift CN <= 1.05 o US/JP mostrano uplift anomalo. Il metodo tiaoxiu-signal va rivisto o il fenomeno e' specifico di GitHub.

## Nota onesta

Queste predizioni sono derivate da un solo esperimento (tiaoxiu-signal). Se il fetch CT le conferma, la probabilita' che sia un artefatto metodologico comune crolla — ma non a zero. Il red team di tiaoxiu-signal (26 attacchi) copre gli attacchi noti; quelli sconosciuti restano sconosciuti.
