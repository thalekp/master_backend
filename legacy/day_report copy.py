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
    unprofitable_parks = get_unprofitable_parks()
    all_parks = get_all_parks()
    total_revenue = 0
    total_dayahead_revenue = 0
    
    park_income = {}
    
    for park in all_parks:
        revenue = calc_revenue(park)
        dayahead = calc_dayahead_revenue(park)
        park_income[park] = {'revenue': revenue, 'dayahead': dayahead}
        total_revenue += revenue
        total_dayahead_revenue += dayahead
    
    rg = determine_revenue_grade(total_revenue, dayahead_revenue=total_dayahead_revenue)
    if rg == "success": status_str = "Dette var en bra dag."
    elif rg == "warning": status_str = "Dette var en ganske dårlig dag."
    else: status_str = "Dette var en veldig dårlig dag."
    
    if unprofitable_parks:
        skyld_str = ""
        for park in unprofitable_parks.keys():
            skyld_str = skyld_str+"Ubalansekostnad for "+park.capitalize()+" ligger "+babel.numbers.format_currency(-unprofitable_parks.get(park)[0][1], '€')+" over median. "
            timesteps, new_grade, cost = find_extreme_prices(park)
            grade = new_grade
            hypothetical_revenue = park_income.get(park).get('revenue')+cost
            bindeledd = "primært"
            if len(timesteps)>0:
                kl_str = str(timesteps[0])
                if len(timesteps)>1:
                    for kl in timesteps[1:]:
                        kl_str = kl_str+", "+str(kl)
                if new_grade == 'success': skyld_str = skyld_str+f"Dette skyldes ekstreme priser kl. {kl_str} som kostet oss {babel.numbers.format_currency(cost, '€')}. "
                else: 
                    bindeledd ="også"
                    skyld_str = skyld_str+f"Dette skyldes først og fremst ekstreme priser kl. {kl_str} som kostet oss {babel.numbers.format_currency(cost, '€')}. "
            if grade != "success":
                blame, no_volume_hours, reg_status, reg_periode, prediction_offset_severity, explanation_weather_sets, replan_improvement, cost, grade = determine_loss_factors(park, hypothetical_revenue, timesteps, None, park_income.get(park).get('dayahead'))
                
                #Blame
                blame_to_norsk = {'availability': 'perioder uten produksjon', 'price': 'høye reguleringspriser', 'volume': 'stort ubalansevolum'}
                if len(blame)>1:
                    if 'price' in blame: blame_str = blame_to_norsk.get(blame[0])+" samtidig som "+blame_to_norsk.get(blame[1])
                    else: blame_str = blame_to_norsk.get(blame[0])+" og "+blame_to_norsk.get(blame[1])
                else:
                    blame_str = blame_to_norsk.get(blame[0])
                skyld_str = skyld_str+f"Dette skyldes {bindeledd} {blame_str}. "
                bindeledd = ""
                
                """#No Volume
                if no_volume_hours>0 and 'availability' in blame:
                    skyld_str = skyld_str+f"Denne dagen hadde {park.capitalize()} {no_volume_hours} timer uten produksjon. "
                    bindeledd = "også"""
                
                #Bare priser
                reg_grade_to_status = {0: 'vanlige', 1: 'litt høye', 2: 'ganske høye', 3: 'veldig høye'}
                if 'price' in blame and not 'volume' in blame:
                    periode_str = {1: 'en periode', 2: 'periode'}
                    skyld_str = skyld_str+f"Denne dagen hadde {park.capitalize()} {bindeledd} {periode_str.get(reg_periode)} med {reg_grade_to_status.get(reg_status)} reguleringspriser. "
                    bindeledd = "også"
                    
                #Volumavvik eller ingen volum
                if not 'price' in blame and ('volume' in blame or 'availability' in blame):
                    prediction_offset_severity_str = {1: "store", 2: "veldig store", 3: "ekstremt store"}
                    if 'volume' in blame: skyld_str = skyld_str+f"Det er {prediction_offset_severity_str.get(prediction_offset_severity)} avvik mellom dayahead produksjon og faktisk produksjon samtidig som {reg_grade_to_status.get(reg_status)} reguleringspriser. "
                    if 'availability' in blame: skyld_str = skyld_str+f"Denne dagen hadde {park.capitalize()} {no_volume_hours} timer uten produksjon. "
                    bindeledd = "også"
                    if len(explanation_weather_sets)>0:
                        weather_blame = explanation_weather_sets[0]
                        for ws in explanation_weather_sets[1:]:
                                if ws == explanation_weather_sets[-1]: weather_blame = weather_blame+" og "+ws
                                else: weather_blame = weather_blame+", "+ws
                        if replan_improvement<0.3 or (replan_improvement < 0.8 and no_volume_hours>5) or no_volume_hours>12:
                                skyld_str = skyld_str + f"Avvikene ser ikke ut til å henge sammen med usikkerhet i værmeldinger, men kan skyldes ising eller andre uforutsette hendelser. "
                        elif replan_improvement < 0.8:
                                skyld_str = skyld_str + f"Avvikene skyldes kanskje usikkerhet i værmeldingene fra {weather_blame}. Det kan også hende at det skyldes ising eller andre uforutsette hendelser."
                        elif replan_improvement < 0.9:
                                skyld_str = skyld_str + f"Avvikene skyldes mest sannsynlig usikkerhet i værmeldingene fra {weather_blame}. "
                        else:
                                skyld_str = skyld_str + f"Avvikene skyldes usikkerhet i værmeldingene fra {weather_blame}. "
                    else:
                            skyld_str = skyld_str + f"Avvikene ser ikke ut til å henge sammen med usikkerhet i værmeldinger, men kan skyldes ising eller andre uforutsette hendelser. "                    
                #Pris og volum
                if 'price' in blame and 'volume' in blame:
                    reg_grade_to_status = {0: 'vanlige', 1: 'litt høye', 2: 'ganske høye', 3: 'veldig høye'}
                    prediction_offset_severity_str = {1: "store", 2: "veldig store", 3: "ekstremt store"}
                    periode_str = {1: 'en periode', 2: 'periode'}
                    skyld_str = skyld_str+f"Denne dagen hadde {park.capitalize()} {bindeledd} {periode_str.get(reg_periode)} med {reg_grade_to_status.get(reg_status)} reguleringspriser samtidig som {prediction_offset_severity_str.get(prediction_offset_severity)} avvik mellom dayahead produksjon og faktisk produksjon."
                    if len(explanation_weather_sets)>0:
                        weather_blame = explanation_weather_sets[0]
                        if len(explanation_weather_sets)>0:
                            for ws in explanation_weather_sets[1:]:
                                if ws == explanation_weather_sets[-1]: weather_blame = weather_blame+" og "+ws
                                else: weather_blame+", "+ws
                            if replan_improvement<0.3:
                                skyld_str = skyld_str
                            elif replan_improvement < 0.5:
                                skyld_str = skyld_str + f"Dette skyldes kanskje endringer i værmeldingene fra {weather_blame}. "
                            elif replan_improvement < 0.8:
                                skyld_str = skyld_str + f"Dette skyldes ganske sikkert endringer i værmeldingene fra {weather_blame}. "
                            else:
                                skyld_str = skyld_str + f"Dette skyldes endringer i værmeldingene fra {weather_blame}. "
            
    else: 
        skyld_str = "\nAlle parker hadde normal eller bedre inntjening."
    
    if total_revenue<0: earn_or_lose = 'tapte'
    else : earn_or_lose = 'tjente'
    return f"{status_str}\nVi {earn_or_lose} {babel.numbers.format_currency(abs(total_revenue), '€')}. {enter_new_line(skyld_str)}"