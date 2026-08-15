APPOINTMENT_REASONS = {
    "فحص دوري",
    "تنظيف وتلميع",
    "حشوة أسنان",
    "علاج عصب السن",
    "قلع سن",
    "تاج / جسر",
    "تقويم الأسنان",
    "تبييض الأسنان",
    "ألم طارئ",
    "متابعة",
}


PATIENT_GENDERS = {
    "Male",
    "Female",
}


from utils.settings_helper import get_treatment_prices, get_treatment_details

class TreatmentPricesProxy(dict):
    def __getitem__(self, key):
        return get_treatment_prices()[key]
        
    def get(self, key, default=None):
        return get_treatment_prices().get(key, default)
        
    def keys(self):
        return get_treatment_prices().keys()
        
    def items(self):
        return get_treatment_prices().items()
        
    def values(self):
        return get_treatment_prices().values()
        
    def __contains__(self, key):
        return key in get_treatment_prices()
        
    def __iter__(self):
        return iter(get_treatment_prices())

    def __len__(self):
        return len(get_treatment_prices())

    def __repr__(self):
        return repr(get_treatment_prices())


class TreatmentDetailsProxy(dict):
    def __getitem__(self, key):
        return get_treatment_details()[key]

    def get(self, key, default=None):
        return get_treatment_details().get(key, default)

    def keys(self):
        return get_treatment_details().keys()

    def items(self):
        return get_treatment_details().items()

    def values(self):
        return get_treatment_details().values()

    def __contains__(self, key):
        return key in get_treatment_details()

    def __iter__(self):
        return iter(get_treatment_details())

    def __len__(self):
        return len(get_treatment_details())

    def __repr__(self):
        return repr(get_treatment_details())


class TreatmentProcedureTypesProxy(set):
    def __contains__(self, item):
        return item in get_treatment_prices()
        
    def __iter__(self):
        return iter(get_treatment_prices().keys())

    def __len__(self):
        return len(get_treatment_prices())

    def __repr__(self):
        return repr(set(get_treatment_prices().keys()))


TREATMENT_PRICES = TreatmentPricesProxy()
TREATMENT_DETAILS = TreatmentDetailsProxy()
TREATMENT_PROCEDURE_TYPES = TreatmentProcedureTypesProxy()

FDI_TOOTH_SET = {
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48',
    '51', '52', '53', '54', '55',
    '61', '62', '63', '64', '65',
    '71', '72', '73', '74', '75',
    '81', '82', '83', '84', '85'
}

UNIV_TO_FDI = {
    '1': '18', '2': '17', '3': '16', '4': '15', '5': '14', '6': '13', '7': '12', '8': '11',
    '9': '21', '10': '22', '11': '23', '12': '24', '13': '25', '14': '26', '15': '27', '16': '28',
    '17': '38', '18': '37', '19': '36', '20': '35', '21': '34', '22': '33', '23': '32', '24': '31',
    '25': '41', '26': '42', '27': '43', '28': '44', '29': '45', '30': '46', '31': '47', '32': '48'
}
FDI_TO_UNIV = {v: k for k, v in UNIV_TO_FDI.items()}

def get_equivalent_tooth_numbers(t_str: str) -> list[str]:
    """
    Returns equivalent tooth representations (FDI and Universal) without cross-contamination.
    If t_str is an FDI number (e.g. '16'), returns ['16', '3']. It does NOT return '28'.
    """
    t_str = str(t_str).strip()
    if not t_str:
        return []
    if t_str in FDI_TOOTH_SET:
        equiv = [t_str]
        if t_str in FDI_TO_UNIV:
            equiv.append(FDI_TO_UNIV[t_str])
        return equiv
    elif t_str in UNIV_TO_FDI:
        return [t_str, UNIV_TO_FDI[t_str]]
    return [t_str]
