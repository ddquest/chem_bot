# -*- coding: utf-8 -*-

from subprocess import PIPE, Popen


def iupac_to_smiles(iupac, opsin='opsin.jar'):
    """Convert IUPAC to SMILES by opsin.

    Args:
        iupac: strings for convert
        opsin: opsin.jar file path

    Returns:
        smiles: str
    """
    cmd = 'java -jar {0}'.format(opsin)
    with Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        smiles = proc.communicate(iupac.encode())
    return smiles[0].decode('utf8')


if __name__ == '__main__':
    print(iupac_to_smiles(
        "2,2',2'',2'''-(Ethane-1,2-diyldinitrilo)tetraacetic acid",
        opsin='../../../java/opsin.jar'))
