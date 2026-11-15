# Laboratorul 05 – Ansible, Jenkins și configurarea automată a unui server de test

## 1. Descrierea proiectului

În acest laborator am extins mediul din lab04 (Jenkins Controller + SSH Agent) cu un **Ansible Agent** și un **server de test**. Ansible configurează serverul (Apache2, PHP, virtual host), iar Jenkins rulează trei pipeline-uri: build + teste, configurarea serverului și deploy-ul aplicației PHP (`php-price-calculator`).

Arhitectura (toate containerele sunt în rețeaua `jenkins-network`):

| Serviciu | Rol |
|---|---|
| `jenkins-controller` | Interfața Jenkins, coordonează pipeline-urile |
| `ssh-agent` | Agent (label `php-agent`): Composer + PHPUnit |
| `ansible-agent` | Agent (label `ansible-agent`): rulează playbook-urile Ansible |
| `test-server` | Ubuntu cu SSH; configurat de Ansible; web pe `localhost:8081` |

Structura lab05:

```text
lab05/
├── compose.yaml
├── Dockerfile.ssh_agent
├── Dockerfile.ansible_agent
├── Dockerfile.test_server
├── scripts/            (entrypoint-uri: scriu cheile publice în authorized_keys)
├── ansible/
│   ├── ansible.cfg
│   ├── hosts.ini
│   ├── group_vars/all.yml
│   ├── templates/php-app.conf.j2
│   ├── setup_test_server.yml
│   └── deploy_php.yml
└── pipelines/
    ├── php_build_and_test_pipeline.groovy
    ├── ansible_setup_pipeline.groovy
    └── php_deploy_pipeline.groovy
```

## 2. Chei SSH

Sunt necesare trei perechi de chei (generate în folderul `keys/`, care este în `.gitignore`):

```bash
mkdir -p keys
ssh-keygen -t rsa -b 4096 -m PEM -f keys/jenkins_ssh_agent     -N ""   # Jenkins -> ssh-agent
ssh-keygen -t rsa -b 4096 -m PEM -f keys/jenkins_ansible_agent -N ""   # Jenkins -> ansible-agent
ssh-keygen -t rsa -b 4096 -m PEM -f keys/ansible_server        -N ""   # ansible-agent -> test-server
```

Cheile **publice** se pun în fișierul `.env` (ignorat de Git):

```bash
cat > .env <<EOT
JENKINS_SSH_AGENT_PUBKEY="$(cat keys/jenkins_ssh_agent.pub)"
JENKINS_ANSIBLE_AGENT_PUBKEY="$(cat keys/jenkins_ansible_agent.pub)"
ANSIBLE_SERVER_PUBKEY="$(cat keys/ansible_server.pub)"
EOT
```

Cheile **private** se adaugă în Jenkins (*Manage Jenkins → Credentials → Global → Add Credentials → SSH Username with private key*):

| ID | Username | Cheia privată | Utilizare |
|---|---|---|---|
| `ssh-agent-key` | `jenkins` | `jenkins_ssh_agent` | conectarea nodului `ssh-agent1` |
| `ansible-agent-key` | `jenkins` | `jenkins_ansible_agent` | conectarea nodului `ansible-agent1` |
| `ansible-server-key` | `ansible` | `ansible_server` | folosită în pipeline pentru ansible-agent → test-server |

## 3. Configurarea Jenkins Controller

1. `docker compose up -d --build`
2. Deschid `http://localhost:8080`, introduc parola inițială (`docker exec jenkins-controller cat /var/jenkins_home/secrets/initialAdminPassword`) și creez utilizatorul administrator.
3. Instalez pluginurile: **Docker**, **Docker Pipeline**, **GitHub Integration**, **SSH Agent** (plus pluginurile sugerate).

## 4. Configurarea SSH Agent

`Dockerfile.ssh_agent` este cel din lab04 (bazat pe `jenkins/ssh-agent`, cu PHP-CLI, extensii PHP, Composer, Git). Serviciul `ssh-agent` primește cheia publică prin `JENKINS_AGENT_SSH_PUBKEY`. În Jenkins nodul `ssh-agent1` (label `php-agent`, host `ssh-agent`, credențiala `ssh-agent-key`, remote root `/home/jenkins/agent`) se configurează ca în lab04.

## 5. Crearea și configurarea Ansible Agent

`Dockerfile.ansible_agent` pornește de la `ubuntu:24.04` și instalează `ansible`, Java (necesar pentru `agent.jar`), `openssh-server`, `git` și `python3`. Se creează utilizatorul `jenkins`, iar `sshd` este configurat să accepte doar chei. La pornire, `entrypoint-agent.sh` scrie cheia publică din variabila de mediu în `authorized_keys`.

În Jenkins se creează nodul permanent:

| Parametru | Valoare |
|---|---|
| Name | `ansible-agent1` |
| Remote root directory | `/home/jenkins/agent` |
| Labels | `ansible-agent` |
| Launch method | Launch agents via SSH |
| Host | `ansible-agent` |
| Credentials | `ansible-agent-key` |

Ansible folosește cheia `ansible_server` pentru conectarea la serverul de test; aceasta este furnizată pipeline-ului din Jenkins Credentials (`ansible-server-key`) prin `withCredentials` și parametrul `--private-key`. Utilizatorul de conectare (`ansible`) este setat în `hosts.ini`.

## 6. Crearea serverului de test

`Dockerfile.test_server` (Ubuntu 24.04) instalează `openssh-server`, `sudo` și `python3` (necesar pentru modulele Ansible). Se creează utilizatorul `ansible` cu `sudo` fără parolă, iar `sshd` permite doar autentificarea cu chei (`PasswordAuthentication no`). `entrypoint-test-server.sh` scrie cheia publică `ansible_server.pub` în `/home/ansible/.ssh/authorized_keys`. Portul 80 al serverului este publicat pe `localhost:8081`.

## 7. Playbook-ul Ansible

**`hosts.ini`** – definește grupul `test_servers` cu hostul `test-server` (utilizator `ansible`, port 22).

**`setup_test_server.yml`** – taskuri:
1. actualizarea cache-ului apt;
2. instalarea Apache2;
3. instalarea PHP și a extensiilor (`libapache2-mod-php`, `php-xml`, `php-mbstring`, `php-curl`);
4. activarea modulului `rewrite` (`community.general.apache2_module`);
5. crearea directorului rădăcină `/var/www/php-app/public`;
6. o pagină implicită, creată doar dacă nu există (`force: false`);
7. configurarea virtual host-ului din șablonul `php-app.conf.j2`;
8. dezactivarea site-ului implicit și activarea celui al aplicației (`a2dissite` / `a2ensite`, idempotent prin `removes` / `creates`);
9. pornirea Apache2; handler-ul `Restart Apache` repornește serviciul când se schimbă configurația.

Deoarece containerul nu rulează systemd, modulul `service` este folosit cu `use: service`.

**`deploy_php.yml`** – copiază `src/` și `public/` din proiect în `/var/www/php-app`, verifică sintaxa PHP și testează că aplicația răspunde cu HTTP 200 (`uri`).

Pentru ca aplicația să aibă o pagină web, în proiectul `php-price-calculator` a fost adăugat fișierul `public/index.php`, care folosește clasa `PriceCalculator`.

## 8. Pipeline-urile Jenkins

Pentru fiecare se creează un job de tip **Pipeline** cu *Pipeline script from SCM* (Git, `https://github.com/Hush322/automation.git`, branch `*/lab05`):

| Job | Script Path | Agent |
|---|---|---|
| `php-build-and-test` | `lab05/pipelines/php_build_and_test_pipeline.groovy` | `php-agent` |
| `ansible-setup` | `lab05/pipelines/ansible_setup_pipeline.groovy` | `ansible-agent` |
| `php-deploy` | `lab05/pipelines/php_deploy_pipeline.groovy` | `ansible-agent` |

- **php_build_and_test** – clonare, `composer install`, `phpunit --log-junit`, raportare cu `junit`.
- **ansible_setup** – clonare, verificare conexiune (`ansible -m ping`), rularea `setup_test_server.yml`.
- **php_deploy** – clonare proiect PHP, clonare playbook-uri, rularea `deploy_php.yml` cu `-e project_dir=$WORKSPACE/php-app`.

Ordinea de rulare: `ansible-setup` → `php-build-and-test` → `php-deploy`.

## 9. Testarea aplicației

După deploy, aplicația este disponibilă la `http://localhost:8081`.

<!-- TODO: adaugă captură de ecran cu pipeline-urile (SUCCESS) și cu pagina din browser -->

## 10. Răspunsuri la întrebări

**Care sunt avantajele utilizării Ansible pentru configurarea serverelor?**
- Este *agentless*: folosește doar SSH și Python pe server, fără software suplimentar.
- Playbook-urile YAML sunt declarative și ușor de citit.
- Taskurile sunt idempotente: rularea repetată nu modifică un server deja configurat.
- Configurația este cod, deci poate fi versionată în Git și reutilizată pe multe servere.
- Reduce erorile manuale și se integrează bine cu CI/CD (Jenkins).

**Ce alte module Ansible există pentru gestionarea configurației?**
`apt`/`yum`/`package` (pachete), `service`/`systemd` (servicii), `copy`/`template`/`lineinfile`/`blockinfile` (fișiere), `file` (permisiuni, directoare), `user`/`group`, `git`, `command`/`shell`, `cron`, `docker_container`, `ufw`/`firewalld`, `uri`, `apache2_module`, `mysql_db`/`postgresql_db`, `synchronize`.

**Ce probleme ați întâmpinat și cum le-ați rezolvat?**
<!-- COMPLETEAZĂ cu problemele reale. Exemple posibile: -->
- *Containerul nu rulează systemd* – modulul `service` nu putea porni Apache; soluție: `use: service`.
- *Ansible nu putea rula module pe server* – lipsea `python3` pe imaginea Ubuntu; a fost adăugat în `Dockerfile.test_server`.
- *Eroare de permisiuni la cheia privată* – cheia trebuie să aibă permisiuni 600; soluție: folosirea `withCredentials`, care creează un fișier temporar cu permisiunile corecte.
- *Verificarea cheii host-ului SSH* – a fost dezactivată în `ansible.cfg` (`host_key_checking = False`) pentru mediul de laborator.
