from app import create_app, db
from app.models import Crop

app = create_app()
with app.app_context():
    # Check if exists
    kakao = Crop.query.filter_by(name='Altın Kakao').first()
    if not kakao:
        c4 = Crop(name='Altın Kakao', grow_time=600, seed_cost=5000, harvest_value=15000, unlock_level=20)
        db.session.add(c4)
        db.session.commit()
        print("Altın Kakao eklendi!")
    else:
        print("Altın Kakao zaten var.")
