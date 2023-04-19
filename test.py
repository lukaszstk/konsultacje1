from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///firma.db'
db = SQLAlchemy(app)

class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Float, nullable=False)

    def __init__(self, saldo):
        self.saldo = saldo

class Historia(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    operacja = db.Column(db.String(50), nullable=False)
    nazwa = db.Column(db.String(50), nullable=False)
    sztuk = db.Column(db.Integer, nullable=False)
    cena = db.Column(db.Float, nullable=False)

class Przedmiot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(50), nullable=False)
    sztuk = db.Column(db.Integer, nullable=False)

alembic = Alembic()
alembic.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def welcome():
    last_saldo = None
    if request.method == "POST":
        typ_forma = request.form.get('typ_forma')
        if typ_forma == 'saldo':
            newsaldo = float(request.form.get('newsaldo'))
            saldo = newsaldo
            sld = Saldo(saldo)
            db.session.add(sld)
            db.session.commit()

            # # historia zapis
            # historia_obj = Historia(operacja='saldo', nazwa=None, sztuk=None, cena=newsaldo)
            # db.session.add(historia_obj)
            # db.session.commit()
        elif typ_forma == 'kupno':
            przedmiot = request.form.get('nazwa')
            sztuk = int(request.form.get('sztuk'))
            cena = float(request.form.get('cena'))
            # aktualizacja salda
            last_saldo_obj = Saldo.query.order_by(Saldo.id.desc()).first()
            if last_saldo_obj:
                last_saldo = last_saldo_obj.saldo
                saldo = last_saldo - sztuk * cena
                sld = Saldo(saldo)
                db.session.add(sld)
                db.session.commit()

            # aktualizacja przedmiotow

            przedmiot_obj = Przedmiot.query.filter_by(nazwa=przedmiot).first()
            if przedmiot_obj:
                przedmiot_obj.sztuk += sztuk
            else:
                przedmiot_obj = Przedmiot(nazwa=przedmiot, sztuk=sztuk)
                db.session.add(przedmiot_obj)
            db.session.commit()

            # historia zapis
            historia_obj = Historia(operacja='kupno', nazwa=przedmiot, sztuk=sztuk, cena=cena)
            db.session.add(historia_obj)
            db.session.commit()

        elif typ_forma == 'sprzedaz':
            przedmiot = request.form.get('nazwa')
            sztuk = int(request.form.get('sztuk'))
            cena = float(request.form.get('cena'))

            # pobranie ostatniego salda
            last_saldo_obj = Saldo.query.order_by(Saldo.id.desc()).first()
            if last_saldo_obj:
                last_saldo = last_saldo_obj.saldo
                saldo = last_saldo + sztuk * cena  # aktualizacja salda

                # aktualizacja przedmiotow
                przedmiot_obj = Przedmiot.query.filter_by(nazwa=przedmiot).first()
                if przedmiot_obj and przedmiot_obj.sztuk >= sztuk:
                    przedmiot_obj.sztuk -= sztuk
                else:
                    return "Niepoprawna sprzedaz"

                # zapisanie operacji w historii
                historia_obj = Historia(operacja='sprzedaz', nazwa=przedmiot, sztuk=sztuk, cena=cena)
                db.session.add(historia_obj)

                # zapisanie aktualnego salda
                sld = Saldo(saldo)
                db.session.add(sld)
                db.session.commit()

            else:
                return "Nie można sprzedać przedmiotu, gdy saldo wynosi zero"

    # pobranie ostatniego salda
    last_saldo_obj = Saldo.query.order_by(Saldo.id.desc()).first()
    if last_saldo_obj:
        last_saldo = last_saldo_obj.saldo
    return render_template('index.html', last_saldo=last_saldo)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)