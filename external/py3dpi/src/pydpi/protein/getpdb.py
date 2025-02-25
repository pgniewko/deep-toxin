# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:18:26 2013

This module is used for downloading the PDB file from RCSB PDB web and 

extract its amino acid sequence.

This is written by Dongsheng Cao

@author: Dongsheng Cao
"""

import os, ftplib, gzip

HOSTNAME = "ftp.wwpdb.org"
DIRECTORY = "/pub/pdb/data/structures/all/pdb/"
PREFIX = "pdb"
SUFFIX = ".ent.gz"

# List of three and one letter amino acid codes
_aa_index = [
    ("ALA", "A"),
    ("CYS", "C"),
    ("ASP", "D"),
    ("GLU", "E"),
    ("PHE", "F"),
    ("GLY", "G"),
    ("HIS", "H"),
    ("HSE", "H"),
    ("HSD", "H"),
    ("ILE", "I"),
    ("LYS", "K"),
    ("LEU", "L"),
    ("MET", "M"),
    ("MSE", "M"),
    ("ASN", "N"),
    ("PRO", "P"),
    ("GLN", "Q"),
    ("ARG", "R"),
    ("SER", "S"),
    ("THR", "T"),
    ("VAL", "V"),
    ("TRP", "W"),
    ("TYR", "Y"),
]

# AA3_TO_AA1 = dict(_aa_index)
# AA1_TO_AA3 = dict([(aa[1],aa[0]) for aa in _aa_index])


def unZip(some_file, some_output):
    """
    Unzip some_file using the gzip library and write to some_output.
    """

    f = gzip.open(some_file, "r")
    g = open(some_output, "w")
    g.writelines(f.readlines())
    f.close()
    g.close()

    os.remove(some_file)


def pdbDownload(
    file_list, hostname=HOSTNAME, directory=DIRECTORY, prefix=PREFIX, suffix=SUFFIX
):
    """
    Download all pdb files in file_list and unzip them.
    """

    success = True

    # Log into server
    print("Connecting...")
    ftp = ftplib.FTP()
    ftp.connect(hostname)
    ftp.login()

    # Remove .pdb extensions from file_list
    for file_index, file in enumerate(file_list):
        try:
            file_list[file_index] = file[: file.index(".pdb")]
        except ValueError:
            pass

    # Download all files in file_list
    to_get = ["%s/%s%s%s" % (directory, prefix, f, suffix) for f in file_list]
    to_write = ["%s%s" % (f, suffix) for f in file_list]
    for i in range(len(to_get)):
        try:
            ftp.retrbinary("RETR %s" % to_get[i], open(to_write[i], "wb").write)
            final_name = "%s.pdb" % to_write[i][: to_write[i].index(".")]
            unZip(to_write[i], final_name)
            print("%s retrieved successfully." % final_name)
        except ftplib.error_perm:
            os.remove(to_write[i])
            print("ERROR!  %s could not be retrieved!" % file_list[i])
            success = False

    # Log out
    ftp.quit()

    if success:
        return True
    else:
        return False


def GetPDB(pdbidlist=[]):

    """
    Download the PDB file from PDB FTP server by providing a list of pdb id.
    """

    for i in pdbidlist:
        templist = []
        templist.append(i)
        pdbDownload(templist)

    return True


def pdbSeq(pdb, use_atoms=False):
    """
    Parse the SEQRES entries in a pdb file.  If this fails, use the ATOM
    entries.  Return dictionary of sequences keyed to chain and type of
    sequence used.
    """

    # Try using SEQRES
    seq = [l for l in pdb if l[0:6] == "SEQRES"]
    if len(seq) != 0 and not use_atoms:
        seq_type = "SEQRES"
        chain_dict = dict([(l[11], []) for l in seq])
        for c in list(chain_dict.keys()):
            chain_seq = [l[19:70].split() for l in seq if l[11] == c]
            for x in chain_seq:
                chain_dict[c].extend(x)

    # Otherwise, use ATOM
    else:

        seq_type = "ATOM  "

        # Check to see if there are multiple models.  If there are, only look
        # at the first model.
        models = [i for i, l in enumerate(pdb) if l.startswith("MODEL")]
        if len(models) > 1:
            pdb = pdb[models[0] : models[1]]

        # Grab all CA from ATOM entries, as well as MSE from HETATM
        atoms = []
        for l in pdb:
            if l[0:6] == "ATOM  " and l[13:16] == "CA ":

                # Check to see if this is a second conformation of the previous
                # atom
                if len(atoms) != 0:
                    if atoms[-1][17:26] == l[17:26]:
                        continue

                atoms.append(l)
            elif l[0:6] == "HETATM" and l[13:16] == "CA " and l[17:20] == "MSE":

                # Check to see if this is a second conformation of the previous
                # atom
                if len(atoms) != 0:
                    if atoms[-1][17:26] == l[17:26]:
                        continue

                atoms.append(l)

        chain_dict = dict([(l[21], []) for l in atoms])
        for c in list(chain_dict.keys()):
            chain_dict[c] = [l[17:20] for l in atoms if l[21] == c]

    AA3_TO_AA1 = dict(_aa_index)
    tempchain = list(chain_dict.keys())
    tempchain.sort()
    seq = ""
    for i in tempchain:
        for j in chain_dict[i]:
            if j in list(AA3_TO_AA1.keys()):
                seq = seq + (AA3_TO_AA1[j])
            else:
                seq = seq + ("X")

    return seq, seq_type


def GetSeqFromPDB(pdbfile=""):
    """
    Get the amino acids sequences from pdb file.
    """
    f1 = file(pdbfile, "r")
    res1, res2 = pdbSeq(f1)
    f1.close()
    return res1


def _GetHTMLDoc():
    """
    #################################################################
    Write HTML documentation for this module.
    #################################################################
    """
    import pydoc

    pydoc.writedoc("getpdb")


####################################################################
if __name__ == "__main__":

    GetPDB(["1atp", "1efz", "1f88"])

    seq = GetSeqFromPDB("1atp.pdb")
    print(seq)
