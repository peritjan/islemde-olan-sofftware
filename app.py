from flask import Flask, render_template, url_for, redirect, request, session, flash
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import psycopg2 as dbapi2
import os
import re


app = Flask(__name__)
app.secret_key = "super secret key"

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is not None:
    config = DATABASE_URL
else:
    config = """dbname='software4' user='postgres' password='1'"""




# parses html into a soup data structure to traverse html
# as if it were a json data type.

#page_soup.h1
#page_soup.body.span
 #grabs each element
#x = containers[0]
#x.a["href"]
#print(x)
#print(x.a["href"])
#print(x.a.span.text)


class Product(object):

    def __init__(self, attr, price, link, img, fav):
        self.attr = attr
        self.price = price
        self.link = link
        self.image = img
        self.fav = fav

Products = []
logged_in = False

@app.route("/",methods=["POST","GET"])
def index():
    if request.method == 'POST':
        searchtext = request.form['search']
        session['searchtext'] = searchtext
        if searchtext == '':
            return render_template("index.html")
        else:
            products = SearchParse(searchtext)
            if(logged_in):
                getWishList()
            return render_template("listele.html",products=products)
    return render_template("index.html")


@app.route("/selectingAttribute",methods=["POST","GET"])
def selectingAttribute():
    if request.method == "POST":
        brand = request.form['brand']
        print(brand)
    return render_template("selectingAttribute.html")

@app.route("/listele",methods=["POST","GET"])
def listele():
    if session['logged_in']:
        getWishList()
    return render_template("listele.html", products=Products)

@app.route("/listele2",methods=["POST","GET"])
def listele2():
    return render_template("listele2.html", products=Products)

@app.route("/listele3",methods=["POST","GET"])
def listele3():
    return render_template("listele3.html", products=Products)

@app.route("/listele1",methods=["POST","GET"])
def listele1():
    return render_template("listele.html", products=Products)

# REGISTER -------------

class RegisterForm(Form):
    name = StringField('', [validators.Length(min=1, max=50)])
    surname = StringField('', [validators.Length(min=1, max=50)])
    username = StringField('', [validators.Length(min=4, max=25)])
    email = StringField('', [validators.Length(min=4, max=50)])
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords dont match')
    ])
    confirm = PasswordField('')

@app.route("/register",methods=["POST","GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name=form.name.data
        surname=form.surname.data
        email=form.email.data
        username = form.username.data
        password = form.password.data



        connection = dbapi2.connect(config)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM users WHERE username = %s """,[username])
        if cursor.rowcount > 0:
            flash('Username already exist!','danger')
            return redirect(url_for("register"))
        else:
            cursor.execute("""SELECT * FROM users WHERE email = %s """, [email])
            if cursor.rowcount > 0:
                flash('E-mail already exist!', 'danger')
                cursor.close()
                return redirect(url_for("register"))
            else:
                cursor.execute("""INSERT INTO users(ad,soyad,email,username,password) VALUES(%s, %s, %s,%s, %s)""",
                               (name,surname,email,username,password))
                connection.commit()
                cursor.close()
                flash('You are registered.', 'success')
                return redirect(url_for("login"))

    return render_template("register.html", form=form)
# REGISTER FINAL ----------

@app.route("/profile",methods=["POST","GET"])
def profile():
    return render_template("profile.html")

@app.route("/updateprofile",methods=["POST","GET"])
def updateprofile():
    return render_template("updateprofile.html")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password_form = request.form['password']

        connection = dbapi2.connect(config)
        cursor = connection.cursor()
        exist = cursor.execute("""SELECT * FROM users WHERE username = %s""", [username])
        row_count = 0
        for row in cursor:
            row_count += 1
        exist = cursor.execute("""SELECT * FROM users WHERE username = %s""", [username])
        if row_count > 0:
            user = cursor.fetchone()
            userid = user[0]
            userisim = user[1]
            usersoyisim = user[2]
            useremail = user[3]
            username = user[4]
            password = user[5]
            if password == password_form:
                session['logged_in'] = True
                session['username'] = username
                session['userid'] = userid
                session['userisim'] = userisim
                session['usersoyisim'] = usersoyisim
                session['useremail'] = useremail

                global logged_in
                logged_in = True
                #
                return redirect(url_for("index"))
            else:
                flash('Username or Password is incorrect!','danger')
                return render_template("login.html")
            cursor.close()
        else:
            flash('Username or Password is incorrect!', 'danger')
            return render_template("login.html")

    return render_template("login.html")
# LOGIN FINAL

# LOGOUT
@app.route("/logout",methods=["POST","GET"])
def logout():
    session.clear()
    global logged_in
    logged_in = False
    return redirect(url_for("index"))
# LOGOUT FINAL













def SearchParse(searchtext):
    Products.clear()
    searchtext = (re.sub("[ ]", "+", searchtext))
    Teknosa(searchtext)
    Amazon(searchtext)
    N11(searchtext)
#    Hepsiburada(searchtext)
#    Vatan(searchtext)
#    Mediamarkt(searchtext)

    return Products



def getWishList():
    userid = session['userid']
    connection = dbapi2.connect(config)
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM wishlist WHERE userid = %s""", [userid])
    wishlist = cursor.fetchall()
    session['wishlist'] = wishlist
    connection.commit()
    cursor.close()
    y=len(Products)
    for i in range(0,y):
        link = Products[i].link
        for row in wishlist:
            if(row[4] == link):
                print(link)
                Products[i].fav = False




def Teknosa(searchtext):
    global Products
    my_url = "https://www.teknosa.com/arama?sort=price-asc&q=" + searchtext + "%3Arelevance%3Acategory%3A1020101&text=#"
    uClinet = uReq(my_url)
    page_html = uClinet.read()
    uClinet.close()
    # parse HTML
    page_soup = soup(page_html, "html.parser")
    container = page_soup.findAll("div", {"class": "product-text"})
    container_link = page_soup.findAll("div", {"class": "product-image-item"})

    x = len(container)
    print(x)
    for count in range(0, x):
        contain = container[count].find("div", {"class": "product-name"})
        attribute = contain.a.span.text

        contain = container[count].find("span", {"class": "price-tag new-price font-size-tertiary"})
        price = contain.text

        link = container_link[count].a["href"]
        link = "https://www.teknosa.com" + link
        photo = container_link[count].img["src"]
        fav = True
        Products.append(Product(attribute, price, link, photo, fav))


def Amazon(searchtext):
    global Products
    my_url = "https://www.amazon.com.tr/s?k="+searchtext+"&rh=n%3A12601898031&__mk_tr_TR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss"
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, "html.parser")

    container = page_soup.findAll("div", {"class": "sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"})

    lenght = len(container)
    print(lenght)
    for i in range(0, lenght - 2):
        contain = container[i].find("span", {"class": "rush-component"})
        link = "https://www.amazon.com.tr" + contain.a["href"]
        contain = container[i].find("div", {"class": "a-section aok-relative s-image-square-aspect"})
        img = contain.img["src"]
        contain = container[i].find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
        attr = contain
        price = container[i].find("span", {"class": "a-price-whole"})
        fav = True
        Products.append(Product(attr.text, price.text, link, img,fav))






def N11(searchtext):
    my_url = "https://www.n11.com/bilgisayar/dizustu-bilgisayar?q=" +searchtext+ "&srt=PRICE_LOW"


    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, "html.parser")

    container = page_soup.findAll("li", {"class": "column"})

    lenght = len(container)

    print(lenght)

    for i in range(0, lenght):
        contain = container[i].find("div", {"class": "pro"})
        link = contain.a["href"]
        contain = container[i].find("a", {"class": "plink"})
        #print(contain)
        img = contain.img["data-original"]
        attr = contain.img["alt"]
        print(img)
        contain = container[i].find("div", {"class": "proDetail"})
        price = contain.ins.text
        price = re.sub(r"\s+", '', price)
        fav = True
        Products.append(Product(attr, price, link, img, fav))


#def Itopya(searchtext):



#    page_url = "https://www.teknosa.com/arama?q=" + searchtext + "%3Arelevance%3Acategory%3A1020101&text=#"
    # opens the connection and downloads html page from url
 #   uClient = uReq(page_url)
  #  page_soup = soup(uClient.read(), "html.parser")
   # uClient.close()
    #containers = page_soup.findAll("div", {"class": "product-detail"})
    #return containers

@app.route("/contact",methods=["POST","GET"])
def cotact():
    return render_template("contact.html")

@app.route("/favorites",methods=["POST","GET"])
def favorites():
    getWishList()
    return render_template("favorites.html")

@app.route("/addfavorite/<int:i>",methods=["POST","GET"])
def addfavorite(i):
    if session['logged_in']:
        title = Products[i].attr
        link =  Products[i].link
        image = Products[i].image
        price = Products[i].price
        userid = session['userid']
        connection = dbapi2.connect(config)
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO wishlist(userid,urun_image,urun_title,urun_link,urun_price) VALUES(%s, %s, %s, %s, %s)""",
                       (userid, image, title, link, price))
        connection.commit()
        cursor.close()
        return redirect(url_for('listele'))
    else:
        return redirect(url_for("login"))
    return render_template("listele.html")

@app.route("/unFavorite/<int:i>",methods=["POST","GET"])
def unFavorite(i):
    link = Products[i].link
    if session['logged_in']:
        userid= session['userid']
        connection = dbapi2.connect(config)
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM wishlist WHERE userid = %s AND urun_link = %s """, (userid, link))
        connection.commit()
        cursor.close()
        Products[i].fav = True
        return redirect(url_for('listele'))
    return render_template("listele.html")





@app.route("/deleteFavorite/<string:favid>",methods=["POST","GET"])
def deleteFavorite(favid):
    connection = dbapi2.connect(config)
    cursor = connection.cursor()
    cursor.execute("""DELETE FROM wishlist WHERE wish_id = %s""", [favid])
    print(favid)
    connection.commit()
    cursor.close()
    return redirect(url_for("favorites"))

# LOGIN FINAL
# LOGIN FINAL


#
#@app.route("/ara", methods=["POST","GET"])
#def listele():
    # buraya girilen metnin arama kısmını yapıp html parse yapılacak
#    return render_template("listele.html")



#@app.route('/')
#def hello_world():
#    return x.a.span.text


if __name__ == '__main__':
    app.run()


