from app import create_app, db
from app.models import Crop, Recipe

app = create_app()
with app.app_context():
    # Check if exists
    ciko = Crop.query.filter_by(name='Kraliyet Çikolatası').first()
    if not ciko:
        c5 = Crop(name='Kraliyet Çikolatası', grow_time=0, seed_cost=0, harvest_value=50000, unlock_level=25)
        db.session.add(c5)
        db.session.commit()
        print("Kraliyet Çikolatası eklendi!")
    else:
        c5 = ciko

    kakao = Crop.query.filter_by(name='Altın Kakao').first()
    if kakao:
        r_ciko = Recipe.query.filter_by(name='Kraliyet Çikolatası Üretimi').first()
        if not r_ciko:
            r4 = Recipe(name='Kraliyet Çikolatası Üretimi', result_item_id=c5.id, ingredient_item_id=kakao.id, req_amount=3, craft_time=1800, unlock_level=25, required_machine_type='royal')
            db.session.add(r4)
            db.session.commit()
            print("Kraliyet Çikolatası Tarifi eklendi!")
        else:
            print("Tarif zaten var.")
