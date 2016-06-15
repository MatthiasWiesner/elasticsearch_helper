# elasticsearch_helper

A simple wrapper to use for some admin elasticsearch operations

## Install
Clone the repository and install the required pacakges (I recommend to use a virtualenv).
```
pip install -r requirements.txt
```

## Indexes
See documentation:
https://elasticsearch-py.readthedocs.io/en/master/api.html#indices

## Usage
```
$ python index.py
Usage: index.py [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --hosts TEXT  [required]
  --help            Show this message and exit.

Commands:
  create_alias    Create alias for indexes
  create_index    Create index
  delete_aliases  Delete alias from indexes
  delete_index    Delete indexes
  get_aliases     Get aliases for index
  move_alias      Move alias from one index to another
  reindex         Reindex one index to another (!Experimental, don't use it for large indexes)
```

### Example:
Move alias from one index to another:
```
python index.py -h 10.210.0.30 move_alias openhpi openhpi_v5 openhpi_v6
```