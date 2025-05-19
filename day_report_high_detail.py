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

def get_hd_day_report():
    loss_factors = determine_loss_factors()
    unprofitable_parks = get_unprofitable_parks()
    
    if len(unprofitable_parks)>0: 
        report = f"I dag så vi store ubalansekostnader på {list_to_str(list([key.replace('aa', 'å').capitalize() for key in unprofitable_parks.keys()]))}. "
        bindeord = "også"
    else: 
        report = "I dag var en bra dag, og ingen parker hadde store ubalansekostnader. "
        bindeord = ""
    for park in unprofitable_parks:
        data = loss_factors.get(park)
        if data.get('volume_abnormality'):
            less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
            buy_hours_set = set(data.get('buy_hours', []))
            high_price_hours_set = set(data.get('high_price_hours', []))
            overlap_hours = sorted(list(buy_hours_set & high_price_hours_set))
            if overlap_hours:
                report = report + f"\n\nUbalansekostnadene på {park.replace('aa', 'å').capitalize()} skyldes primært store volumavvik som sammenfalt med høye priser "
                if coherent_list(overlap_hours) and len(overlap_hours)>1: report = report + f"fra kl. {overlap_hours[0]} til kl. {overlap_hours[-1]}"
                report = report +". "
            else:
                report = report + f"\n\nUbalansekostnadene på {park.capitalize()} skyldes primært store volumavvik. "
            
            if less_wind or model_disagreement or availability_reduction or icing: report = report + "Volumavvikene ser ut til å skyldes:"
            if icing: report = report + "\n• Ising eller andre uforutsette hendelser"
            if not icing or len(data.get('abnormally_low_production_hours'))<12:
                if less_wind: report = report + "\n• Mindre vind enn meldt"
                if model_disagreement: report = report + "\n• Uenighet mellom værmodellene"
                if availability_reduction: report = report + "\n• Lavere tilgjengelighet enn rapportert"
            
        else:
            report = report + f"\nUbalansekostnadene på {park} skyldes primært store prisavvik."
    high_volume_imbalance_parks = [park for park, data in loss_factors.items() if data.get('volume_abnormality') and park not in unprofitable_parks]
    if len(high_volume_imbalance_parks)>0: report = report+f"\n\nNoen parker hadde {bindeord} store ubalansevolum, uten at dette førte til store kostnader. "
    
    for park in high_volume_imbalance_parks:
        less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
        if park == high_volume_imbalance_parks[0]:  report = report + f"\nFor eksempel hadde {park.replace('aa', 'å').capitalize()} betydelige avvik. "
        else: report = report + f"\nVi så også store avvik på {park.replace('aa', 'å').capitalize()}. "
        if less_wind or model_disagreement or availability_reduction or icing: report = report + "Årsaken ser ut til å være: "
        if less_wind: report = report + "\n• Mindre vind enn rapportert"
        if model_disagreement: report = report + "\n• Uenighet mellom værmodellene"
        if availability_reduction: report = report + "\n• Lavere tilgjengelighet enn rapportert om"
        if icing: report = report + "\n• Ising eller andre uforutsette hendelser"
    
    return enter_new_line(report)