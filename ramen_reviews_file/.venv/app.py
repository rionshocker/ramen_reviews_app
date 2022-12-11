from dataclasses import Field
from flask import Flask, abort, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, HiddenField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY']='bluebearisthebest'
db_name = 'ramen-ratings.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
Bootstrap(app)

categories = {"reviews": "View, Search, Edit and Delete Reviews", "countries": "Filter Reviews", "submitform": "Submit a Review!"}

class Ramen(db.Model):
    __tablename__ = 'ramen-ratings'
    Index = db.Column(db.Integer, primary_key=True, autoincrement = True)
    ID = db.Column(db.Integer)
    Country = db.Column(db.String)
    Brand = db.Column(db.String)
    Type = db.Column(db.String)
    Package = db.Column(db.String)
    Rating = db.Column(db.Float)

    def __init__(self, ID, Country, Brand, Type, Package, Rating):
        self.ID = ID
        self.Country = Country
        self.Brand = Brand
        self.Type = Type
        self.Package = Package
        self.Rating = Rating

class AddRecord(FlaskForm):
    Index_field = HiddenField()
    ID_field = HiddenField()
    Country = SelectField('Choose the country', [ InputRequired()], choices=[ ('', ''), ('IDN', 'IDN'), ('KOR', 'KOR'), ('JPN', 'JPN'), ('SGP', 'SGP'), ('THA', 'THA'), ('USA', 'USA'), ('TWN', 'TWN'), ('HKG', 'HKG'), ('VNM', 'VNM'), ('Ghana', 'Ghana'), ('MYS', 'MYS'), ('CHN', 'CHN'), ('NGA', 'NGA'), ('DEU', 'DEU'), ('HUN', 'HUN'), ('MEX', 'MEX'), ('FJI', 'FJI'), ('AUS', 'AUS'), ('PAK', 'PAK'), ('BGD', 'BGD'), ('CAN', 'CAN'), ('NPL', 'NPL'), ('BRA', 'BRA'), ('UK', 'UK'), ('MMR', 'MMR'), ('NLD', 'NLD'), ('KHM', 'KHM'), ('FIN', 'FIN'), ('PHL', 'PHL'), ('SWE', 'SWE'), ('COL', 'COL'), ('EST', 'EST'), ('POL', 'POL'), ('ARE', 'ARE') ])
    Brand = SelectField('Select the brand', [ InputRequired()], choices=[ ('', ''), ('Brand A', 'Brand A'), ('Brand B', 'Brand B'), ('Brand C', 'Brand C'), ('Brand D', 'Brand D'), ('Brand E', 'Brand E'), ('Brand F', 'Brand F'), ('Brand G', 'Brand G'), ('Brand M', 'Brand M')])
    Type = StringField('Noodle Type', [ InputRequired(), Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Type Name"), Length(min=3, message="Invalid type name length")])
    Package = SelectField('Select Package Type', [ InputRequired()], choices=[ ('', ''), ('Cup', 'Cup'), ('Pack', 'Pack'), ('Tray', 'Tray'), ('Bowl', 'Bowl'), ('Can', 'Can'), ('Box', 'Box')  ])
    Rating = FloatField('Rating to give (out of 5.0)', [ InputRequired(), NumberRange(min=1.0, max=5.0, message="Invalid Rating")])
    submit = SubmitField('Add/Update Review')

class ReviewSearchForm(FlaskForm):
    search = StringField('Search Reviews', validators=[InputRequired()])
    submit = SubmitField('Search') 

class DeleteRecord(FlaskForm):
    Index_field = HiddenField()
    purpose = HiddenField()
    submit = SubmitField('Delete This Review')

@app.route('/')
def index():
    return render_template('home.html', categories=categories)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():   
    search_Form = ReviewSearchForm()
    ramens = Ramen.query
    if search_Form.validate_on_submit():
        word = search_Form.search.data
        ramens = Ramen.query.filter(Ramen.Type.ilike('%' + word + '%')).all()
        return render_template('reviews.html', ramens=ramens, search_Form=search_Form)
    else:
        return render_template('reviews.html', ramens=ramens, search_Form=search_Form)

@app.route('/countries')
def countries():
    Country=Ramen.query.with_entities(Ramen.Country).distinct()
    return render_template('countries.html', Country=Country)

@app.route('/country/<Country>')
def country(Country):
    ramens = Ramen.query.filter_by(Country=Country).order_by(Ramen.ID).all()
    return render_template('country.html', ramens=ramens, Country=Country)

@app.route('/submitform', methods=['GET', 'POST'])
def submitform():
    form1 = AddRecord()

    if form1.validate_on_submit():
        ID = (len(Ramen.query.all()) + 1)
        Country = request.form['Country']
        Brand = request.form['Brand']
        Type = request.form['Type']
        Package = request.form['Package']
        Rating = request.form['Rating']
        record = Ramen(ID, Country, Brand, Type, Package, Rating)
        db.session.add(record)
        db.session.commit()
        message = f"The data for ramen {Type} of {Brand} from {Country} has been submitted."
        return render_template('submitform.html', message=message)
    else:
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('submitform.html', form1=form1)

@app.route('/edit_or_delete', methods=['POST'])
def edit_or_delete():
    Index = request.form['Index']
    choice = request.form['choice']
    ramen = Ramen.query.filter(Ramen.Index == Index).first()
    form1 = AddRecord()
    form2 = DeleteRecord()
    return render_template('edit_or_delete.html', ramen=ramen, form1=form1, form2=form2, choice=choice)

@app.route('/delete_result', methods=['GET','POST'])
def delete_result():
    Index = request.form['Index_field']
    purpose = request.form['purpose']
    ramen = Ramen.query.filter(Ramen.Index == Index).first()
    if purpose == 'delete':
        db.session.delete(ramen)
        db.session.commit()
        message = f"The review {ramen.Index} has been deleted successfully."
        return render_template('result.html', message=message)
    else:
        abort(405)

@app.route('/edit_result', methods=['GET','POST'])
def edit_result():
    Index = request.form['Index_field']
    ramen = Ramen.query.filter(Ramen.Index == Index).first()
    ramen.Country = request.form['Country']
    ramen.Brand = request.form['Brand']
    ramen.Type = request.form['Type']
    ramen.Package = request.form['Package']
    ramen.Rating = request.form['Rating']

    form1 = AddRecord()
    if form1.validate_on_submit():
        db.session.commit()
        message = f"Review for {ramen.Type} of {ramen.Brand} has been updated."
        return render_template('result.html', message=message)
    else:
        ramen.index =index
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(getattr(form1, field).label.text,error), 'error')
        return render_template('edit_or_delete.html', form1-form1, ramen=ramen, choice='edit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page not Found", pageheading="Page not found (Error 404)", error=e),404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form not Submitted", pageheading="The form was not submitted (Error 405)", error=e),405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e),505

if __name__ == '__main__':
    app.run(debug=True)