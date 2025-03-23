"""
Writes a PHOTON.dat to filter the isotopes in the R2SUNED calculation. Only the isotopes
present in the file will be taken into account.

#PHOTON.dat format example
100  FM257        13
 43  TC 97M        1
 99  ES256M        3
 13  AL 26M        3
  4  BE  7         1
  5   B 12         1
 ...

For each isotope there are two lines. The first word is the atomic number, then the
element name, then the mass number which may include as last character an 'm' or 'n',
the last word of the line is a '1' representing the number of gamma lines for that
nuclide.
The second line is always a ' 1   1' which means a gamma energy of 1 and a probability
of 1 for that energy. We use this artificial data as we are not interested in the gamma
energies or probabilities, just in the activity of each isotope.
"""
from typing import List
import json
import periodictable as pt
import re


def write_photon_dat_file(isotopes: List[str]):
    """Receives a list with all the relevant isotopes and writes a PHOTON.dat file that
     will include only them.

    The isotopes list items are strings with the format: Re186m, the final 'm' character
    is optional to represent an isomer, in some instances there may be more than an
    isomer using other chars like 'n'.
    """
    with open("PHOTON.dat", "w") as infile:
        for isotope in isotopes:  # isotope example: Re186m
            element_name = re.match(r"[a-z]+", isotope, re.IGNORECASE).group()
            # This atomic number may include the m char
            mass_number = re.search(r"\d+[a-zA-Z]?", isotope).group()
            mass_number = mass_number.upper()  # The m character must be uppercase
            atom_number = pt.elements.isotope(element_name).number
            # In the case where there is an M or N in the mass number we need to do a
            # weird formatting to avoid a crash, it doesnt have much sense but it works
            if "M" in mass_number or "N" in mass_number:
                infile.write(
                    f"{atom_number:>3}{element_name.upper():>4}{mass_number:>4}{1:>9}\n"
                )
                infile.write(f"{1:11.4E}{1:11.4E}\n")
            else:
                infile.write(
                    f"{atom_number:>3}{element_name.upper():>4}{mass_number:>3}{1:>10}\n"
                )
                infile.write(f"{1:11.4E}{1:11.4E}\n")
    # WARNING: the end of the file should not have more than one blank line
    return


if __name__ == "__main__":
    with open("criteria.json", "r") as criteria_file:
        criteria = json.load(criteria_file)  # e.g. criteria = {'H3': [...], 'Be10':...}
    # It seems that the R2SUNED code does not recognize the isomer BI207M, we exclude it
    # here to avoid crashes
    criteria.pop("Bi207m")
    _isotopes = criteria.keys()  # _isotopes = ['H3', 'Be10', ...]
    write_photon_dat_file(_isotopes)
    """
    100  FM257        13
     43  TC 97M        1
     43  TC97M         1 BAD
     99  ES256M        3
     13  AL 26M        3
      4  BE  7         1
      5   B 12         1
    """
