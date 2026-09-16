from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.login_view,
        name="login"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "staff-dashboard/",
        views.staff_dashboard,
        name="staff_dashboard"
    ),

    path(
        "waste/",
        views.waste_dashboard,
        name="waste_dashboard"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "foods/",
        views.food_list,
        name="food_list"
    ),

    path(
        "foods/add/",
        views.add_food,
        name="add_food"
    ),

    path(
        "foods/<int:food_id>/edit/",
        views.edit_food,
        name="edit_food"
    ),

    path(
        "foods/<int:food_id>/delete/",
        views.delete_food,
        name="delete_food"
    ),

    path(
        "production/",
        views.production_list,
        name="production_list"
    ),

    path(
        "production/add/",
        views.add_production,
        name="add_production"
    ),

    path(
        "surplus/",
        views.surplus_list,
        name="surplus_list"
    ),

    path(
        "surplus/add/",
        views.add_surplus,
        name="add_surplus"
    ),

    path(
        "surplus/<int:surplus_id>/status/",
        views.update_surplus_status,
        name="update_surplus_status"
    ),

    path(
        "donations/",
        views.donation_list,
        name="donation_list"
    ),

    path(
        "donations/add/",
        views.add_donation,
        name="add_donation"
    ),
    path(
        "reports/",
        views.reports_dashboard,
        name="reports_dashboard"
    ),
    path(
        "demand-prediction/",
        views.demand_prediction,
        name="demand_prediction"
    ),

    path(
        "preparation-planner/",
        views.preparation_planner,
        name="preparation_planner"
    ),

    path(
        "preparation-planner/review/",
        views.review_preparation_plan,
        name="review_preparation_plan"
    ),

]