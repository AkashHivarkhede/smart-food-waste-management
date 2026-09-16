from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date , timedelta , datetime
from django.utils import timezone
from django.db import transaction
# from .ml.predictor import predict_demand
try:
    from .ml.predictor import predict_demand
except ImportError:
    predict_demand = None
from django.core.paginator import Paginator

from .models import (
    FoodItem,
    ProductionRecord,
    WasteRecord,
    SurplusFood,
    Donation
)

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)


from django.db.models import (
    Sum,
)

from django.db.models.functions import Coalesce

from .forms import (
    FoodItemForm,
    ProductionRecordForm
)


# =========================================================
# AUTHENTICATION
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "waste_management/login.html"
    )




@login_required
def dashboard(request):

    # -----------------------------------------
    # ADMIN
    # -----------------------------------------

    if request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect(
            "admin_dashboard"
        )


    # -----------------------------------------
    # STAFF
    # -----------------------------------------

    if request.user.groups.filter(
        name="Staff"
    ).exists():

        return redirect(
            "staff_dashboard"
        )


    # -----------------------------------------
    # INVALID ROLE
    # -----------------------------------------

    logout(request)

    messages.error(
        request,
        "Your account does not have a valid role."
    )

    return redirect("login")




@login_required
def admin_dashboard(request):

    # -----------------------------------------
    # ADMIN ROLE CHECK
    # -----------------------------------------

    if not request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect("dashboard")


    # -----------------------------------------
    # FOOD ITEMS
    # -----------------------------------------

    total_food_items = FoodItem.objects.count()


    # -----------------------------------------
    # PRODUCTION STATISTICS
    # -----------------------------------------

    prepared_result = ProductionRecord.objects.aggregate(
        total=Sum("prepared_quantity")
    )

    total_prepared = prepared_result["total"] or 0


    sold_result = ProductionRecord.objects.aggregate(
        total=Sum("sold_quantity")
    )

    total_sold = sold_result["total"] or 0


    # -----------------------------------------
    # WASTE STATISTICS
    # -----------------------------------------

    waste_result = WasteRecord.objects.aggregate(
        total=Sum("wasted_quantity")
    )

    total_waste = waste_result["total"] or 0


    cost_result = WasteRecord.objects.aggregate(
        total=Sum("waste_cost")
    )

    total_waste_cost = cost_result["total"] or 0


    # -----------------------------------------
    # WASTE PERCENTAGE
    # -----------------------------------------

    if total_prepared > 0:

        waste_percentage = (
            float(total_waste)
            / float(total_prepared)
        ) * 100

    else:

        waste_percentage = 0


    # -----------------------------------------
    # MOST WASTED FOOD
    # -----------------------------------------

    most_wasted_food = (
        WasteRecord.objects

        .values(
            "production_record__food__food_name"
        )

        .annotate(
            total_waste=Sum(
                "wasted_quantity"
            )
        )

        .order_by(
            "-total_waste"
        )

        .first()
    )


    # -----------------------------------------
    # AVAILABLE SURPLUS
    # -----------------------------------------

    surplus_result = (
        SurplusFood.objects
        .filter(status="Available")
        .aggregate(
            total=Sum("quantity")
        )
    )

    available_surplus = (
        surplus_result["total"] or 0
    )


    # -----------------------------------------
    # TOTAL DONATED
    # -----------------------------------------

    donation_result = Donation.objects.aggregate(
        total=Sum("quantity")
    )

    total_donated = donation_result["total"] or 0


    # -----------------------------------------
    # RECENT PRODUCTION
    # -----------------------------------------

    recent_production = (
        ProductionRecord.objects

        .select_related(
            "food",
            "recorded_by"
        )

        .order_by(
            "-record_date",
            "-created_at"
        )[:5]
    )


    # -----------------------------------------
    # RECENT WASTE
    # -----------------------------------------

    recent_waste = (
        WasteRecord.objects

        .select_related(
            "production_record__food"
        )

        .order_by(
            "-created_at"
        )[:5]
    )


    # -----------------------------------------
    # DASHBOARD CONTEXT
    # -----------------------------------------

    context = {

        "total_food_items":
            total_food_items,

        "total_prepared":
            total_prepared,

        "total_sold":
            total_sold,

        "total_waste":
            total_waste,

        "total_waste_cost":
            total_waste_cost,

        "waste_percentage":
            round(
                waste_percentage,
                2
            ),

        "most_wasted_food":
            most_wasted_food,

        "available_surplus":
            available_surplus,

        "total_donated":
            total_donated,

        "recent_production":
            recent_production,

        "recent_waste":
            recent_waste,

    }


    # -----------------------------------------
    # RENDER ADMIN DASHBOARD
    # -----------------------------------------

    return render(
        request,
        "waste_management/admin_dashboard.html",
        context
    )



@login_required
def staff_dashboard(request):

    # -----------------------------------------
    # STAFF ROLE CHECK
    # -----------------------------------------

    if not request.user.groups.filter(
        name="Staff"
    ).exists():

        return redirect("dashboard")


    # -----------------------------------------
    # TODAY'S DATE
    # -----------------------------------------

    today = timezone.localdate()


    # -----------------------------------------
    # FOOD ITEMS
    # -----------------------------------------

    total_food_items = FoodItem.objects.filter(
        is_available=True
    ).count()


    # -----------------------------------------
    # TODAY'S PRODUCTION
    # -----------------------------------------

    today_production = ProductionRecord.objects.filter(
        record_date=today
    )


    today_prepared = (
        today_production.aggregate(
            total=Sum("prepared_quantity")
        )["total"] or 0
    )


    today_sold = (
        today_production.aggregate(
            total=Sum("sold_quantity")
        )["total"] or 0
    )


    today_remaining = (
        today_production.aggregate(
            total=Sum("remaining_quantity")
        )["total"] or 0
    )


    today_waste = (
        today_production.aggregate(
            total=Sum("wasted_quantity")
        )["total"] or 0
    )


    # -----------------------------------------
    # TODAY'S WASTE RATE
    # -----------------------------------------

    if today_prepared > 0:

        today_waste_percentage = (
            float(today_waste)
            / float(today_prepared)
        ) * 100

    else:

        today_waste_percentage = 0


    # -----------------------------------------
    # AVAILABLE SURPLUS
    # -----------------------------------------

    available_surplus = (
        SurplusFood.objects
        .filter(status="Available")
        .aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )


    # -----------------------------------------
    # RECENT PRODUCTION
    # -----------------------------------------

    recent_production = (
        ProductionRecord.objects
        .filter(
            record_date=today
        )
        .select_related("food")
        .order_by(
            "-created_at"
        )[:5]
    )


    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "today":
            today,

        "total_food_items":
            total_food_items,

        "today_prepared":
            today_prepared,

        "today_sold":
            today_sold,

        "today_remaining":
            today_remaining,

        "today_waste":
            today_waste,

        "today_waste_percentage":
            round(
                today_waste_percentage,
                2
            ),

        "available_surplus":
            available_surplus,

        "recent_production":
            recent_production,

    }


    return render(
        request,
        "waste_management/staff_dashboard.html",
        context
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =========================================================
# FOOD MANAGEMENT
# =========================================================

@login_required
def food_list(request):

    if not request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect("dashboard")

    search = request.GET.get(
        "search",
        ""
    )

    foods = FoodItem.objects.all().order_by(
        "-created_at"
    )

    if search:

        foods = foods.filter(
            food_name__icontains=search
        )

    return render(
        request,
        "waste_management/food_list.html",
        {
            "foods": foods,
            "search": search
        }
    )


@login_required
def add_food(request):

    if not request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect("dashboard")

    if request.method == "POST":

        form = FoodItemForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Food item added successfully."
            )

            return redirect("food_list")

    else:

        form = FoodItemForm()

    return render(
        request,
        "waste_management/food_form.html",
        {
            "form": form,
            "title": "Add Food"
        }
    )


@login_required
def edit_food(request, food_id):

    if not request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect("dashboard")

    food = get_object_or_404(
        FoodItem,
        id=food_id
    )

    if request.method == "POST":

        form = FoodItemForm(
            request.POST,
            instance=food
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Food item updated successfully."
            )

            return redirect("food_list")

    else:

        form = FoodItemForm(
            instance=food
        )

    return render(
        request,
        "waste_management/food_form.html",
        {
            "form": form,
            "title": "Edit Food"
        }
    )


@login_required
def delete_food(request, food_id):

    if not request.user.groups.filter(
        name="Admin"
    ).exists():

        return redirect("dashboard")

    food = get_object_or_404(
        FoodItem,
        id=food_id
    )

    if request.method == "POST":

        food.delete()

        messages.success(
            request,
            "Food item deleted successfully."
        )

        return redirect("food_list")

    return render(
        request,
        "waste_management/food_confirm_delete.html",
        {
            "food": food
        }
    )


# =========================================================
# PRODUCTION MANAGEMENT
# =========================================================

@login_required
def production_list(request):

    # -----------------------------------------
    # ROLE CHECK
    # -----------------------------------------

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()

        or

        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):

        return redirect("dashboard")


    # -----------------------------------------
    # DATE FILTER
    # -----------------------------------------

    today = date.today()

    filter_type = request.GET.get(
        "filter",
        "all"
    )

    start_date = None
    end_date = None


    # -----------------------------------------
    # TODAY
    # -----------------------------------------

    if filter_type == "today":

        start_date = today
        end_date = today


    # -----------------------------------------
    # THIS WEEK
    # -----------------------------------------

    elif filter_type == "week":

        start_date = (
            today
            - timedelta(
                days=today.weekday()
            )
        )

        end_date = today


    # -----------------------------------------
    # THIS MONTH
    # -----------------------------------------

    elif filter_type == "month":

        start_date = today.replace(
            day=1
        )

        end_date = today


    # -----------------------------------------
    # CUSTOM RANGE
    # -----------------------------------------

    elif filter_type == "custom":

        start_date_value = request.GET.get(
            "start_date"
        )

        end_date_value = request.GET.get(
            "end_date"
        )

        try:

            if start_date_value:
                start_date = date.fromisoformat(
                    start_date_value
                )

            if end_date_value:
                end_date = date.fromisoformat(
                    end_date_value
                )

        except ValueError:

            start_date = None
            end_date = None


    # -----------------------------------------
    # PRODUCTION RECORDS
    # -----------------------------------------

    records = (
        ProductionRecord.objects
        .select_related(
            "food",
            "recorded_by"
        )
        .order_by(
            "-record_date",
            "-created_at"
        )
    )


    # -----------------------------------------
    # APPLY DATE FILTER
    # -----------------------------------------

    if start_date and end_date:

        records = records.filter(
            record_date__range=(
                start_date,
                end_date
            )
        )

    elif start_date:

        records = records.filter(
            record_date__gte=start_date
        )

    elif end_date:

        records = records.filter(
            record_date__lte=end_date
        )


    # -----------------------------------------
    # PAGINATION
    # -----------------------------------------

    paginator = Paginator(
        records,
        20
    )

    page_number = request.GET.get(
        "page"
    )

    records_page = paginator.get_page(
        page_number
    )


    # -----------------------------------------
    # ELIDED PAGE RANGE
    # -----------------------------------------

    page_range = paginator.get_elided_page_range(
        number=records_page.number,
        on_each_side=2,
        on_ends=2
    )


    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "records": records_page,

        "filter_type": filter_type,

        "start_date": start_date,

        "end_date": end_date,

        "page_range": page_range,

    }


    return render(
        request,
        "waste_management/production_list.html",
        context
    )

# # =========================================================
# # PRODUCTION MANAGEMENT
# # =========================================================

# @login_required
# def production_list(request):

#     if not (
#         request.user.groups.filter(
#             name="Admin"
#         ).exists()

#         or

#         request.user.groups.filter(
#             name="Staff"
#         ).exists()
#     ):

#         return redirect("dashboard")

#     records = (
#         ProductionRecord.objects
#         .select_related(
#             "food",
#             "recorded_by"
#         )
#         .order_by(
#             "-record_date",
#             "-created_at"
#         )
#     )

#     return render(
#         request,
#         "waste_management/production_list.html",
#         {
#             "records": records
#         }
#     )

@login_required
def add_production(request):

    # -----------------------------------------
    # ADMIN + STAFF ACCESS
    # -----------------------------------------

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()
        or
        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):
        return redirect("dashboard")


    # -----------------------------------------
    # POST REQUEST
    # -----------------------------------------

    if request.method == "POST":

        form = ProductionRecordForm(
            request.POST
        )

        if form.is_valid():

            record = form.save(
                commit=False
            )


            # -----------------------------------------
            # QUANTITY VALIDATION
            # -----------------------------------------

            prepared = record.prepared_quantity
            sold = record.sold_quantity
            remaining = record.remaining_quantity


            if sold + remaining > prepared:

                form.add_error(
                    "sold_quantity",
                    "Sold quantity + remaining quantity "
                    "cannot exceed prepared quantity."
                )

            else:

                # -----------------------------------------
                # RECORDED BY
                # -----------------------------------------

                record.recorded_by = request.user


                # -----------------------------------------
                # CALCULATE WASTE
                # -----------------------------------------

                record.wasted_quantity = (
                    prepared
                    - sold
                    - remaining
                )


                record.save()


                # -----------------------------------------
                # CREATE WASTE RECORD
                # -----------------------------------------

                if record.wasted_quantity > 0:

                    waste_reason = (
                        form.cleaned_data.get(
                            "waste_reason"
                        )
                    )


                    if not waste_reason:

                        waste_reason = "Other"


                    waste_cost = (
                        record.wasted_quantity
                        * record.food.cost_per_unit
                    )


                    WasteRecord.objects.create(

                        production_record=record,

                        wasted_quantity=(
                            record.wasted_quantity
                        ),

                        waste_cost=waste_cost,

                        reason=waste_reason

                    )


                messages.success(
                    request,
                    "Production record added successfully."
                )


                return redirect(
                    "production_list"
                )


    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

    else:

        initial = {}


        # -----------------------------------------
        # ML RECOMMENDATION PARAMETERS
        # -----------------------------------------

        food_id = request.GET.get(
            "food"
        )

        prediction_date = request.GET.get(
            "date"
        )

        recommended = request.GET.get(
            "recommended"
        )


        # -----------------------------------------
        # FOOD
        # -----------------------------------------

        if food_id:

            try:

                initial["food"] = int(
                    food_id
                )

            except (TypeError, ValueError):

                pass


        # -----------------------------------------
        # DATE
        # -----------------------------------------

        if prediction_date:

            initial["record_date"] = (
                prediction_date
            )


        # -----------------------------------------
        # RECOMMENDED PREPARATION
        # -----------------------------------------

        if recommended:

            try:

                recommended_quantity = int(
                    recommended
                )

                if recommended_quantity > 0:

                    initial[
                        "prepared_quantity"
                    ] = recommended_quantity

            except (TypeError, ValueError):

                pass


        form = ProductionRecordForm(
            initial=initial
        )


    # -----------------------------------------
    # RENDER
    # -----------------------------------------

    return render(
        request,
        "waste_management/production_form.html",
        {
            "form": form,
            "title": "Record Daily Production"
        }
    )

# =========================================================
# WASTE ANALYTICS
# =========================================================

@login_required
def waste_dashboard(request):

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()

        or

        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):

        return redirect("dashboard")


    # -----------------------------------------------------
    # TOTAL PREPARED
    # -----------------------------------------------------

    prepared_result = ProductionRecord.objects.aggregate(
        total=Sum("prepared_quantity")
    )

    total_prepared = prepared_result["total"] or 0


    # -----------------------------------------------------
    # TOTAL SOLD
    # -----------------------------------------------------

    sold_result = ProductionRecord.objects.aggregate(
        total=Sum("sold_quantity")
    )

    total_sold = sold_result["total"] or 0


    # -----------------------------------------------------
    # TOTAL WASTE
    # -----------------------------------------------------

    waste_result = WasteRecord.objects.aggregate(
        total=Sum("wasted_quantity")
    )

    total_waste = waste_result["total"] or 0


    # -----------------------------------------------------
    # TOTAL WASTE COST
    # -----------------------------------------------------

    cost_result = WasteRecord.objects.aggregate(
        total=Sum("waste_cost")
    )

    total_waste_cost = cost_result["total"] or 0


    # -----------------------------------------------------
    # WASTE PERCENTAGE
    # -----------------------------------------------------

    if total_prepared > 0:

        waste_percentage = (
            float(total_waste)
            /
            float(total_prepared)
        ) * 100

    else:

        waste_percentage = 0


    # -----------------------------------------------------
    # MOST WASTED FOOD
    # -----------------------------------------------------

    most_wasted_food = (
        WasteRecord.objects

        .values(
            "production_record__food__food_name"
        )

        .annotate(
            total_waste=Sum(
                "wasted_quantity"
            )
        )

        .order_by(
            "-total_waste"
        )

        .first()
    )


    # -----------------------------------------------------
    # WASTE BY REASON
    # -----------------------------------------------------

    waste_by_reason = (
        WasteRecord.objects

        .values(
            "reason"
        )

        .annotate(
            total_waste=Sum(
                "wasted_quantity"
            )
        )

        .order_by(
            "-total_waste"
        )
    )


    # -----------------------------------------------------
    # RECENT WASTE
    # -----------------------------------------------------

    recent_waste = (
        WasteRecord.objects

        .select_related(
            "production_record__food"
        )

        .order_by(
            "-created_at"
        )[:10]
    )


    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "total_prepared":
            total_prepared,

        "total_sold":
            total_sold,

        "total_waste":
            total_waste,

        "total_waste_cost":
            total_waste_cost,

        "waste_percentage":
            round(
                waste_percentage,
                2
            ),

        "most_wasted_food":
            most_wasted_food,

        "waste_by_reason":
            waste_by_reason,

        "recent_waste":
            recent_waste,

    }


    return render(
        request,
        "waste_management/waste_dashboard.html",
        context
    )


@login_required
def surplus_list(request):

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()
        or
        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):
        return redirect("dashboard")

    surplus_foods = (
        SurplusFood.objects
        .select_related("food")
        .order_by(
            "-surplus_date",
            "-created_at"
        )
    )

    return render(
        request,
        "waste_management/surplus_list.html",
        {
            "surplus_foods": surplus_foods
        }
    )

@login_required
def add_surplus(request):

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()
        or
        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):
        return redirect("dashboard")

    foods = FoodItem.objects.filter(
        is_available=True
    )

    if request.method == "POST":

        food_id = request.POST.get("food")
        quantity = request.POST.get("quantity")
        surplus_date = request.POST.get(
            "surplus_date"
        )
        notes = request.POST.get("notes")

        food = get_object_or_404(
            FoodItem,
            id=food_id,
            is_available=True
        )

        try:

            quantity = int(quantity)

            if quantity <= 0:

                messages.error(
                    request,
                    "Quantity must be greater than zero."
                )

                return redirect(
                    "add_surplus"
                )

        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter a valid quantity."
            )

            return redirect(
                "add_surplus"
            )


        SurplusFood.objects.create(

            food=food,

            quantity=quantity,

            surplus_date=surplus_date,

            notes=notes

        )


        messages.success(
            request,
            "Surplus food added successfully."
        )

        return redirect(
            "surplus_list"
        )


    return render(
        request,
        "waste_management/surplus_form.html",
        {
            "foods": foods,
            "today": date.today()
        }
    )

@login_required
def update_surplus_status(
    request,
    surplus_id
):

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()
        or
        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):
        return redirect("dashboard")


    surplus = get_object_or_404(
        SurplusFood,
        id=surplus_id
    )


    if request.method == "POST":

        status = request.POST.get(
            "status"
        )


        valid_statuses = [
            "Available",
            "Donated",
            "Consumed",
            "Disposed"
        ]


        if status in valid_statuses:

            surplus.status = status

            surplus.save()

            messages.success(
                request,
                "Surplus status updated successfully."
            )


    return redirect(
        "surplus_list"
    )


@login_required
def donation_list(request):

    if not (
        request.user.groups.filter(
            name="Admin"
        ).exists()
        or
        request.user.groups.filter(
            name="Staff"
        ).exists()
    ):
        return redirect("dashboard")


    donations = (
        Donation.objects
        .select_related(
            "surplus_food__food"
        )
        .order_by(
            "-donation_date",
            "-created_at"
        )
    )


    return render(
        request,
        "waste_management/donation_list.html",
        {
            "donations": donations
        }
    )
@login_required
def add_donation(request):

    # -----------------------------------------
    # ADMIN + STAFF ACCESS
    # -----------------------------------------

    if not (
        request.user.groups.filter(name="Admin").exists()
        or
        request.user.groups.filter(name="Staff").exists()
    ):
        return redirect("dashboard")


    # -----------------------------------------
    # AVAILABLE SURPLUS
    # -----------------------------------------

    surplus_foods = (
        SurplusFood.objects
        .filter(status="Available")
        .select_related("food")
    )


    # -----------------------------------------
    # POST REQUEST
    # -----------------------------------------

    if request.method == "POST":

        surplus_id = request.POST.get(
            "surplus_food"
        )

        quantity = request.POST.get(
            "quantity"
        )

        recipient = request.POST.get(
            "recipient"
        )

        donation_date = request.POST.get(
            "donation_date"
        )

        notes = request.POST.get(
            "notes"
        )


        # -----------------------------------------
        # GET SURPLUS
        # -----------------------------------------

        surplus = get_object_or_404(
            SurplusFood,
            id=surplus_id,
            status="Available"
        )


        # -----------------------------------------
        # VALIDATE QUANTITY
        # -----------------------------------------

        try:

            quantity = int(quantity)

        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter a valid quantity."
            )

            return redirect(
                "add_donation"
            )


        if quantity <= 0:

            messages.error(
                request,
                "Donation quantity must be greater than zero."
            )

            return redirect(
                "add_donation"
            )


        if quantity > surplus.quantity:

            messages.error(
                request,
                "Donation quantity cannot exceed "
                "available surplus."
            )

            return redirect(
                "add_donation"
            )


        # -----------------------------------------
        # DATABASE TRANSACTION
        # -----------------------------------------

        with transaction.atomic():

            # Create donation
            Donation.objects.create(

                surplus_food=surplus,

                quantity=quantity,

                recipient=recipient,

                donation_date=donation_date,

                notes=notes

            )


            # Reduce available surplus
            surplus.quantity -= quantity


            # Update status
            if surplus.quantity == 0:

                surplus.status = "Donated"

            else:

                surplus.status = "Available"


            surplus.save(
                update_fields=[
                    "quantity",
                    "status"
                ]
            )


        # -----------------------------------------
        # SUCCESS
        # -----------------------------------------

        messages.success(
            request,
            "Donation recorded successfully."
        )


        return redirect(
            "donation_list"
        )


    # -----------------------------------------
    # FORM
    # -----------------------------------------

    return render(
        request,
        "waste_management/donation_form.html",
        {
            "surplus_foods": surplus_foods,
            "today": date.today()
        }
    )


@login_required
def reports_dashboard(request):

    # -----------------------------------------
    # ROLE CHECK
    # -----------------------------------------

    if not (
        request.user.groups.filter(name="Admin").exists()
        or
        request.user.groups.filter(name="Staff").exists()
    ):
        return redirect("dashboard")


    # -----------------------------------------
    # CURRENT DATE
    # -----------------------------------------

    today = timezone.localdate()


    # -----------------------------------------
    # DEFAULT FILTER
    # -----------------------------------------

    filter_type = request.GET.get(
        "filter",
        "today"
    )

    start_date = today
    end_date = today


    # -----------------------------------------
    # TODAY
    # -----------------------------------------

    if filter_type == "today":

        start_date = today
        end_date = today


    # -----------------------------------------
    # THIS WEEK
    # -----------------------------------------

    elif filter_type == "week":

        start_date = (
            today
            - timedelta(days=today.weekday())
        )

        end_date = today


    # -----------------------------------------
    # THIS MONTH
    # -----------------------------------------

    elif filter_type == "month":

        start_date = today.replace(
            day=1
        )

        end_date = today


    # -----------------------------------------
    # CUSTOM RANGE
    # -----------------------------------------

    elif filter_type == "custom":

        start_date_value = request.GET.get(
            "start_date"
        )

        end_date_value = request.GET.get(
            "end_date"
        )

        try:

            if start_date_value:
                start_date = date.fromisoformat(
                    start_date_value
                )

            if end_date_value:
                end_date = date.fromisoformat(
                    end_date_value
                )

        except ValueError:

            messages.error(
                request,
                "Invalid date format."
            )

            start_date = today
            end_date = today

        # Prevent reversed date range
        if start_date > end_date:

            messages.error(
                request,
                "Start date cannot be after end date."
            )

            start_date = today
            end_date = today


    # -----------------------------------------
    # PRODUCTION RECORDS
    # -----------------------------------------

    production_records = (
        ProductionRecord.objects
        .filter(
            record_date__range=(
                start_date,
                end_date
            )
        )
    )


    # -----------------------------------------
    # PRODUCTION TOTALS
    # -----------------------------------------

    total_prepared = (
        production_records
        .aggregate(
            total=Sum("prepared_quantity")
        )["total"]
        or 0
    )


    total_sold = (
        production_records
        .aggregate(
            total=Sum("sold_quantity")
        )["total"]
        or 0
    )


    total_waste = (
        production_records
        .aggregate(
            total=Sum("wasted_quantity")
        )["total"]
        or 0
    )


    # -----------------------------------------
    # WASTE RECORDS
    # -----------------------------------------

    waste_records = (
        WasteRecord.objects
        .filter(
            production_record__record_date__range=(
                start_date,
                end_date
            )
        )
        .select_related(
            "production_record__food"
        )
    )


    # -----------------------------------------
    # WASTE COST
    # -----------------------------------------

    total_waste_cost = (
        waste_records
        .aggregate(
            total=Sum("waste_cost")
        )["total"]
        or 0
    )


    # -----------------------------------------
    # WASTE PERCENTAGE
    # -----------------------------------------

    if total_prepared > 0:

        waste_percentage = round(
            (
                float(total_waste)
                / float(total_prepared)
            ) * 100,
            2
        )

    else:

        waste_percentage = 0


    # -----------------------------------------
    # MOST WASTED FOOD
    # -----------------------------------------

    most_wasted_food = (
        waste_records

        .values(
            "production_record__food__food_name"
        )

        .annotate(
            total_waste=Sum(
                "wasted_quantity"
            )
        )

        .order_by(
            "-total_waste"
        )

        .first()
    )


    # -----------------------------------------
    # WASTE BY REASON
    # -----------------------------------------

    waste_by_reason = (
        waste_records

        .values("reason")

        .annotate(
            total_waste=Sum(
                "wasted_quantity"
            )
        )

        .order_by(
            "-total_waste"
        )
    )


    # -----------------------------------------
    # RECENT WASTE
    # -----------------------------------------

    recent_waste = (
        waste_records

        .order_by(
            "-created_at"
        )[:10]
    )


    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "total_prepared":
            total_prepared,

        "total_sold":
            total_sold,

        "total_waste":
            total_waste,

        "total_waste_cost":
            total_waste_cost,

        "waste_percentage":
            waste_percentage,

        "most_wasted_food":
            most_wasted_food,

        "waste_by_reason":
            waste_by_reason,

        "recent_waste":
            recent_waste,

        "start_date":
            start_date,

        "end_date":
            end_date,

        "filter_type":
            filter_type,

    }


    return render(
        request,
        "waste_management/reports_dashboard.html",
        context
    )


@login_required
def demand_prediction(request):

    if predict_demand is None:
        messages.error(
            request,
            "Demand prediction is temporarily unavailable."
        )
        return redirect("dashboard")

    # -----------------------------------------
    # ROLE CHECK
    # -----------------------------------------

    if not (
        request.user.groups.filter(name="Admin").exists()
        or
        request.user.groups.filter(name="Staff").exists()
    ):
        return redirect("dashboard")

    # -----------------------------------------
    # FOOD ITEMS
    # -----------------------------------------

    foods = FoodItem.objects.filter(
        is_available=True
    ).order_by("food_name")

    prediction = None

    selected_food = None
    selected_date = None

    # -----------------------------------------
    # HANDLE FORM
    # -----------------------------------------

    if request.method == "POST":

        food_id = request.POST.get("food")
        target_date = request.POST.get("target_date")

        selected_date = target_date

        try:

            selected_food = FoodItem.objects.get(
                id=food_id,
                is_available=True
            )

            prediction = predict_demand(
                food_id=selected_food.id,
                target_date=target_date
            )

        except FoodItem.DoesNotExist:

            messages.error(
                request,
                "Selected food item was not found."
            )

        except ValueError as e:

            messages.error(
                request,
                str(e)
            )

        except Exception:

            messages.error(
                request,
                "Unable to generate prediction. "
                "Please try again."
            )

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "foods": foods,

        "prediction": prediction,

        "selected_food": selected_food,

        "selected_date": selected_date,

        "today": date.today(),

    }

    return render(
        request,
        "waste_management/demand_prediction.html",
        context
    )

@login_required
def preparation_planner(request):

    if predict_demand is None:
        messages.error(
            request,
            "Demand prediction is temporarily unavailable."
        )
        return redirect("dashboard")

    # -----------------------------------------
    # ROLE CHECK
    # -----------------------------------------

    if not (
        request.user.groups.filter(name="Admin").exists()
        or
        request.user.groups.filter(name="Staff").exists()
    ):
        return redirect("dashboard")

    # -----------------------------------------
    # DEFAULT DATE
    # -----------------------------------------

    target_date = date.today() + timedelta(days=1)

    # -----------------------------------------
    # SELECTED DATE
    # -----------------------------------------

    date_value = request.GET.get("date")

    if date_value:

        try:
            target_date = date.fromisoformat(date_value)

        except ValueError:
            target_date = date.today() + timedelta(days=1)

    # -----------------------------------------
    # AVAILABLE FOODS
    # -----------------------------------------

    foods = FoodItem.objects.filter(
        is_available=True
    ).order_by("food_name")

    predictions = []

    # -----------------------------------------
    # DAILY SUMMARY VALUES
    # -----------------------------------------

    total_expected_sales = 0
    total_recommended = 0
    total_safety_buffer = 0
    estimated_waste = 0

    # -----------------------------------------
    # PREDICT EVERY FOOD
    # -----------------------------------------

    for food in foods:

        try:

            prediction = predict_demand(
                food_id=food.id,
                target_date=target_date
            )

            prediction["food_name"] = food.food_name

            predictions.append(prediction)

            # ---------------------------------
            # SUMMARY CALCULATIONS
            # ---------------------------------

            predicted_sales = prediction.get(
                "predicted_sales",
                0
            )

            recommended_quantity = prediction.get(
                "recommended_quantity",
                0
            )

            safety_buffer = prediction.get(
                "safety_buffer",
                0
            )

            waste_rate = float(
                prediction.get(
                    "waste_rate",
                    0
                )
            )

            # ---------------------------------
            # ADD TOTALS
            # ---------------------------------

            total_expected_sales += predicted_sales

            total_recommended += recommended_quantity

            total_safety_buffer += safety_buffer

            # ---------------------------------
            # ESTIMATED WASTE
            # ---------------------------------

            food_estimated_waste = (
                recommended_quantity
                * waste_rate
                / 100
            )

            estimated_waste += food_estimated_waste

        except Exception:
            continue

    # -----------------------------------------
    # ROUND ESTIMATED WASTE
    # -----------------------------------------

    estimated_waste = round(
        estimated_waste
    )

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "predictions": predictions,

        "target_date": target_date,

        "today": date.today(),

        # Daily summary
        "total_expected_sales":
            total_expected_sales,

        "total_recommended":
            total_recommended,

        "total_safety_buffer":
            total_safety_buffer,

        "estimated_waste":
            estimated_waste,

    }

    return render(
        request,
        "waste_management/preparation_planner.html",
        context
    )


@login_required
def review_preparation_plan(request):

    # -----------------------------------------
    # ROLE CHECK
    # -----------------------------------------

    if not (
        request.user.groups.filter(name="Admin").exists()
        or
        request.user.groups.filter(name="Staff").exists()
    ):
        return redirect("dashboard")


    # -----------------------------------------
    # GET DATE
    # -----------------------------------------

    date_value = request.GET.get("date")

    if not date_value:
        target_date = date.today() + timedelta(days=1)

    else:

        try:
            target_date = date.fromisoformat(
                date_value
            )

        except ValueError:

            messages.error(
                request,
                "Invalid preparation date."
            )

            return redirect(
                "preparation_planner"
            )


    # -----------------------------------------
    # AVAILABLE FOODS
    # -----------------------------------------

    foods = FoodItem.objects.filter(
        is_available=True
    ).order_by("food_name")


    predictions = []


    # -----------------------------------------
    # GENERATE PLAN
    # -----------------------------------------

    total_expected_sales = 0
    total_recommended = 0
    total_safety_buffer = 0
    estimated_waste = 0


    for food in foods:

        try:

            prediction = predict_demand(
                food_id=food.id,
                target_date=target_date
            )

            prediction["food_name"] = food.food_name

            predictions.append(prediction)

            total_expected_sales += prediction.get(
                "predicted_sales",
                0
            )

            total_recommended += prediction.get(
                "recommended_quantity",
                0
            )

            total_safety_buffer += prediction.get(
                "safety_buffer",
                0
            )

            waste_rate = float(
                prediction.get(
                    "waste_rate",
                    0
                )
            )

            estimated_waste += (
                prediction.get(
                    "recommended_quantity",
                    0
                )
                * waste_rate
                / 100
            )

        except Exception:

            continue


    estimated_waste = round(
        estimated_waste
    )


    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {

        "predictions": predictions,

        "target_date": target_date,

        "today": date.today(),

        "total_expected_sales":
            total_expected_sales,

        "total_recommended":
            total_recommended,

        "total_safety_buffer":
            total_safety_buffer,

        "estimated_waste":
            estimated_waste,

    }


    return render(
        request,
        "waste_management/"
        "review_preparation_plan.html",
        context
    )