from app import create_app, db
from app.models import Crop, Recipe

app = create_app()
with app.app_context():
    # Güncelle Crop
    bugday = Crop.query.filter_by(name='Buğday').first()
    if bugday:
        bugday.unlock_level = 1
        
    domates = Crop.query.filter_by(name='Domates').first()
    if domates:
        domates.unlock_level = 2
        
    cilek = Crop.query.filter_by(name='Çilek').first()
    if cilek:
        cilek.unlock_level = 5

    # Güncelle Recipe
    salca_r = Recipe.query.filter_by(name='Salça Üretimi').first()
    if salca_r:
        salca_r.unlock_level = 2
        
    recel_r = Recipe.query.filter_by(name='Çilek Reçeli').first()
    if recel_r:
        recel_r.unlock_level = 5

    db.session.commit()
    print("Veritabanindaki urun seviyeleri güncellendi!")
