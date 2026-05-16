from app import create_app, db
from app.models import User, Plot

app = create_app()
with app.app_context():
    users = User.query.all()
    for user in users:
        # Delete old plots
        Plot.query.filter_by(user_id=user.id).delete()
        
        # Create 5x5 grid
        plots = []
        for x in range(5):
            for y in range(5):
                # Merkezdeki 4 kare (2,2), (2,3), (3,2), (3,3)
                is_owned = False
                if x in [2, 3] and y in [2, 3]:
                    is_owned = True
                    
                p = Plot(user_id=user.id, x_coord=x, y_coord=y, is_owned=is_owned)
                plots.append(p)
                
        db.session.add_all(plots)
        db.session.commit()
        print(f"User {user.username} (ID: {user.id}) arazileri 5x5 sisteme taşındı.")
