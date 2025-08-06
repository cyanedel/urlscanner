# URL Scanner
Scans an URL to detect url dependencies.

## Commands
### scan
| Args | Description |
|---|---|
| ```--url``` | Target website URL (e.g., https[]()://example.com) |
| ```--output``` or ```-o``` | Output file path (e.g., example.txt). Defaults to datetime. |
| ```--browser``` or ```-b``` | Pick a browser: chrome/firefox, defaults to chrome |
| ```--level``` or ```-l``` | Number 1-3; 1 = base domain; 2 = sub domain; 3 = full url; defaults to 1 |

You can also change browser and level in the config.ini file.

### aggregate
Aggregates all scanned urls in output directory to a single list.

## Examples
Scan an URL 
```
URLScanner scan --url https://example.com -o example.txt
```

Aggregate URLs 
```
URLScanner aggregate
```

## Generate executables
```
pyinstaller --onefile --name URLScanner urlscan.py
```