from flask import Flask, render_template, request, redirect, url_for
from models import db, Student, Batch, Coach, ScheduleEntry, WaitingStudent, PerformanceScore
from datetime import date, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///badminton.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# -------------------- Home --------------------
@app.route('/')
def index():
    return render_template('base.html')

# -------------------- Batches --------------------
@app.route('/batches')
def batches():
    batches = Batch.query.all()
    return render_template('batches.html', batches=batches)

@app.route('/add_batch', methods=['POST'])
def add_batch():
    bid = request.form['bid']
    fees = float(request.form['fees']) if request.form['fees'] else 0
    location = request.form['location']

    new_batch = Batch(bid=bid, fees=fees, location=location)
    db.session.add(new_batch)
    db.session.commit()
    return redirect(url_for('batches'))

@app.route('/delete_batch/<string:batch_id>', methods=['POST'])
def delete_batch(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    db.session.delete(batch)
    db.session.commit()
    return redirect(url_for('batches'))

# -------------------- Students --------------------
@app.route('/students', methods=['GET'])
def students():
    name_filter = request.args.get('name', '')
    batch_filter = request.args.get('batch_id', '')
    location_filter = request.args.get('location', '')

    query = Student.query.join(Batch)

    if name_filter:
        query = query.filter(Student.name.ilike(f'%{name_filter}%'))
    if batch_filter:
        query = query.filter(Student.batch_id.ilike(f'%{batch_filter}%'))
    if location_filter:
        query = query.filter(Batch.location.ilike(f'%{location_filter}%'))

    students = query.all()
    batches = Batch.query.all()

    return render_template('students.html', students=students, batches=batches, filters={
        'name': name_filter,
        'batch_id': batch_filter,
        'location': location_filter
    })

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = int(request.form['age']) if request.form['age'] else None
    gender = request.form['gender']
    contact = request.form['contact']
    batch_id = request.form['batch_id']

    new_student = Student(name=name, age=age, gender=gender, contact=contact, batch_id=batch_id)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('students'))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))




@app.route('/performance/<int:student_id>', methods=['GET', 'POST'])
def performance(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        test1 = int(request.form['test1']) if request.form['test1'] else None
        test2 = int(request.form['test2']) if request.form['test2'] else None
        test3 = int(request.form['test3']) if request.form['test3'] else None

        score_entry = PerformanceScore(
            student_id=student.id,
            date=date.today(),
            test1=test1,
            test2=test2,
            test3=test3
        )
        db.session.add(score_entry)
        db.session.commit()
        return redirect(url_for('performance', student_id=student.id))

    scores = PerformanceScore.query.filter_by(student_id=student.id).order_by(PerformanceScore.date.desc()).all()
    return render_template('performance.html', student=student, scores=scores)

# -------------------- Coaches --------------------
@app.route('/coaches', methods=['GET', 'POST'])
def coaches():
    if request.method == 'POST':
        name = request.form['name']
        batch_id = request.form['batch_id']
        supervisor_id = request.form.get('supervisor_id') or None
        salary = request.form.get('salary')

        salary_val = float(salary) if salary else None

        new_coach = Coach(
            name=name,
            batch_id=batch_id,
            supervisor_id=int(supervisor_id) if supervisor_id else None,
            salary=salary_val
        )
        db.session.add(new_coach)
        db.session.commit()
        return redirect(url_for('coaches'))

    coaches = Coach.query.all()
    batches = Batch.query.all()
    return render_template('coach.html', coaches=coaches, batches=batches)

@app.route('/delete_coach/<int:coach_id>', methods=['POST'])
def delete_coach(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    db.session.delete(coach)
    db.session.commit()
    return redirect(url_for('coaches'))


@app.route('/waitingstudents', methods=['GET', 'POST'])
def waitingstudents():
    locations = [loc[0] for loc in db.session.query(Batch.location).distinct().all()]
    
    selected_location = request.args.get('location', '')
    selected_batch = request.args.get('batch', '')

    batches = []
    waiting_students = []

    if selected_location:
        batches = Batch.query.filter_by(location=selected_location).all()
        if selected_batch:
            waiting_students = WaitingStudent.query.filter_by(batch_id=selected_batch).all()
        else:
            
            batch_ids = [b.bid for b in batches]
            waiting_students = WaitingStudent.query.filter(WaitingStudent.batch_id.in_(batch_ids)).all()

    return render_template('waitingstudents.html',
                           locations=locations,
                           batches=batches,
                           waiting_students=waiting_students,
                           selected_location=selected_location,
                           selected_batch=selected_batch)


@app.route('/add_waitingstudent', methods=['POST'])
def add_waitingstudent():
    name = request.form['name']
    contact = request.form['contact']
    batch_id = request.form['batch_id']

    new_waiting = WaitingStudent(name=name, contact=contact, batch_id=batch_id)
    db.session.add(new_waiting)
    db.session.commit()
    return redirect(url_for('waitingstudents', location=request.form.get('location', ''), batch=batch_id))

# Delete waiting student
@app.route('/delete_waitingstudent/<int:id>', methods=['POST'])
def delete_waitingstudent(id):
    ws = WaitingStudent.query.get_or_404(id)
    location = ws.batch.location
    db.session.delete(ws)
    db.session.commit()
    return redirect(url_for('waitingstudents', location=location, batch=ws.batch_id))

# Move waiting student to students
@app.route('/move_to_students/<int:id>', methods=['POST'])
def move_to_students(id):
    ws = WaitingStudent.query.get_or_404(id)
    location = ws.batch.location
    # Get student info from waiting student
    name = ws.name
    contact = ws.contact
    batch_id = request.form['batch_id']  # batch selected on form

    # Create new student
    new_student = Student(name=name, age=None, gender='', contact=contact, batch_id=batch_id)
    db.session.add(new_student)

    # Delete from waiting list
    db.session.delete(ws)
    db.session.commit()

    return redirect(url_for('waitingstudents', location=ws.batch.location, batch=batch_id))


from datetime import datetime

@app.route('/schedules', methods=['GET', 'POST'])
def schedules():
    if request.method == 'POST':
        batch_id = request.form['batch_id']
        day_of_week = request.form['day_of_week']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        location = request.form['location']

        # Convert time strings to datetime.time objects
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        new_entry = ScheduleEntry(
            batch_id=batch_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('schedules', location=location))
    
    selected_location = request.args.get('location', '')
    locations = [loc[0] for loc in db.session.query(Batch.location).distinct().all()]
    batches = []
    schedules = []

    if selected_location:
        batches = Batch.query.filter_by(location=selected_location).all()
        batch_ids = [b.bid for b in batches]
        schedules = ScheduleEntry.query.filter(ScheduleEntry.batch_id.in_(batch_ids)).all()

    return render_template('schedules.html',
                           locations=locations,
                           selected_location=selected_location,
                           batches=batches,
                           schedules=schedules)

@app.route('/delete_schedule/<int:id>', methods=['POST'])
def delete_schedule(id):
    entry = ScheduleEntry.query.get_or_404(id)
    location = request.form.get('location', '')
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('schedules', location=location))



# -------------------- Run App --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host = "0.0.0.0",port =5000, debug=True)
