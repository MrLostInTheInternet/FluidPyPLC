import datetime
import uuid
import pkg_resources
import json

class LD:
    def __init__(self):
        self.run()

    def run(self):
        date = datetime.datetime.now()
        date_codesys = date.strftime("%Y-%m-%dT%H:%M:%S")
        project_name = ''

        config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
        try:
            with open(config_file_path) as f:
                config = json.load(f)
                path = config["folder_path"]
        except Exception as e:
            print(e)

        xml_file_path = path + "output" + date.strftime("%M") + ".xml"
        
        def write_xml_lines(lines):
            with open(xml_file_path, "w") as output:
                output.writelines(lines)

        xml_lines = [
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<project xmlns="http://www.plcopen.org/xml/tc6_0200">\n',
            f'\t<fileHeader companyName="" productName="CODESYS" productVersion="CODESYS V3.5 SP19" creationDateTime="{date_codesys}" />\n',
            f'\t<contentHeader name="{project_name}" modificationDateTime="{date_codesys}">\n',
            '\t\t<coordinateInfo>\n',
            '\t\t\t<fbd>\n',
            '\t\t\t\t<scaling x="1" y="1" />\n',
            '\t\t\t</fbd>\n',
            '\t\t\t<ld>\n',
            '\t\t\t\t<scaling x="1" y="1" />\n',
            '\t\t\t</ld>\n',
            '\t\t\t<sfc>\n',
            '\t\t\t\t<scaling x="1" y="1" />\n',
            '\t\t\t</sfc>\n',
            '\t\t</coordinateInfo>\n',
            '\t\t<addData>\n',
            '\t\t\t<data name="http://www.3s-software.com/plcopenxml/projectinformation" handleUnknown="implementation">\n',
            '\t\t\t\t<ProjectInformation />\n',
            '\t\t\t\t</data>\n',
            '\t\t\t</addData>\n',
            '\t</contentHeader>\n',
            '\t<types>\n',
            '\t\t<dataTypes />\n',
            '\t\t<pous>\n',
            f'\t\t\t<pou name="PLC_PRG_{date.strftime("%M")}" pouType="program">\n',
            '\t\t\t\t<interface>\n',
            '\t\t\t\t\t<localVars>\n',
            '\t\t\t\t\t</localVars>\n',
            '\t\t\t\t</interface>\n',
            '\t\t\t\t<body>\n',
            '\t\t\t\t\t<LD>\n',
            '\t\t\t\t\t\t<leftPowerRail localId="0">\n',
            '\t\t\t\t\t\t\t<position x="0" y="0" />\n',
            '\t\t\t\t\t\t\t<connectionPointOut formalParameter="none" />\n',
            '\t\t\t\t\t\t</leftPowerRail>\n',
        ]

        def delete_lines_from_end(file_path, line_index):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            # Determine the range of lines to delete
            start_index = line_index
            end_index = len(lines)

            with open(file_path, 'w') as file:
                file.writelines(lines[:start_index])

        try:
            delete_lines_from_end(xml_file_path, 35)
        except Exception as e:
            print(e)

        with open(path + "/plc/plc.st", 'r') as f:
            lines = f.readlines()
            index = 0
            for line in lines:
                index += 1
                if "IF" in line:
                    break

            d_i = 3  # default indentation
            localID = 1
            refLocalID = 0
            Bool = ''
            concatenation_EB = False
            var_localID_AB = 0
            var_localID_EB = 0
            var_localID = 0
            concatenation_AB = False
            deactivation = False
            set_or_reset = 'set'
            # i have to read each line from the first block
            for line in lines[index:]:
                words = line.split()  # array of words in the line
                string_line = line.rstrip()  # string of words in the line
                indentation = string_line[:len(string_line) - len(string_line.lstrip())]  # Indentation of the line

                match indentation:
                    case "\t":  # if one indentation, then I need to concatenate the next contacts or relays to the localID of the last contact at the start of the block
                        concatenation_EB = True
                        if "END_IF" in words:
                            concatenation_AB = False
                    case "\t\t":  # if two indentations, then I need to concatenate the next coils to the localID of the previous contact
                        concatenation_AB = True
                        var_localID_AB = localID - 1
                # each space means new network
                if line == "\n":
                    xml_lines.extend([
                        f'<comment localId="{localID}" height="0" width="0">\n' + '\t' * d_i,
                        '\t<position x="0" y="0" />\n' + '\t' * d_i,
                        '\t<content>\n' + '\t' * d_i,
                        '\t\t<xhtml xmlns="http://www.w3.org/1999/xhtml" />\n' + '\t' * d_i,
                        '\t</content>\n' + '\t' * d_i,
                        '</comment>\n' + '\t' * d_i,
                        f'<vendorElement localId="{localID}">\n' + '\t' * d_i,
                        '\t<position x="0" y="0" />\n' + '\t' * d_i,
                        '\t\t<alternativeText>\n' + '\t' * d_i,
                        '\t\t\t<xhtml xmlns="http://www.w3.org/1999/xhtml" />\n' + '\t' * d_i,
                        '\t\t</alternativeText>\n' + '\t' * d_i,
                        '\t<addData>\n' + '\t' * d_i,
                        '\t\t<data name="http://www.3s-software.com/plcopenxml/fbdelementtype" handleUnknown="implementation">\n' + '\t' * d_i,
                        '\t\t\t<ElementType xmlns="">networktitle</ElementType>\n' + '\t' * d_i,
                        '\t\t</data>\n' + '\t' * d_i,
                        '\t</addData>\n' + '\t' * d_i,
                        '</vendorElement>\n' + '\t' * d_i,
                    ])
                    refLocalID = 0
                # ------------------ New Network created ------------------

                # analyze each word in each line
                for i, word in enumerate(words):
                    match word[:1]:
                        case 'K':
                            # Case Relay Memory K0, K1, etc..
                            match words[i - 1]:
                                case "NOT":
                                    # If NOT before e.g. K0, then i need the contact to be closed
                                    Bool = "true"
                                    if words[i - 2] == "IF":
                                        deactivation = True
                                case _:
                                    if words[i - 1] == "IF":
                                        deactivation = True
                                    # else open
                                    Bool = "false"
                            try:
                                if "TRUE" in words[-1]:
                                    xml_lines.extend([
                                        f'<coil localId="{localID}" negated="false" storage="set">\n' + '\t' * d_i,
                                        '\t<position x="0" y="0" />\n' + '\t' * d_i,
                                        '\t<connectionPointIn>\n' + '\t' * d_i,
                                    ])
                                    if concatenation_AB:
                                        refLocalID = var_localID_AB
                                    xml_lines.append(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t' * d_i)
                                    refLocalID = localID
                                    localID += 1
                                    xml_lines.extend([
                                        '\t</connectionPointIn>\n' + '\t' * d_i,
                                        '\t<connectionPointOut />\n' + '\t' * d_i,
                                        f'\t<variable>{word}</variable>\n' + '\t' * d_i,
                                        '</coil>\n' + '\t' * d_i,
                                    ])
                                    break
                                elif "FALSE" in words[-1]:
                                    xml_lines.extend([
                                        f'<coil localId="{localID}" negated="false" storage="reset">\n' + '\t' * d_i,
                                        '\t<position x="0" y="0" />\n' + '\t' * d_i,
                                        '\t<connectionPointIn>\n' + '\t' * d_i,
                                    ])
                                    if concatenation_AB:
                                        refLocalID = var_localID_AB
                                    xml_lines.append(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t' * d_i)
                                    refLocalID = localID
                                    localID += 1
                                    xml_lines.extend([
                                        '\t</connectionPointIn>\n' + '\t' * d_i,
                                        '\t<connectionPointOut />\n' + '\t' * d_i,
                                        f'\t<variable>{word}</variable>\n' + '\t' * d_i,
                                        '</coil>\n' + '\t' * d_i,
                                    ])
                                    break
                            except:
                                None

                            xml_lines.extend([
                                f'<contact localId="{localID}" negated="{Bool}" storage="none">\n' + '\t' * d_i,
                                '\t<position x="0" y="0" />\n' + '\t' * d_i,
                                '\t<connectionPointIn>\n' + '\t' * d_i,
                            ])
                            if concatenation_EB:
                                refLocalID = var_localID - 1
                            xml_lines.append(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t' * d_i)
                            refLocalID = localID
                            localID += 1
                            xml_lines.extend([
                                '\t</connectionPointIn>\n' + '\t' * d_i,
                                '\t<connectionPointOut />\n' + '\t' * d_i,
                                f'\t<variable>{word}</variable>\n' + '\t' * d_i,
                                '</contact>\n' + '\t' * d_i,
                            ])
                    match word[:2]:
                        case "EB":
                            deactivation = False
                            match words[i - 1]:
                                case "NOT":
                                    Bool = "true"
                                case _:
                                    Bool = "false"
                            xml_lines.extend([
                                f'<contact localId="{localID}" negated="{Bool}" storage="none" edge="none">\n' + '\t' * d_i,
                                '\t<position x="0" y="0" />\n' + '\t' * d_i,
                                '\t<connectionPointIn>\n' + '\t' * d_i,
                            ])
                            if concatenation_EB:
                                refLocalID = var_localID - 1
                            xml_lines.append(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t' * d_i)
                            refLocalID = localID
                            localID += 1
                            xml_lines.extend([
                                '\t</connectionPointIn>\n' + '\t' * d_i,
                                '\t<connectionPointOut />\n' + '\t' * d_i,
                                f'\t<variable>{word}</variable>\n' + '\t' * d_i,
                                '</contact>\n' + '\t' * d_i,
                            ])
                        case "AB":
                            if deactivation:
                                set_or_reset = "reset"
                            else:
                                set_or_reset = "set"
                            xml_lines.extend([
                                f'<coil localId="{localID}" negated="false" storage="{set_or_reset}">\n' + '\t' * d_i,
                                '\t<position x="0" y="0" />\n' + '\t' * d_i,
                                '\t<connectionPointIn>\n' + '\t' * d_i,
                            ])
                            if concatenation_AB:
                                refLocalID = var_localID_AB
                            elif concatenation_EB and not concatenation_AB:
                                refLocalID = var_localID - 1
                            xml_lines.append(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t' * d_i)
                            refLocalID = localID
                            localID += 1
                            xml_lines.extend([
                                '\t</connectionPointIn>\n' + '\t' * d_i,
                                '\t<connectionPointOut />\n' + '\t' * d_i,
                                f'\t<variable>{word}</variable>\n' + '\t' * d_i,
                                '</coil>\n' + '\t' * d_i,
                            ])
                match indentation:
                    case "":  # if no indentation, then it means it is the start of the block, and I need to store the localID of the last contact
                        try:
                            if "THEN" in words[-1]:
                                var_localID = localID
                            if "END_IF;" in words:
                                concatenation_AB = False
                                concatenation_EB = False
                                deactivation = False
                        except:
                            None

        # Generate a UUID
        new_uuid = uuid.uuid4()

        # Convert the UUID to a string in the desired format
        objectID = str(new_uuid)

        xml_lines.extend([
            '<rightPowerRail localId="2147483646">\n',
            '<position x="0" y="0" />\n',
            '<connectionPointIn />\n',
            '</rightPowerRail>\n',
            '</LD>\n',
            '</body>\n',
            '<addData>\n',
            '<data name="http://www.3s-software.com/plcopenxml/objectid" handleUnknown="discard">\n',
            f'<ObjectId>{objectID}</ObjectId>\n',
            '</data>\n',
            '</addData>\n',
            '</pou>\n',
            '</pous>\n',
            '</types>\n',
            '<instances>\n',
            '<configurations />\n',
            '</instances>\n',
            '<addData>\n',
            '<data name="http://www.3s-software.com/plcopenxml/projectstructure" handleUnknown="discard">\n',
            '<ProjectStructure>\n',
            f'<Object Name="PLC_PRG_{date.strftime("%M")}" ObjectId="{objectID}" />\n',
            '</ProjectStructure>\n',
            '</data>\n',
            '</addData>\n',
            '</project>\n',
        ])

        write_xml_lines(xml_lines)
        self.output = 'output' + date.strftime("%M")
