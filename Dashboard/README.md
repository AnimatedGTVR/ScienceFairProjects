# Science Fair Progress Dashboard

This folder is a small website made from plain HTML, CSS, and JavaScript.
`server.py` adds a read-only JSON API that supplies the live experiment counts.
It uses Python's standard library, so there are no packages to install.

## Start it

On Windows, double-click `run.cmd` or run:

```powershell
.\run.ps1
```

On macOS or Linux:

```sh
chmod +x run.sh
./run.sh
```

Then open <http://127.0.0.1:8080>. The page refreshes its data every ten seconds.

## Password experiment demo

The page includes a small browser version of the classroom password experiment.
It tries numbers, the supplied common-password list, pairs from that list, and
letter-and-number strings up to three characters long. It stops after 500,000
guesses so the page remains responsive. Entered text stays in the browser and is
cleared after each test; visitors should still use only made-up passwords.

## Public website

The project computer runs a Cloudflare Quick Tunnel that gives this dashboard a
public `trycloudflare.com` address with no account or sign-in required. It shows
the live API counts while the computer is on. The temporary address is saved in
`ScienceFairRunner/public-dashboard-url.txt` and changes after a tunnel restart.
The API never returns a found password.

The raw API is available at <http://127.0.0.1:8080/api/status>. It returns
completed, target, remaining, percentage, update time, and health state. It does
not return a recovered password.

## Put the HTML somewhere else

Copy `index.html`, `styles.css`, `app.js`, `guesser.js`, and `passwords.txt` to
any static web host. Point
the page to a reachable API by adding its address to the URL:

```text
https://your-site.example/?api=http://YOUR-COMPUTER:8080/api/status
```

Browsers can block an HTTP API from an HTTPS website, and `127.0.0.1` is only
reachable on the same computer. For a public live dashboard, run this API on a
server you control behind HTTPS. The API enables read-only CORS requests.

## Different progress-file locations

The server automatically recognizes this workspace layout. On another computer,
set these environment variables before starting it:

```text
SCIENCE_FAIR_MINE_DATA=/path/to/training_data.csv
SCIENCE_FAIR_PASSWORD_STATE=/path/to/password-search-state.json
```

Use `python server.py --snapshot` to print one API response without starting
the website. Use `python server.py --host 0.0.0.0` only when you intentionally
want other devices on your local network to connect.

