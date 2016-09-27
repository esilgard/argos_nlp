import shelve


shelf_file = 'shelf.db'
full_patient_file = 'full_patient.db'
PATIENTS = 'Patients'


def shelve_patients(patients):
    s = shelve.open(shelf_file)
    try:
        s[PATIENTS] = patients
    finally:
        s.close()


def unshelve_patients():
    s = shelve.open(shelf_file)
    try:
        patients = s[PATIENTS]
    finally:
        s.close()

    return patients


def shelve_full_patients(patients):
    s = shelve.open(full_patient_file)
    try:
        s[PATIENTS] = patients
    finally:
        s.close()


def unshelve_full_patients():
    s = shelve.open(full_patient_file)
    try:
        patients = s[PATIENTS]
    finally:
        s.close()

    return patients
