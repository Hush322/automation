# Laboratorul 04 – Jenkins Controller și SSH Agent cu Docker

## 1. Scopul laboratorului

Scopul acestui laborator este configurarea unui mediu de integrare continuă (CI) utilizând Jenkins, Docker și un agent SSH separat.

În cadrul laboratorului au fost realizate următoarele:
- Configurarea Jenkins Controller într-un container Docker.
- Crearea și configurarea unui SSH Agent.
- Instalarea PHP și Composer pe agent.
- Configurarea autentificării SSH dintre Jenkins și agent.
- Crearea unui proiect PHP cu teste PHPUnit.
- Configurarea unui Jenkins Pipeline pentru instalarea dependențelor și executarea automată a testelor.

## 2. Arhitectura soluției

Soluția este formată din două containere Docker:

**Jenkins Controller**
- Gestionează interfața Jenkins și joburile.
- Coordonează executarea pipeline-urilor.
- Păstrează configurațiile și istoricul compilărilor.

**SSH Agent**
- Este conectat la Jenkins Controller prin SSH.
- Execută comenzile pipeline-ului.
- Conține PHP CLI, Composer și Git.
- Rulează testele proiectului PHP.

Containerele sunt conectate prin rețeaua Docker `jenkins-network`.

## 3. Configurarea mediului Docker

Pentru pornirea mediului a fost creat fișierul `docker-compose.yml`, care definește serviciile Jenkins Controller și SSH Agent.

Au fost configurate:
- Portul `8080` pentru interfața web Jenkins.
- Portul `50000` pentru comunicația Jenkins.
- Volumul `jenkins_home` pentru datele controllerului.
- Volumul `jenkins_agent_volume` pentru agent.
- Rețeaua Docker `jenkins-network`.

Imaginea agentului a fost construită folosind un `Dockerfile` bazat pe `jenkins/ssh-agent`.

Pe agent au fost instalate:
- PHP CLI;
- PHP DBG;
- extensiile PHP necesare;
- Composer;
- Git;
- curl și unzip.

## 4. Configurarea autentificării SSH

Pentru conectarea agentului la Jenkins au fost generate chei SSH RSA în format PEM.

Cheia publică a fost introdusă în fișierul `.env`, iar cheia privată a fost adăugată în Jenkins ca o credențială de tip **SSH Username with private key**.

Configurarea credențialei:
- Username: `jenkins`
- ID: `ssh-agent-key`

În Jenkins a fost creat un nod permanent cu următoarele setări:

| Parametru | Valoare |
|---|---|
| Name | `ssh-agent1` |
| Remote root directory | `/home/jenkins/agent` |
| Labels | `php-agent` |
| Number of executors | `1` |
| Launch method | Launch agents via SSH |
| Host | `ssh-agent` |
| Port | `22` |
| Credentials | `ssh-agent-key` |

După configurare, agentul a fost conectat cu succes și a apărut cu starea **Online**.

## 5. Crearea proiectului PHP

A fost creat un proiect separat, numit `php-price-calculator`, publicat pe GitHub:

https://github.com/Hush322/php-price-calculator

Structura proiectului:

```text
php-price-calculator/
├── src/
│   └── PriceCalculator.php
├── tests/
│   └── PriceCalculatorTest.php
├── composer.json
├── composer.lock
├── phpunit.xml
└── Jenkinsfile
```

Clasa `PriceCalculator` implementează două funcții:
- `calculateWithTax()` – calculează prețul cu TVA.
- `applyDiscount()` – calculează prețul după aplicarea unei reduceri.

Au fost create patru teste PHPUnit:
1. Verificarea calculării prețului cu TVA.
2. Verificarea aplicării reducerii.
3. Verificarea respingerii unui preț negativ.
4. Verificarea respingerii unei reduceri invalide.

## 6. Configurarea Jenkins Pipeline

În Jenkins a fost creat un job de tip **Pipeline**, cu numele `php-price-calculator`.

Pipeline-ul preia automat codul sursă din repository-ul GitHub.

Configurarea repository-ului:
- SCM: Git
- Repository URL: `https://github.com/Hush322/php-price-calculator.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

Pipeline-ul folosește agentul cu eticheta `php-agent`.

### Explicația Jenkinsfile

Pipeline-ul conține două etape principale:

**Etapa 1 – Install Dependencies**

```groovy
sh 'composer install --no-interaction'
```

Această comandă instalează dependențele proiectului pe baza fișierului `composer.lock`.

**Etapa 2 – Test**

```groovy
sh './vendor/bin/phpunit --testdox'
```

Această comandă execută testele PHPUnit și afișează rezultatele într-un format ușor de citit.

La final, secțiunea `post` afișează mesaje diferite în funcție de rezultatul pipeline-ului.

## 7. Rezultatul executării

După salvarea configurării, a fost pornită prima compilare folosind opțiunea **Build Now**.

Jenkins a reușit:
- Să preia proiectul din GitHub.
- Să execute pipeline-ul pe agentul `ssh-agent1`.
- Să instaleze dependențele Composer.
- Să execute toate testele PHPUnit.

Rezultatul testării:

```text
PHPUnit 11.5.57

✔ Calculate price with tax
✔ Apply discount
✔ Negative price throws exception
✔ Invalid discount throws exception

OK (4 tests, 4 assertions)

Finished: SUCCESS
```

Prin urmare, toate cele patru teste au trecut cu succes, iar pipeline-ul s-a încheiat cu starea `SUCCESS`.

## 8. Tipuri de agenți Jenkins

În Jenkins pot fi utilizați mai mulți tipuri de agenți:

- **SSH Agent** – agent conectat la controller prin SSH. Este tipul utilizat în acest laborator.
- **Inbound Agent (JNLP)** – agent care inițiază conexiunea către controller.
- **Docker Agent** – agent care rulează într-un container Docker.
- **Kubernetes Agent** – agent creat dinamic într-un cluster Kubernetes.
- **Built-in Node** – nodul încorporat în Jenkins Controller, care poate executa și el sarcini.

Agenții permit distribuirea sarcinilor pe medii diferite și evită încărcarea exclusivă a controllerului.

## 9. Probleme întâlnite și soluții

În timpul realizării laboratorului au apărut câteva probleme:

**1. Formatul cheii SSH**

Inițial, formatul cheii generate nu a fost acceptat de configurarea agentului. Problema a fost rezolvată prin generarea unei chei RSA în format PEM.

**2. Instalarea dependențelor PHP**

La instalarea Composer au apărut erori din cauza unor extensii PHP lipsă. Au fost adăugate în Dockerfile extensiile necesare, inclusiv `php-xml`, `php-curl` și `php-mbstring`.

**3. Executarea Composer în mediul local**

În mediul WSL, Composer nu era disponibil în modul necesar pentru proiect. Dependențele au fost instalate în containerul SSH Agent, unde PHP și Composer erau configurate corect.

**4. Publicarea proiectului**

Fișierul `composer.lock` a fost generat în container și copiat în proiectul local înainte de publicarea pe GitHub.

**5. Mesajul Git din Jenkins**

La prima compilare a apărut mesajul `Selected Git installation does not exist. Using Default`. Acesta nu a blocat procesul, deoarece Jenkins a identificat și utilizat Git-ul disponibil pe agent.

## 10. Concluzie

În cadrul acestui laborator am configurat cu succes un mediu Jenkins format dintr-un controller și un agent SSH, utilizând Docker Compose.

Am învățat să configurez autentificarea SSH, să înregistrez un agent permanent în Jenkins și să creez un pipeline automat pentru un proiect PHP.

Prin executarea pipeline-ului, am verificat că Jenkins poate prelua codul sursă din GitHub, instala dependențele necesare și rula automat testele pe un agent separat.

Rezultatul final a fost unul reușit: toate cele patru teste PHPUnit au trecut, iar compilarea s-a încheiat cu `SUCCESS`.

Acest laborator demonstrează modul în care Jenkins poate automatiza procesele de integrare continuă și poate distribui sarcinile între mai multe mașini sau containere.
