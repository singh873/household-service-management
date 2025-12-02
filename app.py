from flask import Flask,render_template,request,redirect,url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
from datetime import datetime
import matplotlib.pyplot as plt
app=Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
db = SQLAlchemy(app)


class User(db.Model):
    User_Id = db.Column(db.Integer, primary_key=True)
    Role = db.Column(db.String(15), nullable=False)
    Email = db.Column(db.String(60), unique=True, nullable=False)
    Password = db.Column(db.String(40), nullable=False)
    Full_name = db.Column(db.String(50))
    Status = db.Column(db.String(10),default='pending')
    Is_approved = db.Column(db.Boolean, default=False)
    Pin_code = db.Column(db.Integer)
    Experience = db.Column(db.Integer)
    Address = db.Column(db.String(100))
    Service_id = db.Column(db.Integer, db.ForeignKey('service.Service_Id'))
    Requests = db.relationship('Service_Request',backref='customer',cascade="all, delete",foreign_keys='Service_Request.Customer_id')
    ProfessionalRequests = db.relationship('Service_Request',backref='professional',cascade="all, delete",foreign_keys='Service_Request.Professional_id')



class Service(db.Model):
    Service_Id = db.Column(db.Integer, primary_key=True)
    Name_of_service = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Professionals=db.relationship('User', backref='service',cascade="all, delete")
    Requests=db.relationship('Service_Request', backref='service',cascade="all, delete")
    
class Service_Request(db.Model):
    Service_Request_Id = db.Column(db.Integer, primary_key=True)
    Customer_id = db.Column(db.Integer,db.ForeignKey('user.User_Id'),nullable=False)
    Professional_id = db.Column(db.Integer,db.ForeignKey('user.User_Id'),nullable=True)
    Service_id = db.Column(db.Integer,db.ForeignKey('service.Service_Id'),nullable=False)
    Requested_date = db.Column(db.Date, default=datetime.utcnow)
    Completion_date = db.Column(db.Date)
    Status = db.Column(db.String(20),default='Requested') 
    Rating = db.Column(db.Integer, nullable=True)
    



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    admin=User.query.filter_by(Role='admin').first()
    if not admin:
        new_admin=User(Role='admin',Email='sudhanshu@gmail.com',Password='kumar',Full_name='sudhanshu_kumar',Pin_code=1234,Is_approved=True,Status='Active')
        db.session.add(new_admin)
        db.session.commit()

    if request.method=='GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(Email=email, Password=password).first()
        if user:
            if not user.Is_approved:
                flash('Your account is under verification.', 'error')
                return redirect(url_for('login'))
            else:
                if user.Status == 'Blocked':
                    flash('Your account has been blocked.', 'error')
                    return redirect(url_for('login'))
                else:
        
                    session['user_id'] = user.User_Id
                    if user.Role == 'customer':
                        return redirect(url_for('customer_dashboard'))
                    elif user.Role == 'professional':
                        return redirect(url_for('professional_dashboard'))
                    elif user.Role == 'admin':
                        return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login')) 
   

@app.route('/professional_signup', methods=['GET', 'POST'])
def professional_signup():
    services=Service.query.all()
    
    if request.method=='GET':
        return render_template('professional_signup.html',services=services)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        service = Service.query.filter_by(Name_of_service=request.form['service_name']).first()
        service_id =service.Service_Id
        experience = request.form['experience']
        address = request.form['address']
        pincode = request.form['pincode']
        user=User.query.filter_by(Email=email).first()
        if user:
            flash('Account with this Email already exists', 'error')
            return redirect(url_for('professional_signup'))
        new_user=User(Role='professional',Email=email,Password=password,Full_name=full_name,Service_id=service_id,Experience=experience,Address=address,Pin_code=pincode,Is_approved=False)
        db.session.add(new_user)
        db.session.commit()
        if new_user.Is_approved:
            return redirect(url_for('professional_dashboard'))
        else:
            flash('Your account is under verification', 'error')
            return redirect(url_for('login'))
        

    


@app.route('/professional_dashboard')
def professional_dashboard():
    user_id = session.get('user_id')
    user=User.query.filter_by(User_Id=user_id,Role='professional').first()
    if not session['user_id'] or not user:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))
    Service_Requests=Service_Request.query.filter_by(Professional_id=user_id).all()
    if not user_id:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))
    return render_template('professional_dashboard.html',requests=Service_Requests,user=user)

@app.route('/service_details/<int:service_id>')
def service_details(service_id):
    service=Service.query.filter_by(Service_Id=service_id).first()
    service_requests= Service_Request.query.filter_by(Service_id=service_id).all()
    return render_template('service_details.html', Service_Request=service_requests,service=service)

@app.route('/accept_request/<int:request_id>')
def accept_request(request_id):
    request = Service_Request.query.filter_by(Service_Request_Id=request_id).first()
    if request:
        request.Status = 'Accepted'
        db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/reject_request')
def reject_request():
    request_id = request.args.get('request_id')
    requests = Service_Request.query.filter_by(Service_Request_Id=request_id).first()
    if requests:
        requests.Status = 'Rejected'
        db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/professional_details/<int:user_id>')
def professional_details(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    service_requests= Service_Request.query.filter_by(Professional_id=user_id).all()
    if not session['user_id'] or not user:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))

    return render_template('professional_details.html',user=user,service_requests=service_requests)

@app.route('/professional_edit_profile/<int:user_id>',methods=['GET','POST'])
def professional_edit_profile(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    if not session['user_id'] or not user:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))
    if request.method=='GET':
        return render_template('professional_edit_profile.html',professional=user)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        experience = request.form['experience']
        address = request.form['address']
        pincode = request.form['Pin_code']
        user=User.query.filter_by(User_Id=user_id).first()
        user.Email=email
        user.Password=password
        user.Full_name=full_name
        user.Experience=experience
        user.Address=address
        user.Pin_code=pincode
        db.session.commit()
        return redirect(url_for('professional_dashboard'))


    

@app.route('/professional_dashboard_search/<string:professional_id>', methods=['GET', 'POST'])
def professional_dashboard_search(professional_id):
    results = None  
    error = None  
    user=User.query.filter_by(User_Id=professional_id).first()

    if request.method == 'POST':
       
        search_criteria = request.form.get('search_criteria')
        query = request.form.get('query')

        try:
            if search_criteria == 'service_request_id':
               
                query = int(query)  
                results = Service_Request.query.filter(
                    Service_Request.Service_Request_Id == query,
                    Service_Request.Professional_id == professional_id
                ).all()
            elif search_criteria == 'customer_id':
                # Search by Customer_ID
                query = int(query)  # Ensure query is an integer
                results = Service_Request.query.filter(
                    Service_Request.Customer_id == query,
                    Service_Request.Professional_id == professional_id
                ).all()
            elif search_criteria == 'status':
                # Search by Status (case-insensitive)
                results = Service_Request.query.filter(
                    Service_Request.Status.ilike(f"%{query}%"),
                    Service_Request.Professional_id == professional_id
                ).all()
            elif search_criteria == 'date':
                # Search by Requested Date
                search_date = datetime.strptime(query, '%Y-%m-%d').date()  # Parse date
                results = Service_Request.query.filter(
                    func.date(Service_Request.Requested_date) == search_date,
                    Service_Request.Professional_id == professional_id
                ).all()

            # Handle case where no results are found
            if not results:
                error = f"No results found for '{query}' for Professional ID {professional_id}."

        except ValueError:
            # Handle invalid input (e.g., incorrect format or non-integer)
            error = "Invalid input. Ensure the query matches the selected search type."

    return render_template(
        'professional_dashboard_search.html',
        user=user,
        results=results,
        error=error,
        query=query if request.method == 'POST' else None,
        search_criteria=search_criteria if request.method == 'POST' else None,
        professional_id=professional_id  # Pass Professional_Id to the template
    )


def service_request_status(Professional_id):
    service_requests = Service_Request.query.filter_by(Professional_id=Professional_id).all() 
    rejected=0
    completed=0
    accepted=0
    requested=0
    for request in service_requests:
        if request.Status == 'Rejected':
            rejected += 1
        elif request.Status == 'Completed':
            completed += 1
        elif request.Status == 'Accepted':
            accepted+= 1
        elif request.Status == 'Requested':
            requested += 1
    return rejected,completed,accepted,requested
def rating_count(Professional_id):
    service_requests = Service_Request.query.filter_by(Professional_id=Professional_id).all() 
    one_star = 0
    two_star = 0
    three_star = 0
    four_star = 0
    five_star = 0
    for request in service_requests:
        if request.Rating == 1:
            one_star += 1
        elif request.Rating == 2:
            two_star += 1
        elif request.Rating == 3:
            three_star += 1
        elif request.Rating == 4:
            four_star += 1
        elif request.Rating == 5:
            five_star += 1
    return one_star, two_star, three_star, four_star, five_star

  
@app.route('/professional_dashboard_summary/<int:professional_id>', methods=['GET', 'POST'])
def professional_dashboard_summary(professional_id):
    user=User.query.filter_by(User_Id=professional_id).first()
    image_folder = os.path.join('static', 'images')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # ----- Generate Pie Chart for Service Requests Status -----
    rejected, completed, accepted, requested = service_request_status(professional_id)

    # Data for the pie chart

    labels_status = ['Rejected', 'Completed', 'Accepted', 'Requested']
    sizes_status = [rejected, completed, accepted, requested]
    colors_status = ['red', 'green', 'blue', 'orange']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes_status, labels=labels_status, colors=colors_status, autopct='%1.1f%%', startangle=140)
    plt.title("Service Requests Status Distribution")
    status_image_path = os.path.join(image_folder, f'service_requests_status_{professional_id}.png')
    plt.savefig(status_image_path)
    plt.clf()

    # ----- Generate Bar Chart for Service Ratings -----
    one_star, two_star, three_star, four_star, five_star = rating_count(professional_id)

    # Data for the bar chart
    ratings = [one_star, two_star, three_star, four_star, five_star]
    stars = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']

    plt.figure(figsize=(8, 6))
    plt.bar(stars, ratings, color=['red', 'orange', 'yellow', 'green', 'blue'])
    plt.title("Service Ratings Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Ratings")
    ratings_image_path = os.path.join(image_folder, f'service_ratings_{professional_id}.png')
    plt.savefig(ratings_image_path)
    plt.clf()

    # ----- Return the Template with Both Images -----
    return render_template(
        "professional_dashboard_summary.html",
        user=user,

        status_image=f'images/service_requests_status_{professional_id}.png',
        ratings_image=f'images/service_ratings_{professional_id}.png'
    )

    

@app.route('/customer_signup',methods=['POST','GET'])
def customer_signup():
    if request.method=='GET':
        return render_template('customer_signup.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        pincode = request.form['pincode']
        user=User.query.filter_by(Email=email).first()
        if user:
            flash('Account with this Email already exists', 'error')
            return redirect(url_for('customer_signup'))
        new_user=User(Role='customer',Email=email,Password=password,Full_name=full_name,Address=address,Pin_code=pincode,Is_approved=True,Status='Active')
        db.session.add(new_user)
        db.session.commit()
        flash('Account Created Successfully', 'success')
        return redirect(url_for('login'))        


@app.route('/customer_dashboard')
def customer_dashboard():
    user_id = session['user_id']
    user=User.query.filter_by(User_Id=user_id,Role='customer').first()
    if not session['user_id'] or not user:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))

    # Fetch requests for the logged-in customer
    services=Service.query.all()
    requests = Service_Request.query.filter_by(Customer_id=user_id).all()
    return render_template('customer_dashboard.html', requests=requests,user=user,services=services)

@app.route('/customer_edit_profile/<int:user_id>',methods=['GET','POST'])
def customer_edit_profile(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    if not session['user_id'] or not user:
        flash('Login Now.', 'error')
        return redirect(url_for('login'))
    if request.method=='GET':
        return render_template('customer_edit_profile.html',customer=user)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        pincode = request.form['pincode']
        user=User.query.filter_by(User_Id=user_id).first()
        user.Email=email
        user.Password=password
        user.Full_name=full_name
        user.Address=address
        user.Pin_code=pincode
        db.session.commit()
        return redirect(url_for('customer_dashboard'))

@app.route('/request_professional/<int:service_id>/<int:professional_id>', methods=['POST'])
def request_professional(service_id, professional_id):
    user_id = session.get('user_id')  # Get the logged-in user's ID
    if not user_id:
        flash('You need to log in to request a service.', 'error')
        return redirect(url_for('login'))

    # Create a new service request
    new_request = Service_Request(Customer_id=user_id,Professional_id=professional_id,Service_id=service_id,Status='Requested')
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('customer_dashboard'))

@app.route('/Available_services<service_name>',methods=['GET','POST'])
def Available_services(service_name):
    services=Service.query.filter_by(Name_of_service=service_name).all()
    return render_template('Available_service.html',services=services)

@app.route('/close_request/<int:request_id>',methods=['GET','POST'])
def close_request(request_id):
    request=Service_Request.query.filter_by(Service_Request_Id=request_id).first()
    if request:
        request.Status='Completed'
        db.session.commit()
    return render_template('rating.html',service_request=request)


@app.route('/submit_remarks/<int:request_id>', methods=['POST'])
def submit_remarks(request_id):
    # Retrieve the request from the database
    service_request = Service_Request.query.get_or_404(request_id)
    
    # Get form data
    rating = request.form.get('rating')
    remarks = request.form.get('remarks')

    # Update the service request
    service_request.Status = 'Completed'
    service_request.Rating = rating
    service_request.Remarks = remarks
    db.session.commit()

    return redirect(url_for('customer_dashboard'))

@app.route('/customer_details/<int:user_id>')
def customer_details(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    service_requests= Service_Request.query.filter_by(Customer_id=user_id).all()
    return render_template('customer_details.html',user=user,service_requests=service_requests)

@app.route('/search_customer', methods=['GET', 'POST'])
def customer_dashboard_search():
    if request.method == 'GET':
        return render_template('customer_dashboard_search.html')  # Render the search form
    
    elif request.method == 'POST':
        # Get the search criteria from the form
        query = request.form.get('query')
        search_criteria = request.form.get('search_criteria')
        
        results = []  # Initialize an empty results list

        # Perform search based on the selected criteria
        if search_criteria == 'name':
            results = User.query.filter(
                (User.Role == 'professional') & User.Full_name.ilike(f"%{query}%")
            ).all()
        elif search_criteria == 'address':
            results = User.query.filter(
                (User.Role == 'professional') & User.Address.ilike(f"%{query}%")
            ).all()
        elif search_criteria == 'pincode':
            results = User.query.filter(
                (User.Role == 'professional') & User.Pin_code.ilike(f"%{query}%")
            ).all()

        # Render the results on the same search page
        return render_template('customer_dashboard_search.html', results=results, query=query, search_criteria=search_criteria)


def service_name_count(customer_id):
    service_requests = Service_Request.query.filter_by(Customer_id=customer_id).all() 
    service_names = {}
    for request in service_requests:
        service_name = request.service.Name_of_service
        if service_name in service_names:
            service_names[service_name] += 1
        else:
            service_names[service_name] = 1
    return service_names


@app.route("/service_name_summary/<int:customer_id>")
def generate_service_name_pie_chart(customer_id):
    # Ensure the 'static/images' directory exists
    image_folder = os.path.join('static', 'images')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # Call the service_name_count function to get data
    service_data = service_name_count(customer_id)

    # Data for the pie chart
    labels = list(service_data.keys())
    sizes = list(service_data.values())
    colors = plt.cm.tab20.colors[:len(labels)]  # Use a colormap to generate colors

    # Create the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title(f"Service Name Distribution for Customer {customer_id}")

    # Save the pie chart
    pie_chart_path = os.path.join(image_folder, 'service_name_summary.png')
    plt.savefig(pie_chart_path)
    plt.clf()  # Clear the figure after saving

    return render_template('customer_dashboard_summary.html', pie_chart=f'service_name_summary_{customer_id}.png')

    


 
    
@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
    Service_Requests=Service_Request.query.all()
    admin=User.query.filter_by(Role='admin',User_Id=session['user_id']).first()

    if session['user_id'] and admin:
        services=Service.query.all()
        Users = User.query.filter_by(Role='professional').filter(User.Status.in_(['Active', 'Blocked'])).all()
        customers = User.query.filter_by(Role='customer').filter(User.Status.in_(['Active', 'Blocked'])).all()

        pending_users = User.query.filter_by(Status='pending').all()

        if admin:
            return render_template('admin_dashboard.html',services=services,Users=Users,Service_Requests=Service_Requests,pending_users=pending_users,customers=customers)
        else:
            flash('You need to log in as an admin to access this page.', 'error')
            return redirect(url_for('login'))

    else:
        flash('You need to log in as an admin to access this page.', 'error')
        return redirect(url_for('login'))   



@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    user = User.query.filter_by(User_Id=user_id).first()
    if user:
        user.Is_approved = True
        user.Status = 'Active'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_user/<int:user_id>')
def reject_user(user_id):
    user = User.query.filter_by(User_Id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))
    

@app.route('/admin_dashboard/add_service',methods=['GET','POST'])
def add_service():
    if request.method=='GET':
        return render_template('add_service.html')
    if request.method == 'POST':
        service_name = request.form['service_name']
        description = request.form['description']
        base_price = request.form['base_price']
        new_service=Service(Name_of_service=service_name,Description=description,Price=base_price)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    



@app.route('/admin_dashboard/edit_service<int:service_id>',methods=['GET','POST'])   
def edit_service(service_id):
    service=Service.query.filter_by(Service_Id=service_id).first()
    if request.method=='GET':
        return render_template('edit_service.html',service=service)
    if request.method == 'POST':
        service_name = request.form['service_name']
        description = request.form['description']
        base_price = request.form['base_price']
        service=Service.query.filter_by(Service_Id=service_id).first()
        service.Name_of_service=service_name
        service.Description=description
        service.Price=base_price
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
   

@app.route('/admin_dashboard/delete_service/<int:service_id>',methods=['POST','GET'])
def delete_service(service_id):
    
    service=Service.query.filter_by(Service_Id=service_id).first()
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_users/<int:user_id>',methods=['POST','GET'])
def delete_users(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/block_user/<int:user_id>',methods=['GET','POST'])
def block_user(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    user.Status='Blocked'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/unblock_user/<int:user_id>',methods=['GET','POST'])
def unblock_user(user_id):
    user=User.query.filter_by(User_Id=user_id).first()
    user.Status='Active'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_dashboard/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        search_type = request.form.get('search_type')
        query = request.form.get('query')
        results = []

        if search_type == 'service':
            results = Service.query.filter(Service.Name_of_service.contains(query)).all()
        elif search_type == 'professional':
            results = User.query.filter(
                (User.Role == 'professional') &
                (
                    User.Full_name.contains(query) |
                    User.Pin_code.contains(query) |
                    User.Address.contains(query)
                )
            ).all()
        elif search_type == 'customer':
            results = User.query.filter(
                (User.Role == 'customer') &
                (
                    User.Full_name.contains(query) |
                    User.Pin_code.contains(query) |
                    User.Address.contains(query)
                )
            ).all()

        print(f"Search Type: {search_type}")
        print(f"Results: {results}")

        return render_template('search.html', results=results, search_type=search_type)


def service_requests_data():
    service_requests = Service_Request.query.all()
    rejected=0
    completed=0
    accepted=0
    requested=0
    for request in service_requests:
        if request.Status == 'Rejected':
            rejected += 1
        elif request.Status == 'Completed':
            completed += 1
        elif request.Status == 'Accepted':
            accepted+= 1
        elif request.Status == 'Requested':
            requested += 1
    return rejected,completed,accepted,requested



def survice_rating_summary():
    service_requests = Service_Request.query.all()
    one_star = 0
    two_star = 0
    three_star = 0
    four_star = 0
    five_star = 0
    for request in service_requests:
        if request.Rating == 1:
            one_star += 1
        elif request.Rating == 2:
            two_star += 1
        elif request.Rating == 3:
            three_star += 1
        elif request.Rating == 4:
            four_star += 1
        elif request.Rating == 5:
            five_star += 1
    return one_star, two_star, three_star, four_star, five_star

@app.route("/rating_summary")
def generate_rating_graph():
    try:
        # Ensure the 'static/images' directory exists
        image_folder = os.path.join('static', 'images')
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # ----- Generate Bar Chart for Service Ratings -----
        # Call the existing summary function
        one_star, two_star, three_star, four_star, five_star = survice_rating_summary()

        # Data for the bar chart
        ratings = [one_star, two_star, three_star, four_star, five_star]
        stars = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']

        # Create the bar chart
        plt.figure(figsize=(8, 6))
        plt.bar(stars, ratings, color=['red', 'orange', 'yellow', 'green', 'blue'])
        plt.title("Service Rating Summary")
        plt.xlabel("Rating")
        plt.ylabel("Number of Ratings")

        # Save the bar chart
        rating_image_path = os.path.join(image_folder, 'service_rating_summary.png')
        plt.savefig(rating_image_path)
        plt.clf()  # Clear figure after saving

        # ----- Generate Pie Chart for Service Requests -----
        rejected, completed, accepted,requested = service_requests_data()

        # Data for the pie chart
        labels = ['Rejected', 'Completed', 'Accepted','Requested']
        sizes = [rejected, completed,accepted,requested]
        colors = ['red', 'green', 'blue', 'orange']

        # Create the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title("Service Requests Status Distribution")

        # Save the pie chart
        request_image_path = os.path.join(image_folder, 'service_requests_summary.png')
        plt.savefig(request_image_path)
        plt.clf()  # Clear figure after saving



        # ----- Return the Template with Both Images -----
        return render_template(
            "admin_summary.html",
            rating_image="images/service_rating_summary.png",
            request_image="images/service_requests_summary.png"
        )

    except Exception as e:
        return "<h1>Data is not available</h1>"

    









if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
