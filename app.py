from flask import Flask , render_template , request , flash
import pickle
import os
import csv
import json
from datetime import datetime
import pytz

newMedData12 = pickle.load(open('pickle_files/medDataSet.pkl','rb'))
similarity = pickle.load(open('pickle_files/similarityWeightAssign.pkl','rb'))
similaritySideEffect = pickle.load(open('pickle_files/similaritySideEffect.pkl','rb'))



app = Flask(__name__)

# Flash Message
app.secret_key = 'message'

# Path for csv file 
csv_folder = 'csv_input_files'
if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)
csv_file_path = os.path.join(csv_folder , "user_inputs_data.csv")
# Creating CSV file with Two Columns one with name and another with timestamp
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file) 
        writer.writerow(['user_input_text','suggested_names','results','timestamp'])




@app.route('/')
def index():
    return render_template('home.html')


@app.route('/recommendation')
def recommend_page():
    return render_template('recommendation.html')


@app.route('/contact')
def contact_page():
    return render_template('contact.html')


@app.route('/recommend_action',methods=['POST'])
def recommendation():
    try:
        medicine = request.form.get('user_input')
        medicine = medicine.strip()
        medicine_index = newMedData12[newMedData12['Name'] == medicine].index[0]
        distance = similarity[medicine_index]
        medicine_list = list(enumerate(distance))
        sorted_medicine_list = sorted(medicine_list, reverse=True, key=lambda x: x[1])[1:6]

        top_medicines = {}
        seen = set()
        
        for i in sorted_medicine_list:
            if len(top_medicines) >= 5:
                break
            
            if newMedData12.iloc[i[0]].Name not in seen:
                top_medicines[newMedData12.iloc[i[0]].Name] = {
                    'image_url': newMedData12.iloc[i[0]]["image_url"],
                    'usedFor' : newMedData12.iloc[i[0]].Uses,
                    'sideEffect' : newMedData12.iloc[i[0]].Side_effects,
                    'review_score' : newMedData12.iloc[i[0]].score,
                    'mft' : newMedData12.iloc[i[0]].Manufacturer
                }
            
                seen.add(newMedData12.iloc[i[0]].Name)
    
        sorted_top_medicines = dict(sorted(top_medicines.items(), key=lambda item: item[1]['review_score'], reverse=True))


        medicine_names = ', '.join(sorted_top_medicines.keys())
        sorted_top_medicines_JSON = json.dumps(sorted_top_medicines)
        # Storing user inputs into a csv file with current date and time 
        timeZone = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.now(timeZone).strftime('%d-%m-%Y %H:%M:%S')
        with open(csv_file_path,mode="a",newline='') as file:
            writer = csv.writer(file)
            writer.writerow([medicine , medicine_names , sorted_top_medicines_JSON , timestamp])
        


        return render_template("recommendation.html",sorted_top_medicines=sorted_top_medicines)
    

    except Exception as e: 
        flash("No Such Input Found , please retry with avaiable names in the Dataset , thanks ;-)") 

    return render_template("recommendation.html", sorted_top_medicines={}) 




# Side Effect Code ---------------------------------------------------------------------------



@app.route('/recommend_sideEffect',methods=['POST'])
def recommendationSideEffect():
    try:
        medicine = request.form.get('side_effect')
        medicine = medicine.strip()
        medicine_index = newMedData12[newMedData12['Name'] == medicine].index[0]
        distance = similaritySideEffect[medicine_index]
        medicine_list = list(enumerate(distance))
        sorted_medicine_list = sorted(medicine_list, reverse=True, key=lambda x: x[1])[1:6]


        
        top_medicines = {}
        seen = set()
        
        for i in sorted_medicine_list:
            if len(top_medicines) >= 5:
                break
            
            if newMedData12.iloc[i[0]].Name not in seen:
                top_medicines[newMedData12.iloc[i[0]].Name] = {
                    'image_url': newMedData12.iloc[i[0]]["image_url"],
                    'usedFor' : newMedData12.iloc[i[0]].Uses,
                    'sideEffect' : newMedData12.iloc[i[0]].Side_effects,
                    'review_score' : newMedData12.iloc[i[0]].score,
                    'mft' : newMedData12.iloc[i[0]].Manufacturer
                }
            
                seen.add(newMedData12.iloc[i[0]].Name)
    
        sorted_top_medicines_side_effects = dict(sorted(top_medicines.items(), key=lambda item: item[1]['review_score'], reverse=True))

        medicine_names = ', '.join(sorted_top_medicines_side_effects.keys())
        sorted_top_medicines_JSON = json.dumps(sorted_top_medicines_side_effects)
        # Storing user inputs into a csv file with current date and time 
        timeZone = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.now(timeZone).strftime('%d-%m-%Y %H:%M:%S')
        with open(csv_file_path,mode="a",newline='') as file:
            writer = csv.writer(file)
            writer.writerow([medicine , medicine_names , sorted_top_medicines_JSON , timestamp])



        return render_template("recommendation.html",sorted_top_medicines_side_effects=sorted_top_medicines_side_effects)
    

    except Exception as e: 
        flash("No Such Input Found , please retry with avaiable names in the Dataset , thanks ;-)") 

    return render_template("recommendation.html", sorted_top_medicines_side_effects={}) 




if __name__ == '__main__':
    app.run(debug=True)




