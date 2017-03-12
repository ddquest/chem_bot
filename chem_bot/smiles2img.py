# -*- coding: utf-8 -*-

import os

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
from rdkit.Chem.Draw.rdMolDraw2D import MolDraw2DSVG


class SmilesEncoder(object):
    """SmilesEncoder."""
    def __init__(self, smiles):
        self.name = 'SmilesEncoder'
        self.smiles = smiles
        self.mol = self._to_mol()

    def _to_mol(self):
        """Encode smiles to mol."""
        return Chem.MolFromSmiles(self.smiles)

    def to_img(self, encode_type, width=420, height=420):
        """Encode smiles to image"""
        Chem.Kekulize(self.mol)

        if not self.mol.GetNumConformers():
            AllChem.Compute2DCoords(self.mol)

        if encode_type == 'svg':
            drawer = MolDraw2DSVG(width, height)
        elif encode_type == 'png':
            drawer = Draw.MolDraw2DCairo(width, height)

        drawer.FinishDrawing()
        drawer.DrawMolecule(self.mol)
        self.canvas = drawer.GetDrawingText()
        self.encode_type = encode_type
        return self.canvas

    def to_png(self, width=420, height=420):
        """Synonym of to_img(encode_type='png')"""
        return self.to_img('png', width, height)

    def to_svg(self, width=420, height=420):
        """Synonym of to_img(encode_type='svg')"""
        return self.to_img('svg', width, height)

    def to_file(self, filename):
        """Write mol draw object to file."""
        if not hasattr(self, 'encode_type'):
            raise AttributeError

        ext = os.path.splitext(filename)[1]
        if ext != '.{0}'.format(self.encode_type):
            filename += '.{0}'.format(self.encode_type)

        if self.encode_type == 'svg':
            write_mode = 'w'

        if self.encode_type == 'png':
            write_mode = 'wb'

        with open(filename, write_mode) as f:
            f.write(self.canvas)
