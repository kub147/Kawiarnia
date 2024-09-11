from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import time


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach', True)
chrome_options.add_argument("--disable-search-engine-choice-screen")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class CafeFormAuto(FlaskForm):
    cafe_auto = StringField('Cafe name automaticly', validators=[DataRequired()])
    submit = SubmitField('Search')




class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe location on Google Maps URL', validators=[DataRequired(), URL(message='invalid URL')])
    ocena = StringField('Google stars', validators=[DataRequired()])
    ceny = StringField('Google prices', validators=[DataRequired()])
    open = StringField('Opening Time e.g. 8AM', validators=[DataRequired()])
    close = StringField('Closing Time e.g. 6PM', validators=[DataRequired()])
    coffee = SelectField('Coffee Rating', validators=[DataRequired()], choices=['☕️', '☕️ ☕️', '☕️ ☕️ ☕️', '☕️ ☕️ ☕️ ☕️', '☕️ ☕️ ☕️ ☕️ ☕️'], default=1)
    wifi = SelectField('Wifi Strenght Rating', validators=[DataRequired()], choices=['✘', '💪', '💪 💪', '💪 💪 💪', '💪 💪 💪 💪', '💪 💪 💪 💪 💪'], default=1)
    power = SelectField('Power Socket Availability', validators=[DataRequired()], choices=['✘', '🔌', '🔌 🔌', '🔌 🔌 🔌', '🔌 🔌 🔌 🔌', '🔌 🔌 🔌 🔌 🔌'], default=1)
    komm = StringField('A few words about it ...')
    submit = SubmitField('Submit')




# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form_auto = CafeFormAuto()
    form = CafeForm()

    if form_auto.validate_on_submit():
        name = form_auto.cafe_auto.data
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.google.pl/maps')
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button').click()
        time.sleep(2)

        # Search for the cafe
        search_box = driver.find_element(By.XPATH, '//*[@id="searchboxinput"]')
        search_box.send_keys(name, Keys.ENTER)
        time.sleep(6)  # Wait for results to load

        # Scrape rating, price, and other details
        ocena = driver.find_element(By.XPATH,
                                    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]').text
        cena = driver.find_element(By.XPATH,
                                   '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/span/span/span/span[2]/span/span').text
        # godziny = driver.find_element(By.XPATH, '...').text  # Find appropriate element for hours

        get_url = driver.current_url

        # Close the browser after scraping
        driver.quit()

        # Pre-fill the form with the scraped data
        form.cafe.data = name
        form.ocena.data = ocena
        form.ceny.data = cena
        form.location.data = get_url
        form.open.data = "8AM"  # Placeholder
        form.close.data = "6PM"  # Placeholder

    if form.validate_on_submit():
        with open("cafe-data.csv", "a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write only the form fields (excluding CSRF token and submit button)
            writer.writerow([form.cafe.data, form.location.data, form.ocena.data,
                             form.ceny.data, form.open.data, form.close.data,
                             form.coffee.data, form.wifi.data, form.power.data,
                             form.komm.data])
        return redirect(url_for('add_cafe'))

    return render_template('add.html', form=form, form_auto=form_auto)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        cafes = []
        for row in csv_data:
            cafes.append(row)
    return render_template('cafes.html', cafes=cafes)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)