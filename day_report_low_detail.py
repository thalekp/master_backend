from src.analysis.determine_loss_factors import determine_loss_factors
from src.analysis.explain_volume_imbalance import explain_volume_imbalance
from services.constants import price_areas
from services.parks_list import get_unprofitable_parks
from src.analysis.unforeseen_event import unforeseen_event

def enter_new_line(str):
    parts = str.split('\n')
    output_str = ""
    for part in parts:
        str_list = part.split()
        character_limit = 32
        current_char_count = 0
        final_str = ""
        this_str_part = ""
        for word in str_list:
            if word == "Ubalansekostnad":
                final_str = final_str+"\n"+this_str_part
                this_str_part = "\n"+word
                current_char_count = len(word)
            elif current_char_count+len(word)+1<character_limit:
                this_str_part = this_str_part+" "+word
                current_char_count += (len(word)+1)
            else:
                final_str = final_str+"\n"+this_str_part
                this_str_part = word
                current_char_count = len(word)
        final_str = final_str+"\n"+this_str_part
        output_str = output_str+final_str
    return output_str

def list_to_str(list):
    if len(list)==0:
        return ""
    elif len(list)==1:
        return list[0]
    else:
        return_str = list[0]
        for index in range(len(list[1:])):
            if index == len(list)-2:
                return_str = return_str+" og "+list[index+1]
            else:
                return_str = return_str+", "+list[index+1]
        return return_str
    
def coherent_list(list):
    if len(list)>1:
        last_step = list[0]
        for item in list[1:]:
            if item-last_step != 1: return False
            last_step = item
        return True
    else: return True

def get_ld_day_report():
    loss_factors = determine_loss_factors()
    unprofitable_parks = get_unprofitable_parks()

    park_names = [key.replace("aa", "å").capitalize() for key in unprofitable_parks.keys()]
    report = ""

    if len(unprofitable_parks) > 0:
        bindeord = "også"
        report += f"I dag så vi store ubalansekostnader på {list_to_str(park_names)}. "
        report += "Disse skyldes hovedsakelig volumavvik og høye priser. "
    else:
        bindeord = ""
        report += "I dag var en bra dag, og ingen parker hadde store ubalansekostnader. "

    high_volume_imbalance_parks = [
        park for park, data in loss_factors.items()
        if data.get('volume_abnormality') and park not in unprofitable_parks
    ]

    if high_volume_imbalance_parks:
        report += f"\n\nNoen parker hadde {bindeord} store ubalansevolum, uten at dette førte til store kostnader."
        example = high_volume_imbalance_parks[0].replace("aa", "å").capitalize()
        report += f"\nFor eksempel hadde {example} betydelige avvik."

    return enter_new_line(report)

