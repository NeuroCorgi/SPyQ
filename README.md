# SPyQ

Structured PYthon Queries.
Python to SQL meta-compiler

Kind of failed idea.

## Usage

```python
import spyq

spyq.discover("/path/to/database.db")
```

`spyq.discover` will create global variables that represent tables found in the database.
Operations on the tables are lazy-evaluated, so statement won't be executed until its result is need. 

## Examples

1. `SELECT` statements:

```sql
SELECT Name FROM tracks
WHERE Milliseconds > 180000
```

```python
for name in (Tracks.Milliseconds > 180000).Name:
...
```

2. `UPDATE` statements:

```sql
UPDATE tracks
SET Name = "name"
WHERE Milliseconds > 180000
AND Composer = "ComposerName"
```

```python
t = (Tracks.Milliseconds > 180000) & (Tracks.Composer == "Composername")
t.Name = "name"
```

## Limitations

- Column filtering is not implemented.

```python
names = Tracks.Name

filtered_names = names.Milliseconds > 180000
```

- Updating multiple columns can only be done with multiple quieries.

```python
t.Name = "name"
t.Milliseconds = "240000"
```

- Insert statements are not yet supported.

- Create statements are not supported.

Sample databse taken from [here](https://www.sqlitetutorial.net/sqlite-sample-database/).
