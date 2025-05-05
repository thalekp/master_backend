from src.calculations.calc_revenue import calc_revenue
from src.calculations.calc_dayahead_revenue import calc_dayahead_revenue
from src.analysis.determine_status import determine_revenue_grade, determine_offset
from services.parks_list import get_unprofitable_parks, get_all_parks
from src.analysis.extreme_price import find_extreme_prices
from src.analysis.determine_loss_factors import determine_loss_factors
from src.read_data import read_forecast_data
import babel.numbers

def enter_new_line(str):
    str_list = str.split()
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
    return final_str
        

def get_day_report():
    parks = get_all_parks()
    revenues = []
    dayaheads = []
    under = get_unprofitable_parks()
    for park in parks:
        revenue = calc_revenue(park)
        revenues.append(revenue)
        dayahead = calc_dayahead_revenue(park)
        dayaheads.append(dayahead)
    
    total = sum(revenues)
    total_dayahead = sum(dayaheads)
    rg = determine_revenue_grade(total, dayahead_revenue=total_dayahead)
    os = determine_offset(total, dayahead_revenue=total_dayahead)    
    
    if rg == "success": status_str = "Dette var en bra dag."
    elif rg == "warning": status_str = "Dette var en ganske dårlig dag."
    else: status_str = "Dette var en veldig dårlig dag."
    
    if under: 
        skyld_str = ""
        for park in under.keys():
            skyld_str = skyld_str+"Ubalansekostnad for "+park.capitalize()+" ligger "+babel.numbers.format_currency(-under.get(park)[0][1], '€')+" over median. "
            
            dayahead, prod = read_forecast_data(park, json = False)
            
            timesteps, new_grade, cost = find_extreme_prices(park)
            grade = new_grade
            hypothetical_revenue = revenues[parks.index(park)]+cost
            bindeledd = ""
            if len(timesteps)>0:
                kl_str = str(timesteps[0])
                if len(timesteps)>1:
                    for kl in timesteps[1:]:
                        kl_str = kl_str+", "+str(kl)
                if new_grade == 'success': skyld_str = skyld_str+f"Dette skyldes ekstreme priser kl. {kl_str} som kostet oss {cost}. "
                else: 
                    bindeledd ="også "
                    skyld_str = skyld_str+f"Dette skyldes først og fremst ekstreme priser kl. {kl_str} som kostet oss {babel.numbers.format_currency(cost, '€')}. "
            if bindeledd == "": bindeledd = "primært"
            if grade != "success":
                blame, no_volume_hours, reg_status, reg_periode, prediction_offset_severity, explanation_weather_sets, replan_improvement, cost, grade = determine_loss_factors(park, hypothetical_revenue, timesteps, None, dayaheads[parks.index(park)])
                if no_volume_hours>0: skyld_str = skyld_str+f"Dette skyldes {no_volume_hours} timer uten produksjon. "
                else:
                    pris_type_str = ""
                    periode_string = ""
                    volum_str = ""
                    if cost>0:
                        reg_grade_to_status = {0: 'vanlige', 1: 'litt høye', 2: 'ganske høye', 3: 'veldig høye'}
                        spot_grade_to_status = {0: 'vanlige', 1: 'litt lave', 2: 'ganske lave', 3: 'veldig lave'}
                        if reg_status>0:
                                if reg_periode ==1: periode_string = "en periode"
                                else: periode_string = "perioder"
                                pris_type_str = f"{periode_string} med {reg_grade_to_status.get(reg_status)} reguleringspriser mens vi hadde lavere produksjon enn predikert"
                        if reg_periode ==1: periode_string = "Perioden"
                        else: periode_string = "Periodene"
                        volum_str = ""
                        if prediction_offset_severity>0:
                            prediction_offset_severity_str = {1: "store", 2: "veldig store", 3: "ekstremt store"}
                            volum_str = f"Det er {prediction_offset_severity_str.get(prediction_offset_severity)} avvik mellom dayahead produksjon og faktisk produksjon. "
                    weather_pred_str = ""
                    if len(explanation_weather_sets)>0:
                            weather_services = explanation_weather_sets[0]
                            weather_quant_str = "værmeldingen"
                            if len(explanation_weather_sets)>1:
                                weather_quant_str = "værmeldingene"
                                for ws in explanation_weather_sets[1:]:
                                    if ws == explanation_weather_sets[-1]:
                                        weather_services = weather_services+" og "+ws
                                    else:
                                        weather_services = weather_services+", "+ws
                            weather_pred_str = f"Dette kan skyldes avvik i {weather_quant_str} fra {weather_services}."
                    if new_grade == 'success': 
                            skyld_str = skyld_str+f"Dette skyldes {bindeledd} {pris_type_str}. {periode_string} kostet totalt {babel.numbers.format_currency(cost, '€')}. {volum_str} {weather_pred_str}"
                    else:
                        skyld_str = skyld_str+f"Dette skyldes {bindeledd} {pris_type_str}. {periode_string} kostet totalt {babel.numbers.format_currency(cost, '€')}. {volum_str} {weather_pred_str}"
                    
                
                
    else: 
        skyld_str = "\nAlle parker ligger over snitt."
    
    if total<0: earn_or_lose = 'tapte'
    else : earn_or_lose = 'tjente'
    
    return f"{status_str}\nVi {earn_or_lose} {babel.numbers.format_currency(abs(total), '€')}. {enter_new_line(skyld_str)}"