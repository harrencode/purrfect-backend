from fastapi import FastAPI
# from src.todos.controller import router as todos_router
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.pets.controller import router as pets_router
from src.adoption_reqs.controller import router as adoption_reqs_router
from src.rescue_rep.controller import router as rescue_rep_router
from src.notification.controller import router as notifications_router
from src.product.controller import router as store_router
from src.recommender.controller import router as recommender_router
from src.lost_found.controller import router as lost_found_router
from src.stray_map.controller import router as stray_map_router
from src.leaderboard.controller import router as leaderboard_router
from src.cart.controller import router as cart_router
from src.stats import router as stats_router

from src.chat.controller import router as chat_router

def register_routes(app: FastAPI):
    # app.include_router(todos_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(pets_router)
    app.include_router(adoption_reqs_router)
    app.include_router(rescue_rep_router)
    app.include_router(notifications_router)
    app.include_router(store_router)
    app.include_router(recommender_router)
    app.include_router(lost_found_router)
    app.include_router(stray_map_router)
    app.include_router(chat_router) 
    app.include_router(leaderboard_router)
    app.include_router(cart_router)
    app.include_router(stats_router)