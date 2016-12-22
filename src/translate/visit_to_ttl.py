import pandas as pds
import logging
import os
from load_resources import curr_dir, ohd_ttl, label2uri

def translate_visit_to_ttl(practice_id='3', filename='visit.ttl', print_ttl=True, save_ttl=True):
    # get data from RI-demo-data
    #df_path = os.path.join(curr_dir, '..', 'data', 'Practice1_Patient_History.xlsx')
    df_path = os.path.join(curr_dir, '..', 'data', 'Practice' + str(practice_id) + '_Patient_History.xlsx')
    df = pds.ExcelFile(df_path).parse()

    visit_df = df[['PBRN_PRACTICE', 'PATIENT_ID', 'TRAN_DATE', 'PROVIDER_ID', 'TABLE_NAME', 'DB_PRACTICE_ID']]

    with open(filename, 'w') as f:
        # local function for printing and saving turtle output
        def output(value_str, print_ttl=print_ttl, save_ttl=save_ttl):
            if print_ttl == True: print value_str
            if save_ttl == True: f.write(value_str)

        # output prefixes for ttl file
        prefix_str = ohd_ttl['prefix'].format(practice_id=practice_id)
        output(prefix_str)

        # define uri
        practice_uri = ohd_ttl['practice uri'].format(practice_id=practice_id)
        # define types
        practice_type = label2uri['dental health care organization']
        practice_label = 'practice_' + str(practice_id)
        # delcare individuals
        output(ohd_ttl['declare practice'].format(uri=practice_uri, type=practice_type, label=practice_label))

        # print ttl for each patient
        for (idx, practiceId, pid, visitDate, providerId, tableName, locationId) in visit_df.itertuples():
            if tableName.lower() == 'transactions':
                try:
                    date_str = visitDate.strftime('%Y-%m-%d')

                    visit_id = str(practiceId) + "_" + str(locationId) + "_" + str(pid) + "_" + date_str
                    #uri
                    visit_uri = ohd_ttl['visit uri'].format(visit_id=visit_id)

                    #declare visit
                    output(ohd_ttl['declare obo type with label'].format(uri=visit_uri, type=label2uri['dental visit'].rsplit('/', 1)[-1], label="dental visit " + str(visit_id)))

                    # relate individuals
                    output(ohd_ttl['uri1 realizes uri2'].format(uri1=visit_uri, uri2= str('obo:') + label2uri['dental health care provider role'].rsplit('/', 1)[-1]))
                    output('\n')
                    output(ohd_ttl['uri1 realizes uri2'].format(uri1=visit_uri, uri2=str('obo:') + label2uri['dental patient role'].rsplit('/', 1)[-1]))
                    output(ohd_ttl['declare date property uri'].format(uri=visit_uri, type=label2uri['occurrence date'].rsplit('/', 1)[-1], date=date_str))

                    # patient role: visit realize patient role
                    patientId = str(practiceId) + "_" + str(locationId) + "_" + str(pid)
                    patient_role_uri = ohd_ttl['patient role uri by prefix'].format(patient_id=patientId)
                    patient_patient_role_relation_str = ohd_ttl['uri1 realizes uri2'].format(uri1=visit_uri, uri2=patient_role_uri)
                    output(patient_patient_role_relation_str)
                    output("\n")

                    # provider role: visit realize probider role
                    provider_id = str(practiceId) + "_" + str(locationId) + "_" + str(providerId)
                    provider_role_uri = ohd_ttl['provider role uri by prefix'].format(provider_id=provider_id)
                    patient_provider_role_relation_str = ohd_ttl['uri1 realizes uri2'].format(uri1=visit_uri, uri2=provider_role_uri)
                    output(patient_provider_role_relation_str)
                    output("\n")

                except Exception as ex:
                    print("Problem visit for patient: " + str(pid) + " for practice: " + str(practiceId))
                    logging.exception("message")

translate_visit_to_ttl(practice_id='2')