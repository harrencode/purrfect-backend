from .service import create_notification_if_not_exists
from src.entities.lost_found import LostFoundReport
from src.entities.rescue_rep import RescueReport
from geopy.distance import geodesic


def generate_nearby_notifications(db, current_user, lat: float, lon: float):
    
    user_id = getattr(current_user, "id", None) or getattr(current_user, "user_id", None)
    if callable(user_id):
        user_id = user_id()

    if not user_id:
        print("[Notifications] Could not determine user_id")
        return

    print(f"[Notifications] Checking for nearby reports for user {user_id}")

    # Load all Lost/Found and Rescue reports 
    lost_reports = (
        db.query(LostFoundReport)
        .filter(LostFoundReport.user_id != user_id)
        .all()
    )
    rescue_reports = (
        db.query(RescueReport)
        .filter(RescueReport.user_id != user_id)
        .all()
    )

    # Create notifications for lost/found reports within 10 km
    for r in lost_reports:
        if not r.latitude or not r.longitude:
            continue

        distance = geodesic((lat, lon), (r.latitude, r.longitude)).km
        if distance <= 10:
            message = f"Nearby lost pet: {r.pet_name or 'Unknown pet'} at {r.location}"
            create_notification_if_not_exists(
                db=db,
                user_id=user_id,
                message=message,
                chat_id=r.chat_id,
                report_id=r.report_id,
                notif_type="lostpet",
            )

    # Create notifications for rescue reports within 10 km
    for r in rescue_reports:
        if not r.latitude or not r.longitude:
            continue

        distance = geodesic((lat, lon), (r.latitude, r.longitude)).km
        if distance <= 10:
            # enum value (e.g. "Critical", "High", "Medium", "Low")
            alert_label = r.alert_type.value

            message = (
                f"Rescue alert nearby ({alert_label}) - "
                f"{r.description or 'No description'}"
            )

            create_notification_if_not_exists(
                db=db,
                user_id=user_id,
                message=message,
                chat_id=r.chat_id,
                report_id=r.report_id,
                notif_type="rescue",
            )

    print(f"[Notifications] Nearby check complete for user {user_id}")
