from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

# Konfigurasi database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance/laporan.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Konfigurasi folder upload dan ekstensi yang diizinkan
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Pastikan ekstensi file valid

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS  # Menambahkan konfigurasi ALLOWED_EXTENSIONS

def allowed_file(filename):
    # Memeriksa apakah ekstensi file valid
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Inisialisasi database
db = SQLAlchemy(app)

# Model database untuk Proposal Keluar
class ProposalKeluar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    penerima = db.Column(db.String(100), nullable=False)  # Kolom penerima
    jumlah = db.Column(db.Integer, nullable=False)  # Kolom jumlah
    tanggal = db.Column(db.String(20), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    
# Model untuk Laporan Dana Masuk
class LaporanDanaMasuk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uraian = db.Column(db.String(200), nullable=False)
    bukti = db.Column(db.String(200), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.Date,nullable=False)
    
# Fungsi untuk mengecek apakah file yang diupload adalah gambar
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/laporan_dana_masuk', methods=['GET', 'POST'])
def laporan_dana_masuk():
    if request.method == 'POST':
        uraian = request.form['uraian']
        jumlah = request.form['jumlah']
        tanggal = request.form['tanggal']
        
        tanggal = datetime.strptime(tanggal, '%Y-%m-%d').date()

        # Mengelola upload file bukti
        if 'bukti' not in request.files:
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(request.url)
        file = request.files['bukti']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            bukti_path = filename
        else:
            flash('File tidak valid', 'danger')
            return redirect(request.url)

        # Menambahkan data laporan ke database
        laporan = LaporanDanaMasuk(uraian=uraian, bukti=bukti_path, jumlah=jumlah, tanggal=tanggal)
        try:
            db.session.add(laporan)
            db.session.commit()
            flash('Laporan berhasil ditambahkan!', 'success')
            return redirect(url_for('laporan_dana_masuk'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    laporan_dana_masuk = LaporanDanaMasuk.query.all()
    proposals = ProposalKeluar.query.all()  # Ambil semua proposal keluar untuk dropdown
    return render_template('dana_masuk.html', laporan_dana_masuk=laporan_dana_masuk, proposals=proposals)


    
# Membuat folder 'instance' jika belum ada
if not os.path.exists('instance'):
    os.makedirs('instance')

# Route untuk halaman utama
@app.route('/')
def home():
    return render_template('home.html')

# Route untuk Proposal Keluar
@app.route('/proposal_keluar', methods=['GET', 'POST'])
def proposal_keluar():
    if request.method == 'POST':
        nama = request.form['nama']
        penerima = request.form['penerima']  # Ambil data penerima
        jumlah = request.form['jumlah']  # Ambil data jumlah
        tanggal = request.form['tanggal']
        deskripsi = request.form['deskripsi']
        new_proposal = ProposalKeluar(nama=nama, penerima=penerima, jumlah=jumlah, tanggal=tanggal, deskripsi=deskripsi)
        try:
            db.session.add(new_proposal)
            db.session.commit()
            flash('Proposal berhasil ditambahkan!', 'success')
            return redirect(url_for('proposal_keluar'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    proposals = ProposalKeluar.query.all()
    return render_template('proposal_keluar.html', proposals=proposals)

# Membuat tabel database jika belum ada
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
