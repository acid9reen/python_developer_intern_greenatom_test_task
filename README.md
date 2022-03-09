# Greenatom test task for python developer intern

## Task

- [x] Implement the web service according to the interface, defined in table:

| Title                   | Method | Description |
| ----------------------- | ------ | ----------- |
| `/frame/`               | PUT    | Save the input files to a folder \/data\/\<date in YYYYMMDD format\>\/ with names \<GUID\>.jpg and commit to the database in the inbox table with structure \<request code\> \| \<name of saved file\> \| \<date/time of registration\>. |
| `/frame/<request_code>` | GET    | Return a list of images in JSON format (including date and time of registration and file names), matching request code. |
| `frame/<request_code>`  | DELETE | Delete data from the database and corresponding image from data/ folder, matching request code. |

- [x] Implement unit tests for full functionality coverage.
- [ ] (Optional) Implement web service authentication for access restrictions.

## Configure and run

### Before running

Install all dependencies:

```bash
pip install -r requirements/requirements.txt
```

Add .env file with `DATABASE_URL` variable, containing database url in format

`postgresql://postgres:<password>@<database IP address with port>/<database name>`

(NOTE: you need postgresql database installation)

### Start the application

To run app:

```bash
uvicorn main:app
```

## Run tests

### Before running

To run tests you need to install development dependencies

```bash
pip install -r requirements/dev.txt
```

Add .env file with `TEST_DATABASE_URL` variable, containing database url in format

`postgresql://postgres:<password>@<database IP address with port>/<test database name>`

(NOTE: you need postgresql database installation)

### Run tests

```bash
pytest .
```
