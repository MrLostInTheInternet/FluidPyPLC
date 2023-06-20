import datetime
import uuid
import pkg_resources
import json


class LD():
    def __init__(self):
        self.run()
    
    def run(self):
        date = datetime.datetime.now()

        date_str = str(date)
        date_codesys = date_str.replace(" ", "T")
        # Change the name of the project based on yours
        project_name = ''

        config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
        try:
            with open(config_file_path) as f:
                config = json.load(f)
                path = config["folder_path"]
        except Exception as e:
            print(e)


        with open(path + "output" + date.strftime("%M") + ".xml", "w") as output:
            output.write('<?xml version="1.0" encoding="utf-8"?>\n')
            output.write('<project xmlns="http://www.plcopen.org/xml/tc6_0200">\n')
            output.write(f'\t<fileHeader companyName="" productName="CODESYS" productVersion="CODESYS V3.5 SP19" creationDateTime="{date_codesys}" />\n')
            output.write(f'\t<contentHeader name="{project_name}" modificationDateTime="{date_codesys}">\n')
            output.write('\t\t<coordinateInfo>\n')
            output.write('\t\t\t<fbd>\n')
            output.write('\t\t\t\t<scaling x="1" y="1" />\n')
            output.write('\t\t\t</fbd>\n')
            output.write('\t\t\t<ld>\n')
            output.write('\t\t\t\t<scaling x="1" y="1" />\n')
            output.write('\t\t\t</ld>\n')
            output.write('\t\t\t<sfc>\n')
            output.write('\t\t\t\t<scaling x="1" y="1" />\n')
            output.write('\t\t\t</sfc>\n')
            output.write('\t\t</coordinateInfo>\n')
            output.write('\t\t<addData>\n')
            output.write('\t\t\t<data name="http://www.3s-software.com/plcopenxml/projectinformation" handleUnknown="implementation">\n')
            output.write('\t\t\t\t<ProjectInformation />\n')
            output.write('\t\t\t\t</data>\n')
            output.write('\t\t\t</addData>\n')
            output.write('\t</contentHeader>\n')
            output.write('\t<types>\n')
            output.write('\t\t<dataTypes />\n')
            output.write('\t\t<pous>\n')
            output.write(f'\t\t\t<pou name="PLC_PRG_{date.strftime("%M")}" pouType="program">\n')
            output.write('\t\t\t\t<interface>\n')
            output.write('\t\t\t\t\t<localVars>\n')
            output.write('\t\t\t\t\t</localVars>\n')
            output.write('\t\t\t\t</interface>\n')
            output.write('\t\t\t\t<body>\n')
            output.write('\t\t\t\t\t<LD>\n')
            output.write('\t\t\t\t\t\t<leftPowerRail localId="0">\n')
            output.write('\t\t\t\t\t\t\t<position x="0" y="0" />\n')
            output.write('\t\t\t\t\t\t\t<connectionPointOut formalParameter="none" />\n')
            output.write('\t\t\t\t\t\t</leftPowerRail>\n')

        def delete_lines_from_end(file_path, line_index):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            # Determine the range of lines to delete
            start_index = line_index
            end_index = len(lines)

            with open(file_path, 'w') as file:
                for i, line in enumerate(lines):
                    if i < start_index or i >= end_index:
                        file.write(line)

        try:
            delete_lines_from_end(path + "output" + date.strftime("%M") + ".xml", 35)
        except Exception as e:
            print(e)

        with open(path + "/plc/plc.st", 'r') as f:
            lines = f.readlines()
            index = 0
            for line in lines:
                words = line.split()
                index += 1
                if "IF" in line:
                    break

            d_i = 3 # default indentation
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
                words = line.split()    # array of words in the line
                string_line = line.rstrip()    # string of words in the line
                indentation = string_line[:len(string_line) - len(string_line.lstrip())]     # Indentation of the line

                match indentation:
                    case "\t":     # if one indentation, then I need to concatenate the next contacts or relays to the localID of the last contact at the start of the block
                        concatenation_EB = True
                        if "END_IF" in words:
                            concatenation_AB = False
                    case "\t\t":     # if two indentations, then I need to concatenate the next coils to the localID of the previous contact
                        concatenation_AB = True
                        var_localID_AB = localID - 1
                # each space means new network
                if line == "\n":
                    with open(path + "output" + date.strftime("%M") + ".xml",'a') as output:
                        output.write(f'<comment localId="{localID}" height="0" width="0">\n' + '\t'*d_i)
                        localID += 1
                        output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                        output.write('\t<content>\n' + '\t'*d_i)
                        output.write('\t\t<xhtml xmlns="http://www.w3.org/1999/xhtml" />\n' + '\t'*d_i)
                        output.write('\t</content>\n' + '\t'*d_i)
                        output.write('</comment>\n' + '\t'*d_i)
                        output.write(f'<vendorElement localId="{localID}">\n' + '\t'*d_i)
                        localID += 1
                        output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                        output.write('\t\t<alternativeText>\n' + '\t'*d_i)
                        output.write('\t\t\t<xhtml xmlns="http://www.w3.org/1999/xhtml" />\n' + '\t'*d_i)
                        output.write('\t\t</alternativeText>\n' + '\t'*d_i)
                        output.write('\t<addData>\n' + '\t'*d_i)
                        output.write('\t\t<data name="http://www.3s-software.com/plcopenxml/fbdelementtype" handleUnknown="implementation">\n' + '\t'*d_i)
                        output.write('\t\t\t<ElementType xmlns="">networktitle</ElementType>\n' + '\t'*d_i)
                        output.write('\t\t</data>\n' + '\t'*d_i)
                        output.write('\t</addData>\n' + '\t'*d_i)
                        output.write('</vendorElement>\n' + '\t'*d_i)
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
                                    with open(path + "output" + date.strftime("%M") + ".xml", "a") as output:
                                        output.write(f'<coil localId="{localID}" negated="false" storage="set">\n' + '\t'*d_i)
                                        output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                                        output.write('\t<connectionPointIn>\n' + '\t'*d_i)
                                        if concatenation_AB:
                                            refLocalID = var_localID_AB
                                        output.write(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t'*d_i)
                                        refLocalID = localID
                                        localID += 1
                                        output.write('\t</connectionPointIn>\n' + '\t'*d_i)
                                        output.write('\t<connectionPointOut />\n' + '\t'*d_i)
                                        output.write(f'\t<variable>{word}</variable>\n' + '\t'*d_i)
                                        output.write('</coil>\n' + '\t'*d_i)
                                        break
                                elif "FALSE" in words[-1]:
                                    with open(path + "output" + date.strftime("%M") + ".xml", "a") as output:
                                        output.write(f'<coil localId="{localID}" negated="false" storage="reset">\n' + '\t'*d_i)
                                        output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                                        output.write('\t<connectionPointIn>\n' + '\t'*d_i)
                                        if concatenation_AB:
                                            refLocalID = var_localID_AB
                                        output.write(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t'*d_i)
                                        refLocalID = localID
                                        localID += 1
                                        output.write('\t</connectionPointIn>\n' + '\t'*d_i)
                                        output.write('\t<connectionPointOut />\n' + '\t'*d_i)
                                        output.write(f'\t<variable>{word}</variable>\n' + '\t'*d_i)
                                        output.write('</coil>\n' + '\t'*d_i)
                                        break
                            except:
                                None

                            with open(path + "output" + date.strftime("%M") + ".xml",'a') as output:
                                output.write(f'<contact localId="{localID}" negated="{Bool}" storage="none">\n' + '\t'*d_i)
                                output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                                output.write('\t<connectionPointIn>\n' + '\t'*d_i)
                                if concatenation_EB:
                                    refLocalID = var_localID - 1
                                output.write(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t'*d_i)
                                refLocalID = localID
                                localID += 1
                                output.write('\t</connectionPointIn>\n' + '\t'*d_i)
                                output.write('\t<connectionPointOut />\n' + '\t'*d_i)
                                output.write(f'\t<variable>{word}</variable>\n' + '\t'*d_i)
                                output.write('</contact>\n' + '\t'*d_i)
                    match word[:2]:
                        case "EB":
                            deactivation = False
                            match words[i - 1]:
                                case "NOT":
                                    Bool = "true"
                                case _:
                                    Bool = "false"
                            with open(path + "output" + date.strftime("%M") + ".xml",'a') as output:
                                output.write(f'<contact localId="{localID}" negated="{Bool}" storage="none" edge="none">\n' + '\t'*d_i)
                                output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                                output.write('\t<connectionPointIn>\n' + '\t'*d_i)
                                if concatenation_EB:
                                    refLocalID = var_localID - 1
                                output.write(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t'*d_i)
                                refLocalID = localID
                                localID += 1
                                output.write('\t</connectionPointIn>\n' + '\t'*d_i)
                                output.write('\t<connectionPointOut />\n' + '\t'*d_i)
                                output.write(f'\t<variable>{word}</variable>\n' + '\t'*d_i)
                                output.write('</contact>\n' + '\t'*d_i)
                        case "AB":
                            if deactivation:
                                set_or_reset = "reset"
                            else:
                                set_or_reset = "set"
                            with open(path + "output" + date.strftime("%M") + ".xml",'a') as output:
                                output.write(f'<coil localId="{localID}" negated="false" storage="{set_or_reset}">\n' + '\t'*d_i)
                                output.write('\t<position x="0" y="0" />\n' + '\t'*d_i)
                                output.write('\t<connectionPointIn>\n' + '\t'*d_i)
                                if concatenation_AB:
                                    refLocalID = var_localID_AB
                                elif concatenation_EB and not concatenation_AB:
                                    refLocalID = var_localID - 1
                                output.write(f'\t\t<connection refLocalId="{refLocalID}" />\n' + '\t'*d_i)
                                refLocalID = localID
                                localID += 1
                                output.write('\t</connectionPointIn>\n' + '\t'*d_i)
                                output.write('\t<connectionPointOut />\n' + '\t'*d_i)
                                output.write(f'\t<variable>{word}</variable>\n' + '\t'*d_i)
                                output.write('</coil>\n' + '\t'*d_i)
                match indentation:
                    case "":     # if no indentation, then it means it is the start of the block, and I need to store the localID of the last contact
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

        with open(path + "output" + date.strftime("%M") + ".xml", "a") as output:
            output.write('<rightPowerRail localId="2147483646">\n')
            output.write('<position x="0" y="0" />\n')
            output.write('<connectionPointIn />\n')
            output.write('</rightPowerRail>\n')
            output.write('</LD>\n')
            output.write('</body>\n')
            output.write('<addData>\n')
            output.write('<data name="http://www.3s-software.com/plcopenxml/objectid" handleUnknown="discard">\n')
            output.write(f'<ObjectId>{objectID}</ObjectId>\n')
            output.write('</data>\n')
            output.write('</addData>\n')
            output.write('</pou>\n')
            output.write('</pous>\n')
            output.write('</types>\n')
            output.write('<instances>\n')
            output.write('<configurations />\n')
            output.write('</instances>\n')
            output.write('<addData>\n')
            output.write('<data name="http://www.3s-software.com/plcopenxml/projectstructure" handleUnknown="discard">\n')
            output.write('<ProjectStructure>\n')
            output.write(f'<Object Name="PLC_PRG_{date.strftime("%M")}" ObjectId="{objectID}" />\n')
            output.write('</ProjectStructure>\n')
            output.write('</data>\n')
            output.write('</addData>\n')
            output.write('</project>\n')

        self.output = 'output' + date.strftime("%M")