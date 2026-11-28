# AETC Migration Validation

This project compares indicators between a harmonized MAHIS source and a QECH AETC source. It loads indicator queries from JSON files, runs them against both MySQL databases, and writes discrepancies to an Excel workbook.

## Prerequisites

- Python 3.10 or newer (Python 3.13 is verified for this project)
- Access to both MySQL databases
- SQLAlchemy database credentials
- Optional SSH access if either database cannot be reached directly

## macOS Setup

1. Install Python using Homebrew:

```bash
brew install python
```

2. Open Terminal and change to the project directory:

```bash
cd validate_aetc_migration_migration
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate it:

```bash
source venv/bin/activate
```

5. Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Windows Setup

1. Install Python 3.10 or newer from the Microsoft Store or from https://www.python.org/downloads/windows/. Select **Add Python to PATH** during installation.

2. Open PowerShell and change to the project directory:

```powershell
cd validate_aetc_migration
```

3. Create a virtual environment:

```powershell
py -m venv venv
```

4. Activate it:

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell prevents script activation, allow activation for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

Command Prompt users can activate with:

```cmd
venv\Scripts\activate.bat
```

5. Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ubuntu Setup

1. Install Python and the virtual environment package:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

2. Change to the project directory:

```bash
cd validate_aetc_migration
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate it:

```bash
source venv/bin/activate
```

5. Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure the Databases

1. Copy the example configuration:

```bash
cp config.example.py config.py
```

On Windows PowerShell:

```powershell
Copy-Item config.example.py config.py
```

2. Edit `config.py` and set:

- `START_DATE` and `END_DATE`
- `SOURCE1` for the harmonized MAHIS database
- `SOURCE2` for the QECH AETC database
- SQLAlchemy username, password, host, port, and database name

Example SQLAlchemy MySQL URL structure:

```text
mysql+pymysql://username:password@host:3306/database
```

Do not commit real passwords or SSH credentials. The project uses `config.py` for local configuration, and `config.example.py` is the credential-free template.

## SSH Configuration

Set `USE_SSH=False` for a direct database connection.

For SSH, set `USE_SSH=True` inside the relevant source and provide:

- `HOST`
- `PORT`
- `USERNAME`
- `PASSWORD` when `USE_KEY=False`
- `KEY_PATH` when `USE_KEY=True`

The SSH settings are independent for `SOURCE1` and `SOURCE2`, and `USE_KEY` controls password or private-key authentication for that source.

## Indicator Files

The indicator JSON files are stored in the `input` folder:

- `input/harmonized.json` — source `db1`
- `input/qech_aetc.json` — source `db2`

Each file must contain a non-empty `source` and an `indicators` list:

```json
{
  "source": "db1",
  "indicators": [
    {
      "id": 1,
      "name": "Example Indicator",
      "sql": "SELECT COUNT(*) FROM encounter e WHERE {date_filter}"
    }
  ]
}
```

Supported placeholders include:

- `{base_query}` — the shared encounter/visit/observation join
- `{date_filter}` — the configured start and end encounter-date window
- `{start_date}` and `{end_date}` — the configured report window values

Indicator SQL must return one aggregate value.

## Run the Validation

With the virtual environment active:

```bash
python validate.py
```

The program prints connection status and progress for each source and indicator. It then creates:

```text
output/Output_Static.xlsx
```

The Excel columns are generated from the `source` values in the two input JSON files.

## Troubleshooting

- `ModuleNotFoundError: pymysql` — rerun `python -m pip install -r requirements.txt`.
- `Can't connect to MySQL server on '@localhost'` — the URL was likely created from a password containing an unescaped `@`. Use `URL.create()` with separate username, password, host, port, and database values.
- `No module named sqlalchemy` — confirm that the virtual environment is active and dependencies are installed.
- `SSH_CONFIG must include` — complete the SSH host and username, and provide a password or private key according to `USE_KEY`.
- Database date mismatch — verify `START_DATE`, `END_DATE`, and `DATE_COLUMN` in `config.py`.

Deactivate the virtual environment with:

```bash
deactivate
```

