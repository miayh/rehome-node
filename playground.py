import sys
import os
import re


def create_cmds_file(src_name):
    """
    Creates a file for calling the functions to retrieve information about a certain unit.

    Args:
    - src_name: The name of the MO that the new MO will be based on when created in 
                the new node (e.g. "SectorCarrier=5")
    """
    create_file_cmd = 'touch cmds_2.mos'
    os.system(create_file_cmd)
    content = ''
    if src_name:
        if re.match(r'[Ff]ield[Rr]eplaceable[Uu]nit', src_name):
            content += "getRadioInfo radioCreation.mos FieldReplaceableUnit=R\n"
        elif re.match(r'[Rr]ilink', src_name):
            content += "getRiLinkInfo rilinkCreation.mos RiLink\n"
        elif re.match(r'[Aa]ntenna', src_name):
            content += "getAntennaInfo antennaCreation.mos AntennaUnitGroup\n"
        elif re.match(r'[Ss]ectorEquipment', src_name):
            content += "getSectorInfo sectorCreation.mos SectorEquipment\n"
        elif re.match(r'[Ss]ector[Cc]arrier', src_name):
            content += "getCarrierInfo carrierCreation.mos SectorCarrier\n"
        elif re.match(r'[Cc]ell', src_name):
            content += "getCellInfo cellCreation.mos Cell\n"
    else: 
        content = "getRadioInfo radioCreation.mos FieldReplaceableUnit=R\n" \
                  "getRiLinkInfo rilinkCreation.mos RiLink\n" \
                  "getAntennaInfo antennaCreation.mos AntennaUnitGroup\n" \
                  "getSectorInfo sectorCreation.mos SectorEquipment\n" \
                  "getCarrierInfo carrierCreation.mos SectorCarrier\n" \
                  "getCellInfo cellCreation.mos Cell"
    with open('cmds_2.mos', 'w') as file:
        file.write(content)

if __name__ == '__main__':
    create_cmds_file(sys.argv[1])