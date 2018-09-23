# -*- coding: utf-8 -*-
import os
import rdkit
from nose.tools import with_setup, raises
from chem_bot import SmilesEncoder


class TestSmilesEncoder(object):

    @classmethod
    def setup(self):
        self.encoder = SmilesEncoder('c1ccccc1')

    def test_init(self):
        assert self.encoder.name == 'SmilesEncoder'
        assert hasattr(self.encoder, 'mol')

    def test_to_mol(self):
        assert type(self.encoder._to_mol()) == rdkit.Chem.rdchem.Mol

    def test_to_img_svg(self):
        assert type(self.encoder.to_img('svg')) == str
        assert type(self.encoder.to_img('svg', width=200)) == str
        assert type(self.encoder.to_img('svg', height=200)) == str
        assert type(self.encoder.to_img('svg', width=200, height=200)) == str

    def test_to_img_png(self):
        assert type(self.encoder.to_img('png')) == bytes
        assert type(self.encoder.to_img('png', width=200)) == bytes
        assert type(self.encoder.to_img('png', height=200)) == bytes
        assert type(self.encoder.to_img('png', width=200, height=200)) == bytes

    @raises(UnboundLocalError)
    def test_invalid_encode_type_to_img(self):
        self.encoder.to_img('invalid')

    def test_to_png(self):
        assert type(self.encoder.to_png()) == bytes
        assert type(self.encoder.to_png(width=200)) == bytes
        assert type(self.encoder.to_png(height=200)) == bytes
        assert type(self.encoder.to_png(width=200, height=200)) == bytes

    def test_png_to_file(self):
        self.encoder.to_png()
        filename = os.path.join('/tmp', 'test_smi_file.png')
        self.encoder.to_file(filename)
        assert os.path.exists(filename) is True
        os.remove(filename)

    def test_to_svg(self):
        assert type(self.encoder.to_svg()) == str
        assert type(self.encoder.to_svg(width=200)) == str
        assert type(self.encoder.to_svg(height=200)) == str
        assert type(self.encoder.to_svg(width=200, height=200)) == str

    def test_svg_to_file(self):
        self.encoder.to_svg()
        filename = os.path.join('/tmp', 'test_smi_file.svg')
        self.encoder.to_file(filename)
        assert os.path.exists(filename) is True
        os.remove(filename)

    @raises(UnboundLocalError)
    def test_invalid_encode_type_to_file(self):
        filename = os.path.join('/tmp', 'test_smi_file.png')
        self.encoder.encode_type = 'unrecognize'
        self.encoder.to_file(filename)

    @raises(AttributeError)
    def test_unset_encode_type_to_file(self):
        filename = os.path.join('/tmp', 'test_smi_file.png')
        encoder = SmilesEncoder('c1ccccc1')
        encoder.to_file(filename)
