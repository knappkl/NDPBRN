import pandas as pds
import logging
import os
import collections
from datetime import datetime
from load_resources import curr_dir, ohd_ttl, label2uri, load_ada_filling_material_map, load_ada_endodontic_material_map, \
    load_ada_inlay_material_map, load_ada_onlay_material_map, load_ada_procedure_map, load_ada_apicoectomy_material_map, \
    load_ada_root_amputation_material_map, load_ada_crown_material_map, load_ada_pontic_material_map, load_ada_extraction_material_map, \
    load_ada_oral_evaluation_material_map
from src.util.ohd_label2uri import get_date_str, get_visit_id_suffix_with_date_str

restored_tooth_surface_label_map = {'b': 'restored buccal surface',
                                    'd': 'restored distal surface',
                                    'i': 'restored incisal surface',
                                    'f': 'restored labial surface',
                                    'l': 'restored lingual surface',
                                    'm': 'restored mesial surface',
                                    'o': 'restored occlusal surface'
                                    }


def print_procedure_ttl(practice_id='1', input_f='Patient_History.txt',
                        output_p='./',
                        print_ttl=True, save_ttl=True, procedure_type=1, vendor='ES'):

#    df_path = os.path.join(curr_dir, '..', 'data', 'Practice1_Fillings.xlsx')
    #df_path = os.path.join(curr_dir, '..', 'data', 'Practice1_Patient_History.xlsx')
    #df_path = os.path.join(curr_dir, '..', 'data', 'Practice' + str(practice_id) + '_Patient_History.xlsx')
    #df_path = os.path.join(curr_dir, '..', 'data', 'Practice' + str(practice_id) + '_Patient_History.txt')
    df_path = input_f
    #df = pds.ExcelFile(df_path).parse()
    #patient_id	birth_date	sex	table_name	date_completed	date_entered	tran_date	description	tooth	surface	action_code	action_code_description	service_code	ada_code	ada_code_description	tooth_data	surface_detail	provider_id	db_practice_id
    if vendor == 'ES':
        df = pds.read_csv(df_path, sep='\t',
                      names=["patient_id", "birth_date", "sex", "table_name", "date_completed", "date_entered", "tran_date", "description", "tooth", "surface", "action_code", "action_code_description",
                             "service_code", "ada_code", "ada_code_description", "tooth_data", "surface_detail", "provider_id", "db_practice_id"],
                      header=0)
    else:
        #df = pds.read_csv(df_path, sep='\t',
        #              names=["PBRN_PRACTICE", "LOG_ID", "PATIENT_ID", "patient_status", "BIRTH_DATE", "SEX", "TABLE_NAME",
        #                     "DATE_COMPLETED", "DATE_ENTERED", "TRAN_DATE", "DESCRIPTION", "TOOTH", "toothrangestart",
        #                     "toothrangeend", "SURFACE", "surfm", "surfo", "surfd", "surfl", "surff", "surf5", "ACTION_CODE",
        #                     "ACTION_CODE_DESCRIPTION", "SERVICE_CODE", "ADA_CODE", "ADA_CODE_DESCRIPTION", "PROVIDER_ID",
        #                     "chartstatus", "DB_PRACTICE_ID"],
        #                      header=0)
         df = pds.read_csv(df_path, sep='\t',
                        names=['PBRN_PRACTICE', 'LOG_ID', 'PATIENT_ID', 'BIRTH_DATE', 'SEX',
                                'TABLE_NAME', 'DATE_COMPLETED', 'DATE_ENTERED', 'TRAN_DATE',
                                'DESCRIPTION', 'TOOTH', 'SURFACE', 'ACTION_CODE', 'ACTION_CODE_DESCRIPTION', 'SERVICE_CODE',
                                'ADA_CODE', 'ADA_CODE_DESCRIPTION', 'TOOTH_DATA', 'surface_detail', 'PROVIDER_ID', 'DB_PRACTICE_ID'], header=0)

#patient_df = df[['PBRN_PRACTICE', 'DB_PRACTICE_ID', 'PATIENT_ID', 'TOOTH', 'SURFACE', 'TRAN_DATE', 'ADA_CODE', 'PROVIDER_ID', 'TABLE_NAME']]
    if vendor != 'ES':
        df.columns = df.columns.str.lower()
    patient_df = df[['db_practice_id', 'patient_id', 'tooth', 'surface', 'tran_date', 'ada_code', 'provider_id', 'table_name', 'tooth_data']]

    procedure_type_map = {'1': 'filling',
                   '2': 'endodontic',
                   '3': 'inlays',
                   '4': 'onlays',
                   '5': 'apicoectomy',
                   '6':'root_amputation',
                   '7':'crown',
                   '8':'pontic',
                   '9':'surgic_tooth_extraction',
                   '10':'oral_evaluation'}

    surface_map = {'m': 'Mesial surface enamel of tooth',
                   'o': 'Occlusal surface enamel of tooth',
                   'b': 'Buccal surface enamel of tooth',
                   'd': 'Distal surface enamel of tooth',
                   'i': 'Incisal surface enamel of tooth',
                   'f': 'Labial surface enamel of tooth',
                   'l': 'Lingual surface enamel of tooth'}

    # filters on procedure_type by procedure_type_map and create filenames for ttl and err text file
    try:
        filename = output_p + procedure_type_map[str(procedure_type)] + '.ttl'
        err_filename = output_p + procedure_type_map[str(procedure_type)] + '_err.txt'
    except Exception as ex:  # invalid procedure_type: stop processing here
        print("Invalid procedure type: " + str(procedure_type))
        logging.exception("message")
        return

    with open(filename, 'w') as f:
        with open(err_filename, 'w') as f_err:
            # local function for printing and saving turtle output
            def output(value_str, print_ttl=print_ttl, save_ttl=save_ttl):
                if print_ttl == True: print value_str
                if save_ttl == True: f.write(value_str)

            def output_err(value_str):
                f_err.write(value_str)
                f_err.write('\n')

            if (vendor == 'ES'):
                practice_id = 'A_' + str(practice_id)
            else:
                practice_id = 'B_' + str(practice_id)

            # output prefixes for ttl file
            prefix_str = ohd_ttl['prefix'].format(practice_id=practice_id)
            output(prefix_str)

            #practiceidstring = 'NDPBRN ' + vendor + ' practice ' + str(practice_id)
            # if (vendor == 'ES'):
            #     vendorChar = 'A '
            # else:
            #     vendorChar = 'B '
            # practiceidstring = 'NDPBRN practice ' + vendorChar + str(practice_id)
            practiceidstring = 'NDPBRN practice ' + str(practice_id)
            # practice
            practice_uri = ohd_ttl['practice uri'].format(practice_id=practice_id)
            # define types
            practice_type = label2uri['dental health care organization']
            practice_label = "practice_" + str(practice_id)
            # delcare individuals
            output(ohd_ttl['declare practice'].format(uri=practice_uri, type=practice_type, label=practice_label,
                                                      practice_id_str=practiceidstring))

            # print ttl for each patient
            #for (idx, practiceId, locationId, pid, tooth_num, surface, p_date, ada_code, prov_id, tableName) in patient_df.itertuples():
            practiceId = practice_id
            for (idx, locationId, pid, tooth_num_in_file, surface, p_date, ada_code, prov_id, tableName, tooth_data) in patient_df.itertuples():
                if tableName.lower() == 'transactions':
                    ada_code = str(ada_code)
                    #sometimes it has 'D' in front of numbers, sometimes there's no D
                    #if not ada_code.startswith('D'):
                    #    ada_code = str('D') + ada_code
                    ##change to use last 4 digits of ada_code and add D in front:
                    ada_code = str('D') + ada_code[-4:]
                    if len(ada_code) != 5:
                        date_str = get_date_str(p_date)
                        if date_str == 'invalid date':
                            print("Problem procedure date for patient: " + str(pid) + " for practice: " + str(
                                practiceId) + " idex: " + str(idx))
                            output_err("Problem procedure date for patient: " + str(pid) + " for practice: " + str(
                                practiceId) + " idex: " + str(idx))

                        print("Problem ada_code for patient: " + str(pid) + " for practice: " + str(practiceId) + " ada_code: " + ada_code +  " idex: " + str(idx))
                        output_err("Problem ada_code for patient: " + str(pid) + " for practice: " + str(practiceId) + " ada_code: " + ada_code +  " idex: " + str(idx))

                        if date_str != 'invalid date':
                            cdt_code_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + str(
                                get_ada_code(ada_code, idx)) + "_" + date_str
                        else:
                            cdt_code_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + str(
                                get_ada_code(ada_code, idx)) + "_invalid_procedure_date_" + str(idx)
                        patient_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid)
                        patient_uri = ohd_ttl['patient uri by prefix'].format(patient_id=patient_id)
                        # restoration procedure
                        restoration_procedure_label = "restoration procedure on patient " + str(
                            pid) + " on " + date_str  # "restoration procedure on patient 1 on 2003-05-16"
                        # TODO: double check on this, if invalid ada_code, "specific procedure" points to "dental procedure"
                        specific_procedure = label2uri["dental procedure"].rsplit('/', 1)[-1]
                        restoration_procedure = ohd_ttl['declare restoration procedure'].format(cdt_code_id=cdt_code_id,
                                                                                                tooth_restoration_procedure=specific_procedure,
                                                                                                label=restoration_procedure_label,
                                                                                                practice_id_str=practiceidstring)

                        restoration_procedure_uri = "restoration_procedure:" + str(cdt_code_id)

                        locationId = int(locationId)
                        visit_id = str(practiceId) + "_" + str(locationId) + "_" + str(
                            pid) + "_" + get_visit_id_suffix_with_date_str(date_str, idx)

                        # uri
                        visit_uri = ohd_ttl['visit uri'].format(visit_id=visit_id)

                        # relation: procedure part of visit
                        procedure_visit_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                            uri1=restoration_procedure_uri,
                            uri2=visit_uri)

                        # relation: restoration procedure has specified input provider
                        provider_uri = ohd_ttl['provider uri by prefix'].format(
                            provider_id=str(practiceId) + "_" + str(locationId) + "_" + str(prov_id))
                        procedure_provider_relation_str = ohd_ttl['uri1 has specified input uri2'].format(
                            uri1=restoration_procedure_uri,
                            uri2=provider_uri)

                        # relation: restoration procedure has specified input patient
                        procedure_patient_relation_str = ohd_ttl['uri1 has specified input uri2'].format(
                            uri1=restoration_procedure_uri,
                            uri2=patient_uri)

                        # relation: cdt code is about restoration procedure
                        cdt_code_uri = "cdt_code:" + str(cdt_code_id)
                        cdt_code_procedure_relation_str = ohd_ttl['uri1 is about uri2'].format(
                            uri1=cdt_code_uri,
                            uri2=restoration_procedure_uri)

                        output(restoration_procedure)
                        output("\n")

                        output(procedure_visit_relation_str)
                        output("\n")

                        # procedure "occurence date" property
                        if date_str != 'invalid date':
                            output(
                                ohd_ttl['declare date property uri'].
                                    format(uri=restoration_procedure_uri,
                                           type=label2uri['occurrence date'].rsplit('/', 1)[-1],
                                           date=date_str))

                        output(procedure_provider_relation_str)
                        output("\n")

                        output(procedure_patient_relation_str)
                        output("\n")

                        output(cdt_code_procedure_relation_str)
                        output("\n")

                    else:
                        ## with valid ada_code, continue:
                        #refactor to use tooth column with one integer number (tooth_num) instead of calculating
                        #tooth_char = list(tooth_data)

                        #tooth_idx = 0;
                        #for (tooth_yn) in tooth_char:
                            #if tooth_yn.lower() == 'y':
                                #tooth_num = tooth_idx + 1
                        if pds.notnull(surface):
                            surface = surface.strip()

                        try:
                            date_str = get_date_str(p_date)
                            if date_str == 'invalid date':
                                print("Problem procedure date for patient: " + str(pid) + " for practice: " + str(practiceId) + " idex: " + str(idx))
                                output_err("Problem procedure date for patient: " + str(pid) + " for practice: " + str(practiceId) + " idex: " + str(idx))

                            locationId = int(locationId)
                            visit_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + get_visit_id_suffix_with_date_str(date_str, idx)

                            #uri
                            visit_uri = ohd_ttl['visit uri'].format(visit_id=visit_id)

                            # try/catch here for filter in filling procedures
                            try:
                                # filters on material for certain types of procedures that we are interested in
                                continue_flag_filter_with_procedure = False
                                no_material_flag = False
                                if str(procedure_type) == '1':  ## for filling
                                    try:
                                        load_ada_filling_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_filling:
                                        logging.exception("message")
                                elif str(procedure_type) == '2':  ## for endodontic
                                    try:
                                        load_ada_endodontic_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_endo:
                                        logging.exception("message")
                                elif str(procedure_type) == '3':  ## for inlays
                                    try:
                                        load_ada_inlay_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_in:
                                        logging.exception("message")
                                elif str(procedure_type) == '4':  ## for onlays
                                    try:
                                        load_ada_onlay_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_on:
                                        logging.exception("message")
                                elif str(procedure_type) == '5':  ## for apicoectomy
                                    try:
                                        load_ada_apicoectomy_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_api:
                                        logging.exception("message")
                                elif str(procedure_type) == '6':  ## for root amputation - no material
                                    no_material_flag = True
                                    try:
                                        load_ada_root_amputation_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_amp:
                                        logging.exception("message")
                                elif str(procedure_type) == '7':  ## for crown
                                    try:
                                        load_ada_crown_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_crown:
                                        logging.exception("message")
                                elif str(procedure_type) == '8':  ## for pontic
                                    try:
                                        load_ada_pontic_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_pontic:
                                        logging.exception("message")
                                elif str(procedure_type) == '9':  ## for surgic tooth extraction
                                    no_material_flag = True
                                    try:
                                        load_ada_extraction_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_extract:
                                        logging.exception("message")
                                elif str(procedure_type) == '10':  ## for oral evaluation
                                    no_material_flag = True
                                    try:
                                        load_ada_oral_evaluation_material_map[ada_code]
                                        continue_flag_filter_with_procedure = True
                                    except Exception as ex_oral:
                                        logging.exception("message")
                                else: #invalid procedure_type: stop processing here
                                    print("Invalid procedure type: " + str(procedure_type) + " for patient: " + str(pid) + " for practice: " + str(practiceId))
                                    output_err("Invalid procedure type: " + str(procedure_type) + " for patient: " + str(pid) + " for practice: " + str(practiceId))
                                    logging.exception("message")
                                    return

                                if continue_flag_filter_with_procedure:
                                    ## with right procedure type of ada_code
                                    if str(procedure_type) == '10':  ## for oral evaluation
                                        if date_str != 'invalid date':
                                            cdt_code_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + ada_code + "_" + date_str
                                        else:
                                            cdt_code_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + ada_code + "_invalid_procedure_date_" + str(idx)
                                        patient_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid)
                                        patient_uri = ohd_ttl['patient uri by prefix'].format(patient_id=patient_id)
                                        # restoration procedure
                                        restoration_procedure_label = "restoration procedure on patient " + str(pid) + " on "  + date_str  # "restoration procedure on patient 1 on 2003-05-16"
                                        specific_procedure = label2uri[load_ada_procedure_map[ada_code]].rsplit('/', 1)[-1]
                                        restoration_procedure = ohd_ttl['declare restoration procedure'].format(cdt_code_id=cdt_code_id,
                                                                                                                tooth_restoration_procedure=specific_procedure,
                                                                                                                label=restoration_procedure_label,
                                                                                                                practice_id_str=practiceidstring)
                                        # billing code
                                        billing_code_label = "billing code " + ada_code + " for procedure on " + date_str  # "billing code D2160 for procedure on 2003-05-16"
                                        billing_code = ohd_ttl['declare billing code'].format(cdt_code_id=cdt_code_id,
                                                                                              billing_code_for_restorative=
                                                                                              label2uri[
                                                                                                  ada_code.lower()].rsplit('/',
                                                                                                                           1)[
                                                                                                  -1],
                                                                                              label=billing_code_label,
                                                                                              practice_id_str=practiceidstring)

                                        restoration_procedure_uri = "restoration_procedure:" + str(cdt_code_id)

                                        # relation: procedure part of visit
                                        procedure_visit_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                                            uri1=restoration_procedure_uri,
                                            uri2=visit_uri)

                                        # relation: restoration procedure has specified input provider
                                        provider_uri = ohd_ttl['provider uri by prefix'].format(
                                            provider_id=str(practiceId) + "_" + str(locationId) + "_" + str(prov_id))
                                        procedure_provider_relation_str = ohd_ttl['uri1 has specified input uri2'].format(
                                            uri1=restoration_procedure_uri,
                                            uri2=provider_uri)

                                        # relation: restoration procedure has specified input patient
                                        procedure_patient_relation_str = ohd_ttl['uri1 has specified input uri2'].format(
                                            uri1=restoration_procedure_uri,
                                            uri2=patient_uri)

                                        # relation: cdt code is about restoration procedure
                                        cdt_code_uri = "cdt_code:" + str(cdt_code_id)
                                        cdt_code_procedure_relation_str = ohd_ttl['uri1 is about uri2'].format(
                                            uri1=cdt_code_uri,
                                            uri2=restoration_procedure_uri)

                                        output(restoration_procedure)
                                        output("\n")

                                        output(billing_code)
                                        output("\n")

                                        output(procedure_visit_relation_str)
                                        output("\n")

                                        # procedure "occurence date" property
                                        if date_str != 'invalid date':
                                            output(
                                                ohd_ttl['declare date property uri'].
                                                    format(uri=restoration_procedure_uri,
                                                       type=label2uri['occurrence date'].rsplit('/', 1)[-1],
                                                       date=date_str))

                                        output(procedure_provider_relation_str)
                                        output("\n")

                                        output(procedure_patient_relation_str)
                                        output("\n")

                                        output(cdt_code_procedure_relation_str)
                                        output("\n")

                                    else:
                                    ## refactor to make tooth_num NOT required
                                    #elif pds.notnull(tooth_num):
                                        #TODO - need check this later for procedure_type
                                        tooth_num_array = []
                                        if str(procedure_type) == '11' or str(procedure_type) == '12':  ## for implant and denture
                                            tooth_num_array = get_tooth_array_idx(tooth_data)
                                        else:
                                            tooth_num_array.append(tooth_num_in_file)

                                        for tooth_num in tooth_num_array:
                                            origin_tooth = tooth_num
                                            if pds.notnull(tooth_num):
                                                tooth_num = int(tooth_num)
                                            ## after get_tooth_num call, tooth_num is a string either a valid tooth number or "invalid_tooth_num_{idx}"
                                            tooth_num = get_tooth_num(tooth_num, idx)

                                            if tooth_num.startswith('invalid'):
                                                print("Invalid tooth_num for patient: " + str(pid) + " with ada_code: " + str(ada_code) + " tooth: " + str(origin_tooth) + " tooth_num: " + str(tooth_num) + " idx: " + str(idx))
                                                output_err("Invalid tooth_num for patient: " + str(pid) + " with ada_code: " + str(ada_code) + " tooth: " + str(origin_tooth) + " tooth_num: " + str(tooth_num) + " idx: " + str(idx))

                                            tooth_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + str(tooth_num)

                                            if date_str != 'invalid date':
                                                cdt_code_id = tooth_id + "_" + ada_code + "_" + date_str
                                            else:
                                                cdt_code_id = tooth_id + "_" + ada_code + "_invalid_procedure_date_" + str(idx)
                                            patient_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid)
                                            patient_uri = ohd_ttl['patient uri by prefix'].format(patient_id=patient_id)
                                            provider_id = str(practiceId) + "_" + str(locationId) + "_" + str(prov_id)

                                            if str(procedure_type) == '8':  ## for pontic
                                                tooth_label = "prosthetic tooth " + str(tooth_num) + " of patient " + str(
                                                    pid)  # "prosthetic tooth 13 of patient 1"
                                                tooth_str = ohd_ttl['declare prosthetic tooth by prefix'].format(tooth_id=tooth_id,
                                                                                                                 specific_tooth=get_specific_tooth('prosthetic tooth ', tooth_num, idx),
                                                                                                                 label=tooth_label,
                                                                                                                 practice_id_str=practiceidstring)
                                                if date_str != 'invalid date':
                                                    fixed_partial_denture_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + date_str
                                                else:
                                                    fixed_partial_denture_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_invalid_procedure_date_" + str(idx)
                                                # fixed_partial_denture:1_1_1_1999-12-17
                                                fixed_partial_denture_uri = "fixed_partial_denture:" + fixed_partial_denture_id
                                                fixed_partial_denture_str = ohd_ttl['declare obo type'].format(uri=fixed_partial_denture_uri ,
                                                                                                               type=label2uri['fixed partial denture'].rsplit('/', 1)[-1],
                                                                                                               practice_id_str=practiceidstring)
                                            elif str(procedure_type == '9'): ## for extraction
                                                tooth_label = "tooth " + str(tooth_num) + " of patient " + str(pid) # "tooth 13 of patient 1"
                                                tooth_str = ohd_ttl['declare tooth by prefix'].format(tooth_id=tooth_id,
                                                                                                  specific_tooth=get_specific_tooth('tooth ', tooth_num, idx),
                                                                                                  label=tooth_label,
                                                                                                  practice_id_str=practiceidstring)
                                                dentition_uri = "dentition:" + tooth_id
                                                dentition_str = ohd_ttl['declare obo type'].format(uri=dentition_uri ,
                                                                                                                               type=label2uri['secondary dentition'].rsplit('/', 1)[-1],
                                                                                                                               practice_id_str=practiceidstring)
                                            else:
                                                tooth_label = "tooth " + str(tooth_num) + " of patient " + str(pid) # "tooth 13 of patient 1"
                                                tooth_str = ohd_ttl['declare tooth by prefix'].format(tooth_id=tooth_id,
                                                                                                  specific_tooth=get_specific_tooth('tooth ', tooth_num, idx),
                                                                                                  label=tooth_label,
                                                                                                  practice_id_str=practiceidstring)

                                            # restoration procedure
                                            restoration_procedure_label = "restoration procedure on " + tooth_label + " on " + date_str  # "restoration procedure on tooth 13 of patient 1 on 2003-05-16"
                                            specific_procedure = label2uri[load_ada_procedure_map[ada_code]].rsplit('/', 1)[-1]
                                            restoration_procedure = ohd_ttl['declare restoration procedure'].format(cdt_code_id=cdt_code_id,
                                                                                                                    tooth_restoration_procedure=specific_procedure,
                                                                                                                    label=restoration_procedure_label,
                                                                                                                    practice_id_str=practiceidstring)

                                            # restoration material
                                            restoration_material_label = "restoration material placed in " + tooth_label  # "restoration material placed in tooth 13 of patient 1"
                                            # material fork here: different procedure calls different map for specific material
                                            if str(procedure_type) == '1':  ## for filling (filling has surface info)
                                                specific_material = label2uri[load_ada_filling_material_map[ada_code]].rsplit('/', 1)[-1]
                                            elif str(procedure_type) == '2':  ## for endodontic
                                                specific_material = label2uri[load_ada_endodontic_material_map[ada_code]].rsplit('/', 1)[-1]
                                            elif str(procedure_type) == '3':  ## for inlay
                                                specific_material = label2uri[load_ada_inlay_material_map[ada_code]].rsplit('/', 1)[-1]
                                            elif str(procedure_type) == '4':  ## for onlay
                                                specific_material = label2uri[load_ada_onlay_material_map[ada_code]].rsplit('/', 1)[-1]
                                            elif str(procedure_type) == '5':  ## for apicoectomy
                                                specific_material = label2uri[load_ada_apicoectomy_material_map[ada_code]].rsplit('/', 1)[-1]
                                            elif str(procedure_type) == '7':  ## for crown
                                                specific_material = list()
                                                ada_material_codes = load_ada_crown_material_map[ada_code]
                                                for one_ada_material_code in ada_material_codes:
                                                    specific_material.append(label2uri[one_ada_material_code].rsplit('/', 1)[-1])
                                            elif str(procedure_type) == '8':  ## for pontic
                                                specific_material = list()
                                                ada_material_codes = load_ada_pontic_material_map[ada_code]
                                                for one_ada_material_code in ada_material_codes:
                                                    specific_material.append(label2uri[one_ada_material_code].rsplit('/', 1)[-1])

                                            restoration_material = list()
                                            if no_material_flag == False:
                                                if isinstance(specific_material, basestring):
                                                    restoration_material.append(
                                                        ohd_ttl['declare restoration material'].format(cdt_code_id=cdt_code_id,
                                                                                                       tooth_restoration_material=specific_material,
                                                                                                       label=restoration_material_label,
                                                                                                       practice_id_str=practiceidstring))
                                                elif isinstance(specific_material, collections.Iterable):
                                                    for one_material in specific_material:
                                                        restoration_material.append(ohd_ttl['declare restoration material'].format(cdt_code_id=cdt_code_id,
                                                                                                                tooth_restoration_material=one_material,
                                                                                                                label=restoration_material_label,
                                                                                                                practice_id_str=practiceidstring))

                                            billing_code_label = "billing code " + str(
                                                ada_code) + " for procedure on " + date_str  # "billing code D2160 for procedure on 2003-05-16"
                                            billing_code = ohd_ttl['declare billing code'].format(cdt_code_id=cdt_code_id,
                                                                                                billing_code_for_restorative=
                                                                                                label2uri[ada_code.lower()].rsplit('/',1)[-1],
                                                                                                label=billing_code_label,
                                                                                                practice_id_str=practiceidstring)

                                            # relation: tooth part of patient  'uri1 is part of uri2':
                                            if str(procedure_type) == '8':  ## for pontic
                                                tooth_uri = "prosthetic_tooth:" + str(tooth_id)
                                            else:
                                                tooth_uri = "tooth:" + str(tooth_id)
                                            tooth_patient_relation_str = ohd_ttl['uri1 is part of uri2'].format(uri1=tooth_uri,
                                                                                                                uri2=patient_uri)

                                            restoration_procedure_uri = "restoration_procedure:" + str(cdt_code_id)

                                            # relation: procedure part of visit
                                            procedure_visit_relation_str = ohd_ttl['uri1 is part of uri2'].format(uri1=restoration_procedure_uri,
                                                                                                                  uri2=visit_uri)

                                            material_uri =  "restoration_material:" + str(cdt_code_id)

                                            # relation: restoration procedure has specified input provider
                                            provider_uri = ohd_ttl['provider uri by prefix'].format(provider_id=str(practiceId) + "_" + str(locationId) + "_" + str(prov_id))
                                            procedure_provider_relation_str = ohd_ttl['uri1 has specified input uri2'].format(uri1=restoration_procedure_uri,
                                                                                                                              uri2=provider_uri)

                                            # relation: restoration procedure has specified input tooth
                                            procedure_tooth_input_relation_str = ohd_ttl['uri1 has specified input uri2'].format(uri1=restoration_procedure_uri,
                                                                                                                                 uri2=tooth_uri)

                                            # relation: procedure has specified input material
                                            if no_material_flag == False:
                                                procedure_input_material_relation_str = ohd_ttl['uri1 has specified input uri2'].format(uri1=restoration_procedure_uri,
                                                                                                                                    uri2=material_uri)

                                            # relation: restoration procedure has specified output tooth
                                            procedure_tooth_output_relation_str = ohd_ttl['uri1 has specified output uri2'].format(uri1=restoration_procedure_uri,
                                                                                                                                   uri2=tooth_uri)

                                            # relation: cdt code is about restoration procedure
                                            cdt_code_uri = "cdt_code:" + str(cdt_code_id)
                                            cdt_code_procedure_relation_str = ohd_ttl['uri1 is about uri2'].format(uri1=cdt_code_uri,
                                                                                                                   uri2=restoration_procedure_uri)

                                            if str(procedure_type) == '1' or str(procedure_type) == '3' or str(procedure_type) == '4':  ## for filling/inlay/onlay (with surface info)
                                                if pds.notnull(surface) and surface:
                                                    output(tooth_str)
                                                    output("\n")

                                                    surface_char = list(surface)

                                                    output(restoration_procedure)
                                                    output("\n")

                                                    if no_material_flag == False:
                                                        for one_restoration_material in restoration_material:
                                                            output(one_restoration_material)
                                                            output("\n")

                                                    output(billing_code)
                                                    output("\n")

                                                    output(tooth_patient_relation_str)
                                                    output("\n")

                                                    output(procedure_visit_relation_str)
                                                    output("\n")

                                                    # procedure "occurence date" property
                                                    if date_str != 'invalid date':
                                                        output(
                                                            ohd_ttl['declare date property uri'].
                                                                format(uri=restoration_procedure_uri,
                                                                   type=label2uri['occurrence date'].rsplit('/', 1)[-1],
                                                                   date=date_str))

                                                    for (single_surface) in surface_char:
                                                        convert_surface = get_surface(single_surface, idx)

                                                        if convert_surface.startswith("invalid"):
                                                            print("Invalid surface for patient: " + str(
                                                                pid) + " with ada_code: " + str(
                                                                ada_code) + " tooth: " + str(
                                                                origin_tooth) + " tooth_num: " + str(
                                                                tooth_num) + " surface: " + str(single_surface) + " idx: " + str(
                                                                idx))
                                                            output_err("Invalid surface for patient: " + str(
                                                                pid) + " with ada_code: " + str(
                                                                ada_code) + " tooth: " + str(
                                                                origin_tooth) + " tooth_num: " + str(
                                                                tooth_num) + " surface: " + str(single_surface) + " idx: " + str(
                                                                idx))

                                                        surface_id = tooth_id + "_" + convert_surface

                                                        restored_surface_label = "restored surface " + single_surface.upper() + " for " + tooth_label  # "restored surface M for tooth 13 of patient 1"
                                                        specific_restored_tooth_surface = get_specific_restored_tooth_surface(single_surface, idx)
                                                        restrored_surface_str = ohd_ttl['declare restored tooth surface by prefix'].\
                                                            format(surface_id=surface_id,
                                                                   specific_restored_tooth_surface=specific_restored_tooth_surface,
                                                                   label=restored_surface_label,
                                                                   practice_id_str=practiceidstring)
                                                        output(restrored_surface_str)

                                                        #relation: restored surface part of tooth
                                                        restored_surface_uri = "restored_tooth_surface:" + str(surface_id)
                                                        restored_surface_tooth_relation_str = ohd_ttl['uri1 is part of uri2'].format(uri1=restored_surface_uri, uri2=tooth_uri)
                                                        output(restored_surface_tooth_relation_str)
                                                        output("\n")

                                                        #relation: material part of restored surface
                                                        if no_material_flag == False:
                                                            material_restored_surface_relation_str = ohd_ttl['uri1 is part of uri2'].format(uri1=material_uri, uri2=restored_surface_uri)
                                                            output(material_restored_surface_relation_str)
                                                            output("\n")

                                                        #relation: restoration procedure has specified output restored surface
                                                        procedure_restored_surface_relation_str = ohd_ttl['uri1 has specified output uri2'].\
                                                            format(uri1=restoration_procedure_uri, uri2=restored_surface_uri)
                                                        output(procedure_restored_surface_relation_str)
                                                        output("\n")

                                                    output(procedure_provider_relation_str)
                                                    output("\n")

                                                    output(procedure_tooth_input_relation_str)
                                                    output("\n")

                                                    if no_material_flag == False:
                                                        output(procedure_input_material_relation_str)
                                                        output("\n")

                                                    output(procedure_tooth_output_relation_str)
                                                    output("\n")

                                                    output(cdt_code_procedure_relation_str)
                                                    output("\n")

                                                else:
                                                    ## null/empty surface when there's supposed to have surface:
                                                    print("Null surface for patient: " + str(pid) + " with ada_code: " + str(ada_code) + " tooth: " + str(origin_tooth) + " tooth_num: " + str(tooth_num) + " surface: "  + str(surface) + " idx: " + str(idx))
                                                    output_err("Null surface for patient: " + str(pid) + " with ada_code: " + str(ada_code) + " tooth: " + str(origin_tooth) + " tooth_num: " + str(tooth_num) + " surface: "  + str(surface) + " idx: " + str(idx))

                                                    output(tooth_str)
                                                    output("\n")

                                                    output(restoration_procedure)
                                                    output("\n")

                                                    if no_material_flag == False:
                                                        for one_restoration_material in restoration_material:
                                                            output(one_restoration_material)
                                                            output("\n")

                                                    output(billing_code)
                                                    output("\n")

                                                    output(tooth_patient_relation_str)
                                                    output("\n")

                                                    output(procedure_visit_relation_str)
                                                    output("\n")
                                                    output(procedure_provider_relation_str)
                                                    output("\n")

                                                    output(procedure_tooth_input_relation_str)
                                                    output("\n")

                                                    if no_material_flag == False:
                                                        output(procedure_input_material_relation_str)
                                                        output("\n")

                                                    output(procedure_tooth_output_relation_str)
                                                    output("\n")

                                                    output(cdt_code_procedure_relation_str)
                                                    output("\n")

                                            elif str(procedure_type) == '2' or str(procedure_type) == '5' or str(procedure_type) == '6' or str(procedure_type) == '7'\
                                                    or str(procedure_type) == '8' or str(procedure_type) == '9':
                                                ## for endodontic, apicoectomy, root amputation, crown, pontic, extraction
                                                output(tooth_str)
                                                output("\n")

                                                output(restoration_procedure)
                                                output("\n")

                                                if no_material_flag == False:
                                                    for one_restoration_material in restoration_material:
                                                        output(one_restoration_material)
                                                        output("\n")

                                                output(billing_code)
                                                output("\n")

                                                if str(procedure_type) == '8': ## for pontic
                                                    output(fixed_partial_denture_str)
                                                    output("\n")

                                                    #:prosthetic tooth part of :fixed partial denture
                                                    ## changed to Bill's multiple statements in brackets fashion:
                                                    #prosthetic_tooth_fixed_partial_denture_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                                                    #    uri1=tooth_uri,
                                                    #    uri2=fixed_partial_denture_uri)
                                                    #:fixed partial denture part of :patient
                                                    #fixed_partial_denture_patient_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                                                    #    uri1=fixed_partial_denture_uri,
                                                    #    uri2=patient_uri)
                                                    #output(prosthetic_tooth_fixed_partial_denture_relation_str)
                                                    #output("\n")
                                                    #output(fixed_partial_denture_patient_relation_str)
                                                    #output("\n")

                                                    #relation prosthetic tooth part of  fixed partial denture, and patient
                                                    prosthetic_tooth_fixed_partial_denture_relation_str = ohd_ttl['relate prosthetic tooth to denture and patient']\
                                                        .format(tooth_id=tooth_id,
                                                                fixed_partial_denture_uri=fixed_partial_denture_uri,
                                                                practice_id_str=practiceidstring,
                                                                patient_uri=patient_uri)

                                                    output(prosthetic_tooth_fixed_partial_denture_relation_str)
                                                    output("\n")

                                                elif str(procedure_type) == '9':  ## for extraction
                                                    output(dentition_str)
                                                    output("\n")

                                                    #tooth is not part of dentition relation
                                                    tooth_not_part_dentition_relation_str = ohd_ttl['uri1 is NOT in relationship with uri2'].format(
                                                        uri1=tooth_uri,
                                                        relation=label2uri['is part of'],
                                                        uri2=dentition_uri)
                                                    output(tooth_not_part_dentition_relation_str)
                                                    output("\n")

                                                    # relation dentition part of patient
                                                    dentition_patient_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                                                        uri1=dentition_uri, uri2=patient_uri)
                                                    output(dentition_patient_relation_str)
                                                    output("\n")

                                                    #dentition "missing tooth number" property
                                                    if not tooth_num.startswith('invalid'):
                                                        dentition_miss_tooth_prop = ohd_ttl['declare string property uri'].format(
                                                            uri=dentition_uri, type = label2uri['missing tooth number'].rsplit('/', 1)[-1], string_value=str(tooth_num))
                                                        output(dentition_miss_tooth_prop)
                                                        output("\n")

                                                    # relation: procedure has_specified_output dentition
                                                    procedure_dentition_relation_str = ohd_ttl['uri1 has specified output uri2']\
                                                        .format(uri1=restoration_procedure_uri, uri2=dentition_uri)
                                                    output(procedure_dentition_relation_str)
                                                    output("\n")
                                                else:
                                                    #TODO: check out upcoming proceudres for this, like denture, implant.
                                                    ## extraction and pontics dont have tooth, so no print out of tooth_patient_relation_str, the rest should have
                                                    output(tooth_patient_relation_str)
                                                    output("\n")

                                                # relation: material part of tooth
                                                if no_material_flag == False:
                                                    material_tooth_relation_str = ohd_ttl['uri1 is part of uri2'].format(
                                                        uri1=material_uri, uri2=tooth_uri)
                                                    output(material_tooth_relation_str)
                                                    output("\n")

                                                output(procedure_visit_relation_str)
                                                output("\n")

                                                # procedure "occurence date" property
                                                if date_str != 'invalid date':
                                                    output(
                                                        ohd_ttl['declare date property uri'].
                                                            format(uri=restoration_procedure_uri,
                                                               type=label2uri['occurrence date'].rsplit('/', 1)[-1],
                                                               date=date_str))

                                                output(procedure_provider_relation_str)
                                                output("\n")

                                                output(procedure_tooth_input_relation_str)
                                                output("\n")

                                                if no_material_flag == False:
                                                    output(procedure_input_material_relation_str)
                                                    output("\n")

                                                output(procedure_tooth_output_relation_str)
                                                output("\n")

                                                output(cdt_code_procedure_relation_str)
                                                output("\n")
                                #else:
                                #    print("Info -- pid: " + str(pid) + " with procedure: " + str(ada_code) + " has no tooth info. " + " idx: " + str(idx))
                                #    output_err("Info -- pid: " + str(pid) + " with procedure: " + str(ada_code) + " has no tooth info. " + " idx: " + str(idx))
                            except Exception as ex1:
                                print("Info -- pid: " + str(pid) + " procedure with problem: " + str(ada_code) + " tooth_num: " + str(tooth_num) + " idx: " + str(idx))
                                output_err("Info -- pid: " + str(pid) + " procedure with problem: " + str(ada_code) + " tooth_num: " + str(tooth_num) + " idx: " + str(idx))
                                logging.exception("message")
                        except Exception as ex:
                            print("Problem procedure date for patient: " + str(pid) + " for practice: " + str(practiceId) + " idx: " + str(idx))
                            output_err("Problem procedure date for patient: " + str(pid) + " for practice: " + str(practiceId) + " idx: " + str(idx))
                            logging.exception("message")

def get_ada_code(ada_code, idx):
    if len(ada_code) != 5:
        return "invalid_ada_code_" + str(idx)
    else:
        return ada_code

def get_tooth_num(tooth_num, idx):
    if pds.notnull(tooth_num):
        try:
            label2uri["tooth " + str(tooth_num)]
        except Exception as ex:
            return "invalid_tooth_num_" + str(idx)
        return str(tooth_num)
    else:
        return "invalid_tooth_num_" + str(idx)

## now the tooth_prefix is one of "tooth ", "prosthetic tooth ".
def get_specific_tooth(tooth_prefix, tooth_num, idx):
    try:
        specific_tooth = label2uri[tooth_prefix + str(tooth_num)]
        return specific_tooth
    except Exception as ex:
        if tooth_prefix.startswith('tooth'):
            return label2uri['tooth']
        elif tooth_prefix.startswith('prosthetic'):
            return label2uri['prosthetic tooth']

def get_surface(single_surface, idx):
    try:
        label2uri[restored_tooth_surface_label_map[single_surface.lower()]]
        return single_surface
    except Exception as ex:
        return "invalid_surface_" + str(idx)

def get_specific_restored_tooth_surface(single_surface, idx):
    try:
        specific_restored_tooth_surface = label2uri[restored_tooth_surface_label_map[single_surface.lower()]]
        return specific_restored_tooth_surface
    except Exception as ex:
        return label2uri['restored tooth surface']

def get_tooth_array_idx(tooth_data):
    tooth_num_array = []
    array_idx = 1
    for tooth_array_char in tooth_data:
        if 'Y' == tooth_array_char and array_idx < 33:
            tooth_num_array.append(array_idx)
        array_idx = array_idx + 1
    #TODO - check on this:
    ## if there is NO tooth data marked with Y for first 32 teeth, append '' into it so we can do invalid info output
    if len(tooth_num_array) < 1:
        tooth_num_array.append('empty_tooth')

    return tooth_num_array

def test_get_tooth_array_idx():
    indx_array = get_tooth_array_idx('NNNNNNNNNNYYYYYNNNNNYYYYYYYYYYYYYYY')
    print indx_array
    indx_array = get_tooth_array_idx('NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
    print indx_array
#test_get_tooth_array_idx()

# print_procedure_ttl(practice_id='1', procedure_type=1,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=2,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=3,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=4,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=5,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=6,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=7,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=8,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=9,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
# print_procedure_ttl(practice_id='1', procedure_type=10,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/PRAC_1/Patient_History.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/PRAC_1/',
#                     vendor='ES')
##test dentrix with 2 procedures
#print_procedure_ttl(practice_id='1', procedure_type=1,
#                    input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/Dentrix/PRAC_1/Dentrix_Pract1_Patient_History.txt',
#                    output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/dentrix/PRAC_1/',
#                    vendor='dentrix')
#print_procedure_ttl(practice_id='1', procedure_type=2,
#                    input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/Dentrix/PRAC_1/Dentrix_Pract1_Patient_History.txt',
#                    output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/data/translated/dentrix/PRAC_1/',
#                    vendor='dentrix')
# print_procedure_ttl(practice_id='1', procedure_type=2,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/dentrix_sample/tooth history.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/dentrix_sample/',
#                     vendor='dentrix')
# print_procedure_ttl(practice_id='1', procedure_type=1,
#                     input_f='/Users/cwen/development/pyCharmHome/NDPBRN/src/dentrix_sample/tooth history.txt',
#                     output_p='/Users/cwen/development/pyCharmHome/NDPBRN/src/dentrix_sample/',
#                     vendor='dentrix')
