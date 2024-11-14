from flask import Flask, request, redirect, url_for, render_template
import csv 
import pymongo
app = Flask(__name__)
userName = ''
password = ''
template = 'login.html'

def login_failed():
   return 'Login Failed!'

def validate_user(userName, password):
 loginsucess = False
 dbClient = pymongo.MongoClient("mongodb://localhost:27017/")
 with open('users.csv', mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
    if userName == lines[0] and password == lines[1]:
        loginsucess = True
        break 
  return loginsucess
 
def recommend_workouts(bmi_category, fitness_level):
    # Define BMI categories and workout counts (sets and reps) for each activity
    workouts = {
        "underweight": {
            "pushups": {"sets": 2, "reps": 5},
            "pullups": {"sets": 1, "reps": 3},
            "walking": {"sets": 1, "reps": 30},  # minutes of walking
            "squats": {"sets": 2, "reps": 5}
        },
        "normal": {
            "pushups": {"sets": 3, "reps": 10},
            "pullups": {"sets": 2, "reps": 5},
            "walking": {"sets": 1, "reps": 20},  # minutes of walking
            "squats": {"sets": 3, "reps": 10}
        },
        "overweight": {
            "pushups": {"sets": 2, "reps": 8},
            "pullups": {"sets": 1, "reps": 4},
            "walking": {"sets": 1, "reps": 40},  # minutes of walking
            "squats": {"sets": 2, "reps": 8}
        },
        "obese": {
            "pushups": {"sets": 1, "reps": 5},
            "pullups": {"sets": 1, "reps": 2},
            "walking": {"sets": 1, "reps": 60},  # minutes of walking
            "squats": {"sets": 1, "reps": 5}
        }
    }

    # Adjust workouts based on fitness level (beginner, intermediate, advanced)
    fitness_adjustments = {
        "beginner": 0.8,
        "intermediate": 1,
        "advanced": 1.2
    }

    # Get adjustment factor based on fitness level
    adjustment_factor = fitness_adjustments.get(fitness_level, 1)

    # Adjust the sets and reps based on fitness level
    adjusted_workouts = {}
    for activity, counts in workouts[bmi_category].items():
        adjusted_sets = max(1, int(counts["sets"] * adjustment_factor))  # Ensure at least 1 set
        adjusted_reps = max(1, int(counts["reps"] * adjustment_factor))  # Ensure at least 1 rep
        adjusted_workouts[activity] = {"sets": adjusted_sets, "reps": adjusted_reps}

    return adjusted_workouts

@app.route('/')
def my_form():
    return render_template(template)

@app.route('/', methods=['POST'])
def my_form_post():
    userName = request.form['inputUserName']
    password = request.form['inputPassword']
    if validate_user(userName, password) == False:
     return redirect(url_for('failed'))
    else:
     return redirect(url_for('bmi', userName=userName))
    
@app.route('/bmi')
def bmi():
    userName = request.args.get('userName')
    if userName is None or userName == '':
        return 'Not authorized!'
    else:
        return render_template('bmi.html', userName=userName)

@app.route('/bmi', methods=['POST'])
def bmi_post():
    height = int(request.form['height'])
    weight = int(request.form['weight'])
    fitness = request.form['fitness']
    userName = request.form['userName']
    height_m = height / 100
    bmi_value = round(weight / (height_m ** 2), 2)
    if bmi_value < 18.5:
        bmi_category = "underweight"
    elif 18.5 <= bmi_value < 24.9:
        bmi_category = "normal"
    elif 25 <= bmi_value < 29.9:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"
    
    workout_plan = recommend_workouts(bmi_category, fitness)
    workoutList = []
    workOutDetail = ""
    for activity, counts in workout_plan.items():
        if activity == 'walking':
            workoutList.append(f"{activity.capitalize()}: {counts['reps']} minutes")
        else:
            workoutList.append(f"{activity.capitalize()}: {counts['sets']} sets of {counts['reps']} reps")

    for e in workoutList:
        workOutDetail+= e+'|'
    
    print(userName)
    return redirect(url_for('bmiresult', data=bmi_value, bmi_category=bmi_category,fitness=fitness,workout_plan=workout_plan, workOutDetail=workOutDetail,userName=userName))

@app.route('/bmiresult')
def bmiresult():
    userName = request.args.get('userName')
    if userName is None or userName == '':
        return 'Not authorized!'
    else:
        return render_template('bmiresult.html', bmi_value=request.args.get('data'), bmi_category=request.args.get('bmi_category'), fitness_level=request.args.get('fitness'), workout_plan=request.args.get('workout_plan'), workOutDetail=request.args.get('workOutDetail'),userName=userName)

@app.route('/failed')
def failed():
   return 'Login Failed!'

if __name__ == '__main__':
    app.run(debug=True)