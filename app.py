# -*- coding: UTF-8 -*-
import tempfile
from flask import Flask, request, send_file
from chem_bot import SmilesEncoder


app = Flask(__name__)


@app.route('/')
def index():
    return 'chem_bot API'


@app.route('/api/v1.0/smi2img', methods=['GET'])
def smi2img():
    """smi2img is a simple SMILES encoder.

    example:
        curl http://127.0.0.1:5000/api/v1.0/smi2img?smi=c1ccccc1 > c1cccc1.png
    paramater:
        smi: strings of SMILES
        width: int
        height: int
    """
    smi = request.args.get('smi')
    width = request.args.get('width')
    height = request.args.get('height')
    if not width:
        width = 420
    if not height:
        height = 420
    with tempfile.NamedTemporaryFile(suffix='.png') as fp:
        encoder = SmilesEncoder(smi)
        encoder.to_png(width=int(width), height=int(height))
        encoder.to_file(fp.name)
        return send_file(fp.name,
                         mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
