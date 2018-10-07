# -*- coding: utf-8 -*-

from rdkit import Chem
from subprocess import PIPE, Popen


def iupac_to_smiles(iupac, opsin='opsin.jar'):
    """Convert IUPAC to SMILES by opsin.

    Args:
        iupac: strings for convert
        opsin: opsin.jar file path

    Returns:
        smiles: str
        error: stderr strings of opsin
    """
    cmd = 'java -jar {0}'.format(opsin)
    with Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        smiles = proc.communicate(iupac.encode())
    return (Chem.MolToSmiles(
        Chem.MolFromSmiles(smiles[0].decode('utf8').strip('\r\n'))),
            smiles[1].decode('utf8').strip('\r\n').split(':')[-1].lstrip(' '))


if __name__ == '__main__':
    res, error = iupac_to_smiles('benzen', opsin='../../../java/opsin.jar')
    print('"{0}"'.format(res))
    print(type(res))
    print(error)
