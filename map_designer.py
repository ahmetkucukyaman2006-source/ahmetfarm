from app import create_app, db
from app.models import User, Plot

app = create_app()
with app.app_context():
    users = User.query.all()
    
    # Asimetrik Harita Şablonu:
    # (x, y, w, h, is_owned)
    map_template = [
        (0, 0, 2, 2, False), # Sol üst devasa orman
        (2, 0, 3, 1, False), # Sağ üst uzun tarla
        (0, 2, 1, 3, False), # Sol alt nehir/sera
        (1, 2, 1, 1, False),
        (2, 1, 3, 1, False),
        (2, 2, 1, 1, True),  # Merkez başlangıç
        (3, 2, 1, 1, True),  # Merkez başlangıç
        (2, 3, 1, 1, True),  # Merkez başlangıç
        (3, 3, 1, 1, True),  # Merkez başlangıç
        (4, 2, 1, 2, False), # Sağ dikey tarla
        (1, 3, 1, 2, False), 
        (2, 4, 2, 1, False),
        (4, 4, 1, 1, False)
    ]

    for user in users:
        # Eski tarlaları sil
        Plot.query.filter_by(user_id=user.id).delete()
        
        plots = []
        for x, y, w, h, owned in map_template:
            p = Plot(user_id=user.id, x_coord=x, y_coord=y, width=w, height=h, is_owned=owned)
            plots.append(p)
            
        db.session.add_all(plots)
        db.session.commit()
        print(f"User {user.username} (ID: {user.id}) haritası asimetrik hale getirildi!")
