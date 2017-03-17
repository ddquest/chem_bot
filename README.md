![chem_bot_logo](docs/img/chem_bot_logo.png)
# Chem bot

## Install

Clone this repo.

```
git clone https://github.com/kubor/chem_bot.git
```

Prepare conda environment.

```
cd chem_bot
conda env create -n chem_bot -f environment.yml
```

Activate conda environment.

```
source activate chem_bot
```

Install `chem_bot`.

Run pip command at `chem_bot` directory.

```
python setup.py install
```

## Usage

Here is a sample code of convert smiles to png image.

```python
from chem_bot import SmilesEncoder
```

```python
encoder = SmilesEncoder('C(CN(CC(=O)O)CC(=O)O)N(CC(=O)O)CC(=O)O')
encoder.to_png()
encoder.to_file('edta.png')
```

![edta](docs/img/edta.png)


### Use png binary

`.to_png()` return binary PNG code.

```python
png_binary = encoder.to_png()
```

## Twitter bot(alpha)

Before run the bot, set config files.

- `twitter.config`
- `twitter.token`

Then, run a script `bin/run_twitter_client.py` .
