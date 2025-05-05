from src.analysis.determine_loss_factors import determine_loss_factors
from src.read_data import read_forecast_data
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

def get_day_report():
    unprofitable_parks = get_unprofitable_parks()
    print(unprofitable_parks)
    abnormal_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks = determine_loss_factors()
    print(abnormal_prices, extreme_prices, unforeseen_events, abnormal_volumes, non_extreme_parks)
    num_lists = len([l for l in [abnormal_prices, extreme_prices, [p for p in abnormal_volumes if p.lower() in unprofitable_parks]] if len(l)>0])
    if num_lists>0: 
        return_str = "Ubalansekostnadene i dag skyldes primært"
        bindeord = " også"
    else: 
        return_str = "Dette var en bra dag. Det var ingen store ubalansekostnader eller ubalansevolum"
        bindeord = ""
    bindeledd = ""
    if len(extreme_prices.keys())>0:
        return_str = return_str+f" ekstreme priser i {list_to_str(list(extreme_prices.keys()))}"
        if num_lists==3: bindeledd = ","
        else: bindeledd = " og"
    if len(abnormal_prices)>0:
        return_str = return_str+f"{bindeledd} høye priser i {list_to_str(abnormal_prices)}"
        bindeledd = ", og"
    if len([p for p in abnormal_volumes if p not in non_extreme_parks and p.lower() in unprofitable_parks])>0:
        return_str = return_str+f"{bindeledd} store ubalansevolum i {list_to_str([p for p in abnormal_volumes if p not in non_extreme_parks and p.lower() in unprofitable_parks])}"
        bindeledd = ", og"
    if len(non_extreme_parks)>0:
        return_str = return_str+f"{bindeledd} de moderate ubalansevolumene i {list_to_str(non_extreme_parks)} på grunn av uheldig sammenfall med reguleringspris"
        #bindeord = ""
    return_str = return_str+"."
    
    if len(abnormal_volumes)>0:
        for park in abnormal_volumes:
            if park.lower() not in unprofitable_parks.keys(): return_str = return_str +f"\n\nDet er{bindeord} et moderat ubalansevolum i {park.capitalize()} som skyldes"
            else: return_str = return_str +"\n\nUbalansevolumet i "+park+" skyldes"
            less_wind, model_disagreement, availability_reduction, icing = explain_volume_imbalance(park)
            if park in unforeseen_events: return_str = return_str +" noe annet enn lave vindstyrker. Det skyldes mest sannsynlig ising eller andre ufortsette hendelser. "
            else:
                return_str = return_str+":"
                if len(unforeseen_event(park.lower()))>3:  return_str = return_str +"\n• Ising eller andre uforutsette hendelser"
                elif availability_reduction: return_str = return_str +"\n• Lavere tilgjengelighet enn forventet"
                else:
                    if less_wind: return_str = return_str +"\n• Mindre vind enn forventet"
                    if model_disagreement: return_str = return_str +"\n• Uenige værmodeller"
            if park.lower() not in unprofitable_parks: return_str = return_str+"\nDette har ikke ført til høy ubalansekostnad."
    
    for park in unforeseen_events:
        if park not in abnormal_volumes:
            return_str = return_str +f"\n\nDet er moderate  ubalansevolum for {park}. Deler av dagen er produksjonen mye lavere enn vindnivåene skulle tilsi. Dette kan skyldes ising eller andre uforutsette hendelser."
    
    
    return enter_new_line(return_str)